import configparser
import logging

import daemon
import signal

import image_processor
import picamera
from os import access, R_OK
from os.path import isfile
from argparse import ArgumentParser

import network

DEFAULT_CONFIG = 'config.ini'
DEFAULT_LOGFILE = 'jeepers.log'
DEFAULT_CONSOLE_VERBOSITY = logging.DEBUG
DEFAULT_LOGFILE_VERBOSITY = logging.INFO
DEFAULT_HOSTNAME = ''
DEFAULT_PORT = "9191"


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    Stolen from 'Link Electric Monk
    <http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/>
    """

    def __init__(self, mylogger, log_level=logging.INFO):
        self.logger = mylogger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def fileno(self):
        return 0


def get_args():
    argparser = ArgumentParser(prog="Jeepers",
                               description="A service for monitoring an attached picamera.")
    argparser.add_argument('-c', '--config', default='config.ini', help="Optionally define a custom config file.")
    argparser.add_argument('-d', '--daemon', action='store_true', help="If present, spawn a daemon.")
    # TODO: Implement
    argparser.add_argument('-l', '--logfile', help="Location to log messages.")
    # TODO: Implement
    argparser.add_argument('-v', '--verbose', action='count')
    # TODO: Implement
    argparser.add_argument('-H', '--host', help="The server hostname.")
    # TODO: Implement
    argparser.add_argument('-p', '--port', help="The port to use.")
    return argparser.parse_args()


def spawn_daemon(file_handlers=None):
    context = daemon.DaemonContext(working_directory=".",
                                   files_preserve=file_handlers)
    context.signal_map = { signal.SIGTERM: halt }
    context.open()


def create_config(path, parser):
    # TODO: Create default config
    parser['jeepers'] = {}
    parser['jeepers']['logfile'] = DEFAULT_LOGFILE
    parser['jeepers']['logfile_level'] = "INFO"
    parser['jeepers']['hostname'] = DEFAULT_HOSTNAME
    parser['jeepers']['port'] = DEFAULT_PORT
    parser['jeepers']['ssl'] = "True"
    with open(path, 'w') as configfile:
        parser.write(configfile)


def merge_two_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    y = {k: v for k, v in y.items() if v is not None}
    z = x.copy()
    z.update(y)
    return z


def halt(signum, frame):
    logging.getLogger('jeepers').warning("Received shutdown signal")
    logging.getLogger('jeepers').info("==================================\n")


def setup_logger(options):
    logger = logging.getLogger('jeepers')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)15s : %(levelname)8s : %(message)s')

    fh = logging.FileHandler(options['logfile'])
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug("Logger created")

    # sys.stdout = StreamToLogger(logger, logging.DEBUG)
    # sys.stderr = StreamToLogger(logger, logging.DEBUG)
    logger.debug("stdout and stderr routed to logger")

    return [fh.stream]


def main():
    args = get_args()
    parser = configparser.ConfigParser()
    path = args.config
    if not (isfile(path) and access(path, R_OK)):
        print(path + " is not a valid config file. Creating " + DEFAULT_CONFIG)
        create_config(DEFAULT_CONFIG, parser)
        path = DEFAULT_CONFIG
    parser.read(path)
    options = merge_two_dicts(dict(parser.items('jeepers')), vars(args))
    logging_files = setup_logger(options)
    logging.getLogger('jeepers').info("==================================")
    logging.getLogger('jeepers').info("Started jeepers")
    logging.getLogger('jeepers').info("Set up logging")
    if options['daemon']:
        spawn_daemon(file_handlers=logging_files)
        logging.getLogger('jeepers').info("Split off daemon")
    # TODO: Implement program
    # Create camera
    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)
        # Start recording high-res circularIO
        hi_res_stream = picamera.PiCameraCircularIO(camera, seconds=20)
        camera.start_recording(hi_res_stream, format="h264")
        # Start recording low-res stream
        motion_detector = image_processor.MotionDetector((640, 384))
        # Enter main loop
        camera.start_preview()
        while True:
            camera.wait_recording(0.1)
            camera.capture(motion_detector, format="bgr", splitter_port=0, use_video_port=True, resize=(640, 384))
            if motion_detector.motion:
                camera.annotate_text = "Motion Detected"
            else:
                camera.annotate_text = ""


    # If motion
        # Split circularIO
        connection = network.get_connection(parser)
        # Send circularIO to network
        hi_res_stream.copy_to(connection)
        # replace circularIO stream with network stream
        camera.stop_recording()
        camera.start_recording(connection, format="h264")
        camera.wait_recording(20)
        # Extend loop delay to four minutes
    # If not motion
        # Close the network stream
        # Replace the network stream with circularIO

        connection.close()
    handlers = logging.getLogger('jeepers').handlers
    for handler in handlers:
        handler.close()
        logging.getLogger('jeepers').removeHandler(handler)

    logging.shutdown()


if __name__ == '__main__':
    main()
