import random
from subprocess import STDOUT, call
from typing import Union
from PIL import Image

import re
from cv2 import CAP_PROP_FOURCC
from stegano import lsb
from os.path import isfile,join
from typing import Union
import time                                                                 #install time ,opencv,numpy modules
import cv2
import glob

from stegano import lsb
from os.path import isfile,join

import time                                                                 #install time ,opencv,numpy modules
import cv2
import numpy as np
import math
import os
import shutil
from subprocess import call,STDOUT


def data_to_binary(data: bytes) -> list:
    binary_strings = []
    for i in data:
        binary_strings.append(format(i, '08b'))
    return binary_strings

randonnumber = random.randint(0, len([name for name in os.listdir('./temp') if os.path.isfile(name)]))

def modify_pixels(pixels, data: bytes):
    binary_strings = data_to_binary(data)
    data_length = len(binary_strings)
    image_data = iter(pixels)
    for i in range(data_length):
        pixels = [value for value in next(image_data)[:3] + next(image_data)[:3] + next(image_data)[:3]]
        for j in range(0, 8):
            if binary_strings[i][j] == '0' and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif binary_strings[i][j] == '1' and pixels[j] % 2 == 0:
                if pixels[j] > 0:
                    pixels[j] -= 1
                else:
                    pixels[j] += 1
        if i == data_length - 1:
            if pixels[-1] % 2 == 0:
                if pixels[-1] > 0:
                    pixels[-1] -= 1
                else:
                    pixels[-1] += 1
        else:
            if pixels[-1] % 2 != 0:
                pixels[-1] -= 1
        pixels = tuple(pixels)
        yield pixels[0:3]
        yield pixels[3:6]
        yield pixels[6:9]

def frame_extraction(video):
    if not os.path.exists("./temp/"):
        os.makedirs("temp")
    temp_folder="./temp/"            # Temporary folder created to store the frames and audio from the video.
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1

def encode_data(data: Union[bytes,str],image_path: str,Output_path: str):
    frame_extraction(image_path)
    call(["ffmpeg", "-i",image_path, "-q:a", "0", "-map", "a", "./temp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    encode(data,Output_path)
    # Merge()
    call(["ffmpeg", "-i", "temp/%d.png" , "-c:a", "png", "project.avi", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", "project.avi", "-i", "./temp/audio.mp3", "-c:a", "copy", "project12.avi", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
	


# This function would delete the temp directory 
def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")

numbers = re.compile(r'(\d+)')
def numericalSort(value): 
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def Merge():
    img_array = []
    for filename in sorted(glob.glob('./temp/*.png'),key=numericalSort):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    out = cv2.VideoWriter('./temp/project12.avi',cv2.VideoWriter_fourcc(*'DIVX'),15, size)
 
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


def encode(data: Union[bytes, str], output_path: str,root="./temp/{}.png".format(randonnumber)):
    if isinstance(data, str):
        data = data.encode('utf-8')
    print(root)
    image = Image.open(root)

    new_image = image.copy()
    os.remove(root)
    width = new_image.size[0]
    x, y = 0, 0
    for pixel in modify_pixels(new_image.getdata(), data):
        new_image.putpixel((x, y), pixel)
        if x == width - 1:
            x = 0
            y += 1
        else:
            x += 1
    new_image.save(output_path, 'png')


def decode(image_path: str):
    f_name = "./temp/{}.png".format(randonnumber)
    image = Image.open(f_name,'r')
    data = b''
    image_data = iter(image.getdata())
    while True:
        pixels = [value for value in next(image_data)[:3] + next(image_data)[:3] + next(image_data)[:3]]
        binary_string = ''
        for i in pixels[:8]:
            if i % 2 == 0:
                binary_string += '0'
            else:
                binary_string += '1'
        data += bytes((int(binary_string, 2),))
        if pixels[-1] % 2 != 0:
            return data
