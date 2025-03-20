from asset_manager.commands import CliAction, CliOption


class UserPromptSetting(CliAction):
    name = "user-prompt"
    help_msg = "assume the answer as yes for all user prompts"

    def run(self, args):
        if args.value:
            self.user_log.message(args.value)
        else:
            pass
            # todo: complete this implementation
            # self.user_log.message("missing commit message, please use asset commit -m <message text>")

    def get_options(self):
        return [
            CliOption(
                dest="value",
                help_msg="true or false",
                n_args="?",
                positional=True
            ),
        ]
