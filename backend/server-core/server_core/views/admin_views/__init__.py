import flask_admin
from flask_admin.menu import MenuLink
from .index_view_admin import AdminIndexView
from .asset_admin import AssetAdmin
from .asset_class_admin import AssetClassAdmin
from .asset_ref_admin import AssetRefAdmin
from .asset_version_admin import AssetVersionAdmin
from .object_admin import ObjectAdmin
from .content_admin import ContentAdmin
from .asset_class_content_rel_admin import AssetClassContentRelationsAdmin
from .asset_object_rel_admin import AssetObjectRelationsAdmin
from .auth_provider_admin import AuthProviderAdmin
from .project_admin import ProjectAdmin
from .user_admin import UserAdmin
from .role_admin import RoleAdmin
from .user_role_admin import UserRoleAdmin
from .asset_settings_admin import AssetSettingsAdmin
from .tags_admin import TagsAdmin
from .tag_refs_admin import TagRefsAdmin
from .tag_queries_admin import TagQueriesAdmin
from .app_secrets_admin import AppSecretsAdmin
from .bucket_admin import BucketAdmin
from .template_admin import TemplateAdmin
from .webhook_admin import WebhookAdmin
from .webhook_status_admin import WebhookStatusAdmin


def register_blueprints(app):
    app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
    admin = flask_admin.Admin(app=app,
                              name="asset server",
                              index_view=AdminIndexView(),
                              endpoint="admin",
                              template_mode='bootstrap2'
                              )
    admin.add_link(MenuLink(name='Logout', category='', url="/admin/logout/"))
    admin.add_view(AssetClassAdmin())
    admin.add_view(AssetAdmin())
    admin.add_view(AssetRefAdmin())
    admin.add_view(AssetVersionAdmin())
    admin.add_view(ObjectAdmin())
    admin.add_view(ContentAdmin())
    admin.add_view(AssetClassContentRelationsAdmin())
    admin.add_view(AssetObjectRelationsAdmin())
    admin.add_view(AuthProviderAdmin())
    admin.add_view(ProjectAdmin())
    admin.add_view(UserAdmin())
    admin.add_view(RoleAdmin())
    admin.add_view(UserRoleAdmin())
    admin.add_view(AssetSettingsAdmin())
    admin.add_view(TagsAdmin())
    admin.add_view(TagRefsAdmin())
    admin.add_view(TagQueriesAdmin())
    admin.add_view(AppSecretsAdmin())
    admin.add_view(BucketAdmin())
    admin.add_view(TemplateAdmin())
    admin.add_view(WebhookAdmin())
    admin.add_view(WebhookStatusAdmin())

