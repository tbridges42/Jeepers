from picamera import PiCamera
from io import BytesIO
from time import sleep


def standby_stream():
    """Uses a circular buffer to continuously monitor camera"""


def motion_detected():
    """Returns True if motion is detected, False otherwise"""
    return False


def get_stream():
    stream = BytesIO()
    camera = PiCamera()
    camera.resolution = (1920, 1080)
    print("Recording")
    camera.start_recording(stream, format='h264', quality=1)
    camera.wait_recording(15)
    camera.stop_recording()
    return stream


if __name__ == '__main__':
    mystream = get_stream()
    mystream.seek(0)
    with open("test4.h264", "wb") as f:
        f.write(mystream.read())
    mystream.close()
