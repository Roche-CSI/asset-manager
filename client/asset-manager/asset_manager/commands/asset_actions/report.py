from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common import exceptions
from asset_utils.utils import LogColors


class AssetReport(CliAction):
    name = "report"
    help_msg = "generates a report for the asset"
    requires_repo = True

    def run(self, args):
        if args.name is None:
            self.user_log.message("missing report file name", color=LogColors.ERROR)
            return
        if args.template is None:
            self.user_log.message("missing html jinja template", color=LogColors.ERROR)
            return
        api = AssetAPI(repo=self.repo).report
        if not api:
            return
        try:
            with api.environment():
                api.generate_report(report=args.name, template=args.template)
        except exceptions.AssetException as e:
            self.user_log.message(e.msg, color=LogColors.ERROR)

    def get_options(self):
        return [
            CliOption(
                dest="name",
                help_msg="optional: the html file name of the report to be generated",
                short_name="n",
                full_name="name",
                is_boolean=False
            ),

            CliOption(
                dest="template",
                help_msg="optional: a jinja template to generate the report",
                short_name="t",
                full_name="template",
                is_boolean=False
            ),
        ]
