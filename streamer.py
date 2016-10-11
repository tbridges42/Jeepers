from picamera import PiCamera
from io import BytesIO
from time import sleep


if __name__ == '__main__':
    stream = BytesIO()
    camera = PiCamera()
    camera.resolution = (1920, 1080)
    print("Recording")
    camera.start_recording(stream, format='h264', quality=1)
    camera.wait_recording(15)
    camera.stop_recording()
    print("Done recording")
    stream.seek(0)
    with open("test4.h264", "wb") as f:
        f.write(stream.read())
    stream.close()
