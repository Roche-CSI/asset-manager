import colorama

from asset_utils.utils.log_utils import LogData, colored_string, colorize, UserLog, LogColors, \
    kilo_byte, comma_formatted


def test_log_data_add():
    log_data = LogData()
    message = "Test message"
    color = LogColors.INFO
    log_data.add(message, color)
    assert len(log_data.data) == 1, "LogData should contain exactly one message."
    assert log_data.data[0] == {"message": message, "color": color}, "Toes not match the expected values."


def test_log_data_print_format():
    log_data = LogData()
    log_data.data.clear()  # make sure data is empty
    messages = [("First message", LogColors.ERROR), ("Second message", None)]
    expected_output = ""
    for message, color in messages:
        log_data.add(message, color)
        expected_output += f"{colored_string(message, color)}\n" if color else f"{message}\n"
    assert log_data.print_format().strip() == expected_output.strip(), "Output does not match expected format."


def test_colorize_with_style():
    message = "Test message"
    color = LogColors.ERROR
    style = "bold"
    expected_result = f"{colorama.Style.BRIGHT}{color}{message}{colorama.Style.RESET_ALL}"
    assert colorize(message, color=color, style=style) == expected_result


def test_bulletize():
    user_log = UserLog()
    items = ["Item 1", "Item 2"]
    result = user_log.bulletize(items)
    expected = "- Item 1\n- Item 2"
    assert result.strip() == expected


def test_dict_to_logs():
    user_log = UserLog()
    data = {"key1": "value1", "key2": "value2"}
    result = user_log.dict_to_logs(data)
    expected = "key1: value1,key2: value2"
    assert result == expected


def test_kilo_byte():
    # Test typical use case
    assert kilo_byte(1024) == 1
    # Test rounding up
    assert kilo_byte(1025) == 2
    # Test zero bytes
    assert kilo_byte(0) == 0
    # Test negative bytes
    assert kilo_byte(-1024) == -1


def test_comma_formatted():
    # Test typical use case
    assert comma_formatted(1000) == "1,000"
    # Test large number
    assert comma_formatted(1000000) == "1,000,000"
    # Test zero
    assert comma_formatted(0) == "0"
    # Test negative number
    assert comma_formatted(-1000) == "-1,000"
