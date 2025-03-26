import logging

from flask import Blueprint, Response, request

from server_core.models.role import Role
from server_core.models.user import User
from server_core.models.user_role import UserRole
from server_core.utils import json_encoder
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

user_role_view = Blueprint(name='db_user_role_view', import_name=__name__)


@user_role_view.route('', methods=['GET'])
def list():
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    project_name = request.args.get('project_name')
    if project_name:
        result = list_by_project(project_name)
    else:
        result = [record.to_dict() for record in UserRole.select()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)


def list_by_project(project_name: str):
    """List all members (including admins) in project"""
    member_role: Role = Role.get_if_exists(Role.project_name == project_name, ~Role.can_admin_project)
    admin_role: Role = Role.get_if_exists(Role.project_name == project_name, Role.can_admin_project)

    if not member_role and not admin_role:
        raise Exception(f"Roles not found for project: {project_name}")

    result = []
    for role, access_level in [(member_role, "member"), (admin_role, "admin")]:
        if role:
            query = (UserRole
                     .select(UserRole.id,
                             UserRole.role_id,
                             User.username.alias('username'),
                             User.email.alias('email'),
                             UserRole.created_at)
                     .join(User)
                     .where(UserRole.role_id == role.id))

            result.extend([
                {
                    "id": record.id,
                    "role_id": record.role_id,
                    "username": record.asset_user.username,
                    "email": record.asset_user.email,
                    "access_level": access_level,
                    "created_at": record.created_at,
                }
                for record in query
            ])

    return result


@user_role_view.route('', methods=['POST'])
def create_user_role():
    """Create member user role using project_name and username"""
    data: dict = view_utils.data_from_request(request)
    created_by = data.get("created_by")
    project_name = data.get("project_name")
    if not created_by or not project_name:
        result = {"error": "required params missing: created_by or project_name"}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)

    # check if user has admin role
    if not is_admin_for_project(created_by, project_name):
        result = {
            "error": "Cannot add user because {} is not an admin for the {} project".format(created_by, project_name)}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
    try:
        asset_user = get_user_record(data.get("username"), data.get("email"))
        created: UserRole = get_or_create_user_role(
            project_name=project_name,
            asset_user=asset_user,
            username=created_by)
        result = created.to_dict()
        res_code = 201  # created
    except Exception as e:
        result = {"error": str(e)}
        res_code = 400
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


def is_admin_for_project(username: str, project_name: str):
    user = User.get(User.username == username)
    admin_role: Role = Role.get_if_exists(Role.project_name == project_name, Role.can_admin_project)
    if not admin_role:
        return False
    is_project_admin: UserRole = UserRole.get_if_exists(UserRole.role == admin_role.id,
                                                        UserRole.asset_user == user.id)
    return bool(is_project_admin)


def get_user_record(username: str, email: str):
    """Get the user record from database"""
    asset_user: User = User.get_if_exists(User.username == username,
                                          User.email == email,
                                          include_deleted_records=True)
    # if asset user doesn't exist, throw error
    if not asset_user:
        raise Exception("missing asser user record, cannot create user role for nonexistent user")
    # restore if soft deleted previously
    if asset_user.status == User.statuses.DELETED:
        asset_user.restore()
    return asset_user


def get_or_create_user_role(project_name, username, asset_user, is_admin=False):
    if is_admin:
        role: Role = Role.get_if_exists(Role.project_name == project_name, Role.can_admin_project)
    else:
        role: Role = Role.get_if_exists(Role.project_name == project_name, ~Role.can_admin_project)
    if not role:
        # create a new role
        role = Role.create_if_not_exists_for_project(project_name=project_name, username=username,
                                                     can_admin_project=is_admin)

    new_user_role: UserRole = UserRole.create_if_not_exists_for_role(
        role_id=role.id,
        user_id=asset_user.id,
        username=username)
    return new_user_role


@user_role_view.route('/<id>', methods=['PUT'])
def update_user_role(id: str):
    """Update user role using id"""
    data: dict = view_utils.data_from_request(request)
    updated_by, project_name = data.get("modified_by"), data.get("project_name")
    if not updated_by or not project_name:
        result = {"error": "required params missing: updated_by or project_name"}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)

    user_role: UserRole = UserRole.get_if_exists(UserRole.id == id)
    if not user_role:
        result = {"error": "User role not found with id: {}".format(id)}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)

    if not is_admin_for_project(updated_by, data.get("project_name")):
        result = {
            "error": "Cannot add user because {} is not an admin for the {} project".format(updated_by, project_name)}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
    try:
        # if access level is changed, then create a new role
        # todo: this might create a new role for the same user, if the user is already an admin
        # note no other updates are allowed to the user-role
        if "access_level" in data:
            is_admin = data.get("access_level") == "admin"
            if is_admin != user_role.role.can_admin_project:
                # update the user role
                role = Role.get_if_exists(Role.project_name == project_name, Role.can_admin_project == is_admin)
                if not role:
                    role = Role.create_if_not_exists_for_project(project_name=project_name, username=updated_by,
                                                                 can_admin_project=is_admin)
                user_role.role = role
                user_role.save(user=updated_by, only=[UserRole.role_id])
                result = {
                    "id": user_role.id,
                    "role_id": user_role.role_id,
                    "username": user_role.asset_user.username,
                    "email": user_role.asset_user.email,
                    "access_level": user_role.role.can_admin_project and "admin" or "member",
                    "created_at": user_role.created_at,
                }
                res_code = 200
    except Exception as e:
        result = {"error": str(e)}
        res_code = 400
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


@user_role_view.route('/<id>', methods=['DELETE'])
def delete_user_role(id: str):
    """Delete user role using id"""
    deleted_by = request.args.get('deleted_by')
    project_name = request.args.get('project_name')
    if not deleted_by or not project_name:
        result = {"error": "required params missing: deleted_by or project_name"}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)

    # check if user has admin role
    if not is_admin_for_project(deleted_by, project_name):
        result = {
            "error": "Cannot add user because {} is not an admin for the {} project".format(deleted_by, project_name)}
        res_code = 400
        return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)

    user_role: UserRole = UserRole.get_if_exists(UserRole.id == id)
    result = user_role.delete_instance(user=deleted_by, recursive=True, permanently=True)
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)
