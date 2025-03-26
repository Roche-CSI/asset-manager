import argparse
import os

from server_core.app import create_app
from server_core.configs import Configs
from server_core.run_gunicorn import StandaloneApplication

PORT = 5000
HOST = '0.0.0.0'


def get_app(*args):
    Configs.shared()  # default is DEV
    return create_app()


def parse_args():
    parser = argparse.ArgumentParser(description='Run the asset server')
    parser.add_argument('protocol', choices=['http', 'https'], nargs='?', default='http',
                        help='Protocol to use (http or https)')
    parser.add_argument('--debug', action='store_true',
                        help='Run the server in debug mode')
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_args()

    app = get_app()
    options = {
        'bind': '%s:%s' % (HOST, PORT),
        'workers': 2,
    }
    if args.protocol == 'https':
        options['certfile'] = os.environ.get('SSL_CERT')  # os.path.join(MOUNT_DIR, CERT)
        options['keyfile'] = os.environ.get('SSL_KEY')  # os.path.join(MOUNT_DIR, KEY)

    if args.debug:
        print('running in debug mode')
        app.run(debug=True)
    else:
        print(f'running on: {args.protocol}')
        StandaloneApplication(app, options).run()


if __name__ == '__main__':
    main()
