from flask import Blueprint
import logging

logger = logging.getLogger(__file__)
asset_view = Blueprint(name='db_login', import_name=__name__)

CLIENT_ID = ""

