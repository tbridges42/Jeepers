import configparser
import daemon
from os import access, R_OK
from os.path import isfile
from argparse import ArgumentParser


def get_args():
    argparser = ArgumentParser(prog="Jeepers",
                               description="A service for monitoring an attached picamera.")
    argparser.add_argument('-c', '--config', default='config.ini', help="Optionally define a custom config file.")
    argparser.add_argument('-d', '--daemon', action='store_true', help="If present, spawn a daemon.")
    return argparser.parse_args()


def spawn_daemon():
    context = daemon.DaemonContext()
    # TODO: set up daemon parameters
    context.open()
    pass


def create_config(path, parser):
    # TODO: Create default config
    pass


if __name__ == '__main__':
    args = get_args()
    parser = configparser.ConfigParser()
    path = args.config
    if not (isfile(path) and access(path, R_OK)):
        create_config(path, parser)
    parser.read(path)
    if args.daemon:
        spawn_daemon()
    # Do stuff