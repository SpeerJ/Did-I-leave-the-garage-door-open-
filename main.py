import configparser
import datetime
import time

import cv2
import pywhatkit
import pyautogui as pg
from numpy import *
from datetime import datetime, timedelta
import os

# Class to handle the configuration file
class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.expanduser('~') + '/ingressus.conf')

    def get_phone_number(self):
        return self.config.get('Whatsapp', 'phone_number')

    def get_bot_name(self):
        return self.config.get('Whatsapp', 'bot_name')

    def get_vlc_default_image_path(self):
        return self.config.get('Settings', 'image_dir')

    # Video Device used: for example /dev/video1 on linux
    def get_camera_path(self):
        return self.config.get('Settings', 'video_device')

    # Distance Settings: A setting on flood fill that determines the color difference sensitivity of the fill
    def get_distance_settings(self):
        return self.config.get('Settings', 'distance_settings')

    # Flood pixel: A pixel on the door that has similar looking pixels around it to determine whether the door is
    # open or closed egg 244,602
    def get_flood_pixel(self):
        return self.config.get('Settings', 'flood_pixel')


class WhatsappBot:
    def __init__(self, config):
        self.config = config
        self.sent_messages = []

    def phone_number(self):
        return self.config.get_phone_number()

    def bot_name(self):
        return self.config.get_bot_name()

    def send_message(self, message):
        # Use a breakpoint in the code line below to debug your script.
        time.sleep(3)
        pywhatkit.sendwhatmsg_instantly(self.phone_number(),
                                        f'{self.bot_name}: {message}')  # Press Ctrl+8 to toggle the breakpoint.
        time.sleep(2)
        pg.click(1050, 950)
        pg.press("enter")
        self.sent_messages.append(datetime.now())

    # Have their been messages sent recently
    def any_messages_recently(self):
        now = datetime.now()
        three_minutes_ago = now - timedelta(minutes=3)

        for message in self.sent_messages:
            if message < three_minutes_ago:
                return True
        return False


class Door:
    def __init__(self, config):
        self.config = config
        self.door_openings = []

    # Have their been messages sent recently
    def last_opening_greater_than_allowed_time(self, additional_minutes=0):
        now = datetime.now()
        three_minutes_ago = now - timedelta(minutes=3 + additional_minutes)

        for opening in self.door_openings:
            if opening > three_minutes_ago:
                return True
        return False

    def add_opening(self):
        now = datetime.now()
        self.door_openings.append(now)

    def is_closed(self, identical_pixel_count):
        return identical_pixel_count < 10000


class Photo:
    def __init__(self, config):
        self.config = config

    # You need to configure config.get_vlc to output to a specific dir
    def captured_image(self):
        # Timer wasn't working for me so I had to kill all
        os.system(
            f'cvlc -v v4l2://{config.get_camera_path} --video-filter=scene --no-audio --scene-path= --scene-format=png --scene-prefix=snap --scene-replace --scene-ratio=24 --run-time=60 & sleep 5s &&  killall vlc')
        return self.vlc_default_image_path

    def result(self):
        img = cv2.imread(self.captured_image())
        height, width, channels = img.shape
        mask = zeros((height + 2, width + 2), uint8)

        identicalPixels, rect, a, b = cv2.floodFill(img, mask, config.get_flood_pixel, (0, 255, 0),
                                                    config.get_distance_settings,
                                                    config.get_distance_settings)

        print(identicalPixels)
        new_path = config.get_vlc_default_image_path().replace(".jpg", "") + "_result.jpg"
        cv2.imwrite(new_path, img)
        return identicalPixels, new_path


config = Config()

bot = WhatsappBot(config)

door = Door(config)


def queue_and_check():
    if bot.any_messages_recently():
        return

    if door.last_opening_greater_than_allowed_time():
        bot.send_message("Garage door has been open for over 3 minutes, please ensure it's closed")
    else:
        door.add_opening()


def main_loop():
    while 1:
        time.sleep(5)
        photo = Photo(config)
        identical_pixel_count, new_path = photo.result()
        if door.is_closed(identical_pixel_count):
            print("Door Closed")
        else:
            queue_and_check()


if __name__ == '__main__':
    time.sleep(2)
    main_loop()
