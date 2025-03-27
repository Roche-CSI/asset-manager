import os
import subprocess

from asset_utils.utils import ch_dir
from asset_utils.utils.log_utils import LoggingMixin


# don't add test prefix here, we don't want pytest to run this

def run(cmds, working_dir=None, code_dir=None):
    script = "asset-manager/asset_manager/app.py"
    base_cmd = [
        "python3",
        os.path.join(code_dir, script)
    ]

    def _run_cmd():
        result = None
        for idx, cmd in enumerate(cmds):
            trg = base_cmd + cmd.split()
            result = subprocess.run(trg, capture_output=True, text=True)
            if idx == 0 or idx != len(cmds) - 1:
                print(f"->cmd: {trg}")
                print(f"->output: {result.stdout}")
                print(f"->error: {result.stderr}")

        # return the last command's output
        return result.stdout, result.stderr

    if working_dir:
        os.makedirs(working_dir, exist_ok=True)
        with ch_dir(working_dir):
            return _run_cmd()
    else:
        return _run_cmd()


class BaseE2ETest(LoggingMixin):
    desc = None
    cmd = None
    out = None
    error = None

    def __init__(self, working_dir: str = None, params: dict = None):
        self.working_dir = working_dir or os.environ.get("WORKING_DIR")
        if not self.working_dir:
            raise Exception("WORKING_DIR not set, you need to set it as environment variable to run the tests")
        self.code_dir = os.environ.get("CODE_DIR")
        if not self.code_dir:
            raise Exception("CODE_DIR not set, you need to set it as environment variable to run the tests")
        self.params = params or {}

    @property
    def command(self):
        formatted = []
        for cmd_string in self.cmd:
            for key in self.params:
                if "{" + key + "}" in cmd_string:
                    cmd_string = cmd_string.format(**{key: self.params[key]})
            formatted.append(cmd_string)
        return formatted

    def run(self):
        self.user_log.info(f"****Running test: {self.desc}====Start")
        out, error = run(self.command, working_dir=self.working_dir, code_dir=self.code_dir)
        self.print_result(output=out, error=error)

    def print_result(self, output: str, error: str):
        self.user_log.message("----output start----")
        self.user_log.message(output)
        self.user_log.message("----output end----")

        is_valid = self.validate(out=output, err=error)
        if is_valid:
            self.user_log.success(f"\nValidating {self.desc} - Success")
        else:
            msg = f"Validating '{self.desc}' - Error, {error}"
            self.user_log.message("----error start----")
            self.user_log.error(msg)
            self.user_log.message("----error end----")
            raise Exception(msg)
        self.user_log.info(f"**Ending test: {self.desc}====End")

    def validate(self, out, err):
        if out and self.out:
            # check if the output contains the expected output
            # we do a loose word matching here instead of exact matching
            for o in self.out.split():
                if o not in out:
                    return False
            return True
        elif self.error:
            # expecting error i.e. user is trying to do something that should fail
            if err != self.error or self.error not in err:
                return False
            else:
                return True
        else:
            return True
