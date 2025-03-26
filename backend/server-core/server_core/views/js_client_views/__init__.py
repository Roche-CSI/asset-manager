from .asset_class_view import asset_class_view
from .asset_objct_view import asset_object_view
from .asset_ref_view import asset_ref_view
from .asset_settings_view import view as asset_settings_view
from .asset_version_view import asset_version_view
from .asset_view import asset_view
from .bucket_view import view as bucket_view
from .content_view import content_view
from .elastic_view import view as elastic_view
from .issue_view import issue_view
from .project_view import project_view
from .signed_url_view import url_view
from .tags_view import tags_view
from .template_view import view as template_view
from .user_role_view import user_role_view
from .webhook_view import view as webhook_view


def register_blueprints(app):
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
