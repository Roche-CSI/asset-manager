import sys
from io import StringIO

from asset_utils.utils import LogColors
from asset_utils.utils.progress import Progress


def test_progress_bar():
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    pbar = Progress.progress_bar(total=100, desc="test")
    assert pbar.total == 100  # Assert initial total
    pbar.update(50)
    assert pbar.n == 50  # Assert progress after update
    pbar.close(message="done", color=LogColors.SUCCESS)

    output = sys.stdout.getvalue()
    assert "done" in output  # Assert message in output

    # Reset for second part of the test
    sys.stdout.seek(0)
    sys.stdout.truncate(0)

    pbar = Progress.progress_bar(total=100, desc="failed test")
    pbar.close(message="failed", color=LogColors.ERROR)

    output = sys.stdout.getvalue()
    assert "failed" in output  # Assert message in output

    sys.stdout = original_stdout  # Reset stdout


def test_status_bar():
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    pbar = Progress.progress_bar(total=100, desc="test")
    assert pbar.total == 100  # Assert initial total
    pbar.update(50)
    assert pbar.n == 50  # Assert progress after update
    pbar.close(message="done", color=LogColors.SUCCESS)

    output = sys.stdout.getvalue()
    assert "done" in output  # Assert message in output

    # Reset for second part of the test
    sys.stdout.seek(0)
    sys.stdout.truncate(0)

    pbar = Progress.progress_bar(total=100, desc="failed test")
    pbar.close(message="failed", color=LogColors.ERROR)

    output = sys.stdout.getvalue()
    assert "failed" in output  # Assert message in output

    sys.stdout = original_stdout  # Reset stdout
