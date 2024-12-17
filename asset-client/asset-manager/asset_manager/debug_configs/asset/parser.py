import subprocess


def run_parsing():
    cmd = ["asset"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         encoding='utf-8')
    stdout, stderr = p.communicate()
    print(stdout)


if __name__ == "__main__":
    run_parsing()
