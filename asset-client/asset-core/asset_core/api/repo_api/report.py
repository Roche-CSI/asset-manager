import os

from jinja2 import Environment, FileSystemLoader

from asset_core.asset.refs import AssetRef
from asset_core.configs import AppSettings
from asset_utils.common import exceptions
from asset_utils.utils import kilo_byte
from asset_utils.utils.web_utils import open_in_browser
from .repo import RepoAPI

# template is located in asset-core/asset_core/api/repo_api/templates/
DEFAULT_TEMPLATE = "report_template.html"
DEFAULT_REPORT = "asset_report.html"


class ReportAPI(RepoAPI):

    def update_input_refs(self, asset_name: str, project_id: str):
        try:
            refs, _ = AssetRef.get_refs_from_remote(asset_name=asset_name, project_id=project_id)
            if refs.get("error"):
                # server sends back error, if asset is not found
                self.user_log.alert(refs.get("error"))
            elif refs.get("depends_on"):
                [ref.get_state() for ref in refs.get("depends_on")]
                self.asset.refs.add_refs(refs.get("depends_on"), save=False)
        except exceptions.AssetException:
            raise

    def render_html_report(self, report: str, template: str):
        # use default template if no template is provided
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        template_file = DEFAULT_TEMPLATE
        if template:
            template_dir, template_file = os.path.split(template)

        # set up the environment and filters
        env = Environment(loader=FileSystemLoader(template_dir))
        env.filters["kilo_byte"] = kilo_byte
        env.filters["enumerate"] = enumerate
        relpath = lambda x: os.path.relpath(x, self.asset.repo_dir)
        env.filters["relpath"] = relpath
        env.filters["project_info"] = AppSettings.shared().projects.get

        # render the jinja template
        jinja_template = env.get_template(template_file)
        output = jinja_template.render(asset=self.asset)

        # write the output to the report file
        os.makedirs(os.path.dirname(report), exist_ok=True)
        with open(report, "w") as html:
            html.write(output)

    def generate_report(self, report: str, template: str):
        # update the asset input refs from remote
        self.update_input_refs(asset_name=self.asset.version.name,
                               project_id=self.asset.asset_class.project)

        if not report:
            # if no report file name is provided, use the default report file name
            report = os.path.join(self.asset.repo_dir, DEFAULT_REPORT)

        # render html report
        self.render_html_report(report=report, template=template)
        self.user_log.success(f"Report generated at: {report}")
        self.user_log.success("Opening report in browser...")
        open_in_browser(report)
