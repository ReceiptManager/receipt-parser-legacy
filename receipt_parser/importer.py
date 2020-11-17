# !/usr/bin/python3
# coding: utf-8

# Copyright 2015-2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io
import os

from PIL import Image
from pytesseract import pytesseract
from wand.image import Image as WandImage

from receipt_parser.config import read_config

BASE_PATH = os.getcwd()
INPUT_FOLDER = os.path.join(BASE_PATH, "data/img")
TMP_FOLDER = os.path.join(BASE_PATH, "data/tmp")
OUTPUT_FOLDER = os.path.join(BASE_PATH, "data/txt")

ORANGE = '\033[33m'
RESET = '\033[0m'

def prepare_folders():
    """
    :return: void
        Creates necessary folders
    """

    for folder in [
        INPUT_FOLDER, TMP_FOLDER, OUTPUT_FOLDER
    ]:
        if not os.path.exists(folder):
            os.makedirs(folder)


def find_images(folder):
    """
    :param folder: str
        Path to folder to search
    :return: generator of str
        List of images in folder
    """

    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            try:
                _ = Image.open(full_path)  # if constructor succeeds
                yield file
            except:
                pass


def rotate_image(input_file, output_file, angle=90):
    """
    :param input_file: str
        Path to image to rotate
    :param output_file: str
        Path to output image
    :param angle: float
        Angle to rotate
    :return: void
        Rotates image and saves result
    """
    print(ORANGE + '\t~: ' + RESET + 'Rotate image' + RESET)
    with WandImage(filename=input_file) as img:
        with img.clone() as rotated:
            rotated.rotate(angle)
            rotated.save(filename=output_file)


def sharpen_image(input_file, output_file):
    """
    :param input_file: str
        Path to image to prettify
    :param output_file: str
        Path to output image
    :return: void
        Prettifies image and saves result
    """

    rotate_image(input_file, output_file)  # rotate
    print(ORANGE + '\t~: ' + RESET + 'Increase image contrast and sharp image' + RESET)

    with WandImage(filename=output_file) as img:
        img.auto_level()
        img.sharpen(radius=0, sigma=4.0)
        img.contrast()
        img.save(filename=output_file)


def run_tesseract(input_file, output_file, language="deu"):
    """
    :param input_file: str
        Path to image to OCR
    :param output_file: str
        Path to output file
    :return: void
        Runs tesseract on image and saves result
    """

    print(ORANGE + '\t~: ' + RESET + 'Parse image using pytesseract' + RESET)
    with io.BytesIO() as transfer:
        with WandImage(filename=input_file) as img:
            img.auto_level()
            img.sharpen(radius=0, sigma=4.0)
            img.contrast()
            img.save(transfer)

        with Image.open(transfer) as img:
            image_data = pytesseract.image_to_string(img, lang=language, timeout=60)

            out = open(output_file, "w")
            out.write(image_data)
            out.close()


def main():
    prepare_folders()

    dir_path = os.getcwd()
    config = read_config(config=dir_path + "/config.yml")

    images = list(find_images(INPUT_FOLDER))
    print(ORANGE + '~: ' + RESET + 'Found: ' + ORANGE + str(len(images)),
          RESET + ' images in: ' + ORANGE + INPUT_FOLDER + RESET)

    i = 1
    for image in images:
        input_path = os.path.join(
            INPUT_FOLDER,
            image
        )
        tmp_path = os.path.join(
            TMP_FOLDER,
            image
        )
        out_path = os.path.join(
            OUTPUT_FOLDER,
            image + ".out.txt"
        )

        if i != 1: print()
        print(ORANGE + '~: ' + RESET + 'Process (' + ORANGE + str(i) + '/' + str(len(images)) + RESET + ') : ' + input_path + RESET)
        sharpen_image(input_path, tmp_path)
        run_tesseract(tmp_path, out_path, config.language)

        i = i + 1


if __name__ == '__main__':
    main()
