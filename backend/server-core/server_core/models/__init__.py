from peewee import DoesNotExist
from .asset import Asset
from .asset_ref import AssetRef
from .version_counter import VersionCounter
from .asset_class import AssetClass
from .content import Content
from .asset_class_content_relations import AssetClassContentRelations
from .object import Object
from .asset_object_relations import AssetObjectRelations
from .asset_version import AssetVersion
from .asset_ref import AssetRef
from .auth_provider import AuthProvider
from .user import User
from .project import Project
from .role import Role
from .user_role import UserRole
from .asset_settings import AssetSettings
from .tags import Tags
from .tag_refs import TagRefs
from .tag_queries import TagQueries
from .app_secret import AppSecret
from .bucket import Bucket
from .template import Template
from .webhook import Webhook
from .webhook_status import WebhookStatus
from .project_bucket_relations import ProjectBucketRelations
from .template_entity_relations import TemplateEntityRelations
from flask import g


def create_tables(database=None):
    database = database or g.db
    with database:
        database.create_tables([AssetClass,
                                Asset,
                                VersionCounter,
                                AssetRef,
                                Content,
                                AssetClassContentRelations,
                                Object,
                                AssetObjectRelations,
                                AssetVersion,
                                AuthProvider,
                                Project,
                                User,
                                Role,
                                UserRole,
                                AssetSettings,
                                Tags,
                                TagRefs,
                                TagQueries,
                                AppSecret,
                                Bucket,
                                Template,
                                TemplateEntityRelations,
                                Webhook,
                                WebhookStatus,
                                ProjectBucketRelations
                                ])


def delete_tables(database=None):
    database = database or g.db
    with database:
        database.drop_tables([AssetObjectRelations,
                              Object,
                              AssetRef,
                              AssetClassContentRelations,
                              Content,
                              VersionCounter,
                              AssetClass,
                              Asset,
                              AssetVersion,
                              AuthProvider,
                              Project,
                              User,
                              Role,
                              UserRole,
                              AssetSettings,
                              Tags,
                              TagRefs,
                              TagQueries,
                              AppSecret,
                              Bucket,
                              Template,
                              Webhook,
                              WebhookStatus,
                              TemplateEntityRelations,
                              ProjectBucketRelations
                              ])
