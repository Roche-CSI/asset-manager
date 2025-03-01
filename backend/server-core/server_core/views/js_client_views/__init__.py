from .asset_view import asset_view
from .asset_class_view import asset_class_view
from .signed_url_view import url_view
from .asset_version_view import asset_version_view
from .asset_objct_view import asset_object_view
from .asset_ref_view import asset_ref_view
from .google_login import google_login_view, CLIENT_ID, CLIENT_SECRET
from .content_view import content_view
from .asset_settings_view import view as asset_settings_view
from .project_view import project_view
from .user_role_view import user_role_view
from .tags_view import tags_view
from .issue_view import issue_view
from .bucket_view import view as bucket_view
from .template_view import view as template_view
from .webhook_view import view as webhook_view
from .elastic_view import view as elastic_view

def register_blueprints(app):
    app.config["GOOGLE_OAUTH_CLIENT_ID"] = CLIENT_ID
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = CLIENT_SECRET

    app.register_blueprint(asset_view, url_prefix="/db/asset")
    app.register_blueprint(asset_version_view, url_prefix="/db/asset_version")
    app.register_blueprint(asset_class_view, url_prefix="/db/asset_class")
    app.register_blueprint(url_view, url_prefix="/db/file_url")
    app.register_blueprint(asset_ref_view, url_prefix="/db/asset_ref")
    app.register_blueprint(asset_object_view, url_prefix="/db/asset_object")
    app.register_blueprint(content_view, url_prefix="/db/content")
    app.register_blueprint(asset_settings_view, url_prefix="/db/asset_settings")
    app.register_blueprint(project_view, url_prefix="/db/project")
    app.register_blueprint(user_role_view, url_prefix="/db/user_role")
    app.register_blueprint(tags_view, url_prefix="/db/tags")
    app.register_blueprint(issue_view, url_prefix="/issues")
    app.register_blueprint(bucket_view, url_prefix="/db/bucket")
    app.register_blueprint(template_view, url_prefix="/db/template")
    app.register_blueprint(webhook_view, url_prefix="/db/webhook")
    app.register_blueprint(elastic_view, url_prefix="/db/elastic")
    # app.register_blueprint(google_login_view, url_prefix="/db/google_login")


    # app.register_blueprint(asset_commit_view, url_prefix="/asset_commit")
    # app.register_blueprint(asset_version_view, url_prefix="/asset_version")
    # app.register_blueprint(asset_ref_view, url_prefix="/asset_ref")


