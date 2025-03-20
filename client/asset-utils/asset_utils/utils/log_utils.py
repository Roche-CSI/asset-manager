import logging
import math
import os
import re
import textwrap

import colorama
import tqdm
from tabulate import tabulate

from asset_utils.utils.pager import Pager

INDENT = 70
BOLD = '\033[1m'
END = '\033[0m'

DISABLE_USER_LOG_PRINTING = False


class LogColors:
    ERROR = colorama.Fore.LIGHTRED_EX
    INFO = colorama.Fore.LIGHTCYAN_EX
    SUCCESS = colorama.Fore.LIGHTGREEN_EX
    COMMAND = colorama.Fore.LIGHTYELLOW_EX
    INPUT = colorama.Fore.LIGHTYELLOW_EX
    ACTIVE = colorama.Fore.GREEN
    ALERT = colorama.Fore.RED
    PROGRESS = colorama.Fore.LIGHTWHITE_EX
    green = colorama.Fore.LIGHTGREEN_EX
    red = colorama.Fore.RED
    cyan = colorama.Fore.CYAN
    yellow = colorama.Fore.LIGHTYELLOW_EX
    off_white = colorama.Fore.WHITE


class LogData:
    data = []

    def add(self, message, color=None):
        self.data.append({"message": message, "color": color})

    def print_format(self):
        """format the logs into printable format"""
        if not self.data:
            return None

        result = ""
        for item in self.data:
            msg = colored_string(string=item['message'], color=item['color']) if item['color'] else item['message']
            result += f"{msg}\n"
        return result


def disable_user_log():
    global DISABLE_USER_LOG_PRINTING
    DISABLE_USER_LOG_PRINTING = True


def _user_log_content(msg, paged=False):
    """wrapper function that displays message to user"""
    if DISABLE_USER_LOG_PRINTING:
        return
    elif paged:
        Pager().paged_print(msg)
    else:
        print(msg)


def _user_log_title(title):
    return """{blue}{title}{nc}""" \
        .format(blue=colorama.Fore.LIGHTRED_EX, nc=colorama.Fore.RESET, title=title)


class UserLog:

    @property
    def colors(self) -> LogColors:
        return LogColors

    def indented_message(self, body, color=None, title=None):
        if title:
            prefix = "" + ":\t"
            expanded_indent = textwrap.fill(prefix + '$', replace_whitespace=False)[:-1]
            subsequent_indent = ' ' * len(expanded_indent)
            wrapper = textwrap.TextWrapper(initial_indent=subsequent_indent, subsequent_indent=subsequent_indent)
            _user_log_content(_user_log_title(f"{title}\n") + wrapper.fill(colored_string(body, color)))
        else:
            _user_log_content(colored_string(body, color))

    def message(self, body, color=None, title=None, bulleted=False, formatted=True, paged=False):
        if formatted:
            if bulleted:
                body = self.__bulleted_message(data=body)
            if title:
                _user_log_content(_user_log_title(f"{title}\n") + colored_string(body, color), paged=paged)
            else:
                _user_log_content(colored_string(body, color), paged=paged)
        else:
            if color or title or bulleted:
                raise Exception("color, title and bulleted can only be used with formatted=True")
            _user_log_content(body, paged=paged)

    def ask_user(self, question: str, options: list, default: str, ask_confirmation=True):
        dont_ask = os.getenv("ASSET_DONT_ASK_USER") == "true" or not ask_confirmation
        if dont_ask:
            opts = '\n'.join([f" - {opt}" for opt in options])
            msg = f"received DONT_ASK_USER=true \n" \
                  f"user_prompt: {question} options:\n{opts}\n default: {default}\n"
            msg += "using default value: {}".format(default)
            self.message(colored_string(msg, LogColors.INPUT))
            return default
        prompt = f"{question} options: ({'/'.join(options)}), default: [{default}]: "
        return self._get_input(prompt=prompt, default=default)

    def _get_input(self, prompt: str, default: str):
        try:
            return input(colored_string(prompt, LogColors.INPUT)) or default
        except Exception as e:
            self.error(f"Error in getting input from user: {e}")
            self.info(f"using default option: {default}")
            return default
        except KeyboardInterrupt:
            self.info("User interrupted, aborted")
            exit(1)

    def error(self, message: str):
        self.message(body=message, color=LogColors.ERROR)

    def info(self, message: str):
        self.message(body=message, color=LogColors.INFO)

    def alert(self, message: str):
        self.message(body=message, color=LogColors.ALERT)

    def success(self, message: str):
        self.message(body=message, color=LogColors.SUCCESS)

    def colorize(self, string: str, color):
        return colored_string(string=string, color=color)

    def bulletize(self, items: [str]):
        return self.__bulleted_message(data=items)

    def dict_to_logs(self, data: dict) -> str:
        """print formatted string representation of dictionary"""
        return ",".join([f"{key}: {data[key]}" for key in data])

    def __bulleted_message(self, data: list):
        return '\n'.join(['{} {}'.format("-", val) for i, val in (enumerate(data))])

    def boxed(self, message, border_color=None) -> None:
        _user_log_content(_boxed_message(message=message, border_color=border_color))

    def table(self, columns: dict, rows: list, table_fmt="simple", col_align=None, paged=False, indent=0) -> None:
        """prints table format
        Parameters
        ----------
        columns: dict, key is which key to extract from each element of data, value if title
        rows: list of dicts

        Returns
        -------
        """
        # header = [list(columns.values())]
        # body = [[d[key] if type(d) is dict else getattr(d, key) for key in columns.keys()] for d in rows]
        # alignment = ("left" for key in columns.keys())
        _user_log_content(self.table_formatted(columns=columns,
                                               rows=rows,
                                               table_fmt=table_fmt,
                                               col_align=col_align,
                                               indent=indent), paged=paged)

    def table_formatted(self, columns: dict, rows: list, table_fmt="pretty", col_align=None, indent=0) -> str:
        """Returns formatted table

        Parameters
        ----------
        columns: dict, key is which key to extract from each element of data, value if title
        rows: list of dicts
        table_fmt: str, table format
        col_align: list of str, column alignment
        indent: int, indent

        Returns
        -------
        str
        """
        header = [list(columns.values())]
        body = [[d[key] if type(d) is dict else getattr(d, key) for key in columns.keys()] for d in rows]
        alignment = ["left" for i in range(0, len(columns.keys()))]
        if col_align:
            for i, col in enumerate(col_align):
                alignment[i] = col
        table = tabulate(header + body, headers="firstrow", tablefmt=table_fmt, colalign=alignment).strip()

        # add indent
        if indent:
            table = "\n".join(["\t" * indent + row for row in table.split("\n")])
        return table


class TqdmLoggingHandler(logging.Handler):
    """Custom Loghandler so logging doesn't interfere with tqdm progress bars"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def get_logger(name):
    log_format1 = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    log_format2 = '%(levelname)-6s [%(name)-12s: %(lineno)d] %(message)s'
    logging.basicConfig(level=logging.WARNING,
                        format=log_format2,
                        datefmt='%m-%d %H:%M')
    # logging.basicConfig(format=log_format1,
    #                     datefmt='%Y-%m-%d:%H:%M:%S',
    #                     level=logging.DEBUG)
    logger = logging.getLogger(name)
    logger.addHandler(TqdmLoggingHandler())
    return logger


class LoggingMixin:
    user_log: UserLog = UserLog()

    @classmethod
    def logger(cls) -> logging.Logger:
        return get_logger(f"{cls.__module__}.py")

    @property
    def log(self) -> logging.Logger:
        try:
            return self._log
        except AttributeError:
            self._log = self.__class__.logger()
            return self._log


def colorize(message, color=None, style=None):
    """Returns a message in a specified color."""
    if not color:
        return message

    styles = {
        "dim": colorama.Style.DIM,
        "bold": colorama.Style.BRIGHT,
    }

    return "{style}{color}{message}{reset}".format(
        style=styles.get(style, ""),
        color=color,
        # color=colors.get(color, ""),
        message=message,
        reset=colorama.Style.RESET_ALL,
    )


def format_link(link):
    return "<{blue}{link}{nc}>".format(
        blue=colorama.Fore.CYAN, link=link, nc=colorama.Fore.RESET
    )


def _boxed_message(message, border_color=None):
    """Put a message inside a box.

    Args:
        message (unicode): message to decorate.
        border_color (unicode): name of the color to outline the box with.
    """
    lines = message.split("\n")
    max_width = max(_visual_width(line) for line in lines)

    padding_horizontal = 10
    padding_vertical = 1

    box_size_horizontal = max_width + (padding_horizontal * 2)

    chars = {"corner": "+", "horizontal": "-", "vertical": "|", "empty": " "}

    margin = "{corner}{line}{corner}\n".format(
        corner=chars["corner"], line=chars["horizontal"] * box_size_horizontal
    )

    padding_lines = [
        "{border}{space}{border}\n".format(
            border=colorize(chars["vertical"], color=border_color),
            space=chars["empty"] * box_size_horizontal,
        ) * padding_vertical
    ]

    content_lines = [
        "{border}{space}{content}{space}{border}\n".format(
            border=colorize(chars["vertical"], color=border_color),
            space=chars["empty"] * padding_horizontal,
            content=_visual_center(line, max_width),
        )
        for line in lines
    ]

    box_str = "{margin}{padding}{content}{padding}{margin}".format(
        margin=colorize(margin, color=border_color),
        padding="".join(padding_lines),
        content="".join(content_lines),
    )

    return box_str


def _visual_width(line):
    """Get the the number of columns required to display a string"""
    return len(re.sub(colorama.ansitowin32.AnsiToWin32.ANSI_CSI_RE, "", line))


def _visual_center(line, width):
    """Center align string according to its visual width"""
    spaces = max(width - _visual_width(line), 0)
    left_padding = int(spaces / 2)
    right_padding = spaces - left_padding

    return (left_padding * " ") + line + (right_padding * " ")


def colored_string(string, color=None):
    text = f"{string}{colorama.Fore.RESET}"
    return f"{color}{text}" if color else text


def bold_string(msg):
    return colored_string(msg, color=BOLD) + END


def asset_logo():
    # fonts = "standard", black_square
    logo = colored_string("🅰🆂🆂🅴🆃-🅼🅰🅽🅰🅶🅴🆁", color=colorama.Fore.LIGHTYELLOW_EX)
    return logo


def kilo_byte(byte: int):
    return math.ceil(int(byte) / 1024)


def comma_formatted(number: int):
    return "{:,}".format(number)
