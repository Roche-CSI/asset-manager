import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from asset_utils.utils.log_utils import LoggingMixin


class DefaultHelpParser(ArgumentParser):

    def error(self, message):
        sys.stderr.write('error in command: %s\n' % message)
        self.print_help()
        sys.exit(2)

    def format_help(self) -> str:
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            # print(json.dumps(action_group.__dict__, indent=4, default=str))
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        # print(f"formatter: {formatter.format_help()}")
        return formatter.format_help()


class NewLineFormatter(RawTextHelpFormatter):
    def _split_lines(self, text: str, width):
        # print(f"splitting lines: {text}")
        if text.endswith('\n'):
            return text[2:].splitlines()
        return super()._split_lines(text, width=width)

    def format_help(self) -> str:
        help = self._root_section.format_help()
        # print(f"help: {help}")
        return help


class CommandParser(LoggingMixin):
    parser = None
    groups = {}
    sub_parsers = None

    def __init__(self):
        self.parser = DefaultHelpParser(
            description=self.user_log.colorize("Asset Manager Command Line Tool",
                                               color=self.user_log.colors.cyan),
            formatter_class=NewLineFormatter,
            epilog=self.user_log.colorize('Command Line tool for interacting with assets',
                                          color=self.user_log.colors.cyan)
        )
        sub_parsers = self.parser.add_subparsers(metavar='groups', dest='group')
        sub_parsers.required = True
        self.sub_parsers = sub_parsers

    def add_actions(self, *actions):
        for action in actions:
            action.add_parser(self.sub_parsers)
            self.groups[action.name] = action

    def add_action_groups(self, *groups):
        for group in groups:
            group.add_parser(sub_parsers=self.sub_parsers, parent=self.parser)
            self.groups[group.name] = group

    def parse_args(self, args=None):
        args, unknown = self.parser.parse_known_args(args=args)
        return args, unknown

    def run(self, args=None):
        args, _ = self.parse_args(args=args)
        if args.group:
            self.groups[args.group].execute(args)
        else:
            self.user_log.message("invalid command")
