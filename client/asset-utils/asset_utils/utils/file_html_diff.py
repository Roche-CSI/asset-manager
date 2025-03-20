import difflib
from pathlib import Path


class FileHtmlDiff(difflib.HtmlDiff):
    """
    source: https://blog.furas.pl/python-difflib-how-to-format-html-from-htmldiff-when-text-is-too-long-gb.html
    """

    def __init__(self, *args,
                 html_template: str,
                 css_file: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_template = Path(html_template).read_text()
        if css_file:
            self._styles = Path(css_file).read_text()
        self._legend = ""
        # self._legend = Path(os.path.dirname(__file__), "templates/diff_legend.html").read_text()

    def set_description(self, title: dict, subtitle: dict):
        self._file_template = self._file_template.replace("{{title_name}}", title.get("name"))
        self._file_template = self._file_template.replace("{{title_desc}}", title.get("val"))
        self._file_template = self._file_template.replace("{{subtitle_name}}", subtitle.get("name"))
        self._file_template = self._file_template.replace("{{subtitle_desc}}", subtitle.get("val"))
