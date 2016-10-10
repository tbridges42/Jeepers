import picamera
from time import sleep


if __name__ == '__main__':
    camera = picamera.PiCamera(resolution=(1920, 1080), framerate=30)

    sleep(2)
    print("Capturing")
    camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
