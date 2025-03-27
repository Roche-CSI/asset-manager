import abc
from .base_action import BaseAction


class CliAction(BaseAction):
    """
    To create an action instance.
    Parameters:
        name: action name, mime_type str.
        desc_help: description for the action. Type str.
        options: list of options/arguments chosen from the keys of options_mapping. Type list.
    """
    name: str
    help_msg: str
    options: list = None

    def __init__(self):
        self.options = self.get_options()

    def add_parser(self, sub_parsers):
        parser = sub_parsers.add_parser(self.name, help=self.help_msg)  # add_assets action
        for option in self.options:  # add_assets argument for the action
            option.add_to_parser(parser=parser)

    def run(self, args):
        pass

    @abc.abstractmethod
    def get_options(self):
        raise NotImplementedError
