from .asset_view import asset_view
from .asset_class_view import asset_class_view
from .asset_commit_view import asset_commit_view
from .asset_version_view import asset_version_view
from .asset_ref_view import asset_ref_view
from .project_view import view as project_view
from .tag_view import view as tag_view
from .bucket_proxy_view import view as bucket_proxy_view


def register_blueprints(app):
    app.register_blueprint(asset_view, url_prefix="/asset")
    app.register_blueprint(asset_class_view, url_prefix="/asset_class")
    app.register_blueprint(asset_commit_view, url_prefix="/asset_commit")
    app.register_blueprint(asset_version_view, url_prefix="/asset_version")
    app.register_blueprint(asset_ref_view, url_prefix="/asset_ref")
    app.register_blueprint(project_view, url_prefix="/project")
    app.register_blueprint(tag_view, url_prefix="/tag")
    app.register_blueprint(bucket_proxy_view, url_prefix="/bucket_proxy")
