from .base_action import BaseAction


class CommandGroup(BaseAction):
    """create an instance of this class for every command group
    i.e. class, credentials etc
    """
    name: str = None
    help: str = None
    description: str = None
    actions: {} = None
    default_action = None

    def __init__(self,
                 name: str = None,
                 help: str = None,
                 description: str = None,
                 actions: list = None,
                 default_action=None):
        self.name = name
        self.help = help
        self.description = description
        actions = actions or self.get_actions()
        self.actions = {action.name: action for action in actions}
        self.default_action = default_action

    def run(self, args):
        if args.action in self.actions:
            self.actions[args.action].execute(args=args)
        elif self.default_action:
            return self.default_action.execute(args=args)

    def add_parser(self, sub_parsers, parent):
        group_parser = sub_parsers.add_parser(self.name,
                                              help=self.help,
                                              description=self.description,
                                              formatter_class=parent.formatter_class,
                                              )
        cmd_sub_parser = group_parser.add_subparsers(metavar='actions',
                                                     dest='action')
        for action in self.actions.values():
            action.add_parser(sub_parsers=cmd_sub_parser)

    # noinspection PyMethodMayBeStatic
    def get_actions(self):
        """subclass overrides"""
        return []
