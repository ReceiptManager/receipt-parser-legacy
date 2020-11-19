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

import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract
from wand.image import Image as WandImage

from receipt_parser import Receipt
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
    print(ORANGE + '\t~: ' + RESET + 'Parse image at: ' + input_file + RESET)
    print(ORANGE + '\t~: ' + RESET + 'Write result to: ' + output_file + RESET)

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


def rescale_image(img):
    print(ORANGE + '\t~: ' + RESET + 'Rescale image' + RESET)
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    return img


def grayscale_image(img):
    print(ORANGE + '\t~: ' + RESET + 'Grayscale image' + RESET)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def remove_noise(img):
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    print(ORANGE + '\t~: ' + RESET + 'Applying gaussianBlur and medianBlur' + RESET)

    img = cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 2)
    return img


def detect_orientation(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    print(ORANGE + '\t~: ' + RESET + 'Get rotation angle:' + str(angle) + RESET)
    return image


def enhance_image(img):
    img = rescale_image(img)
    img = grayscale_image(img)
    img = remove_noise(img)
    img = detect_orientation(img)
    return img


def process_receipt(config, filename):
    input_path = INPUT_FOLDER + "/" + filename

    output_path = OUTPUT_FOLDER + "/" + filename.split(".")[0] + ".txt"

    print(ORANGE + '~: ' + RESET + 'Process image: ' + ORANGE + input_path + RESET)
    prepare_folders()

    try:
        img = cv2.imread(input_path)
    except FileNotFoundError:
        return Receipt(config=config, raw="")

    img = enhance_image(img)
    tmp_path = os.path.join(
        TMP_FOLDER, filename
    )

    print(ORANGE + '~: ' + RESET + 'Temporary store image at: ' + ORANGE + tmp_path + RESET)

    cv2.imwrite(tmp_path, img)

    sharpen_image(tmp_path, tmp_path)
    run_tesseract(tmp_path, output_path, config.language)

    print(ORANGE + '~: ' + RESET + 'Store parsed text at: ' + ORANGE + output_path + RESET)
    raw = open(output_path, 'r').read()

    return Receipt(config=config, raw=raw)


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
            image + ".txt"
        )

        if i != 1: print()
        print(ORANGE + '~: ' + RESET + 'Process image (' + ORANGE + str(i) + '/' + str(
            len(images)) + RESET + ') : ' + input_path + RESET)

        img = cv2.imread(input_path)
        img = enhance_image(img)
        cv2.imwrite(tmp_path, img)

        sharpen_image(tmp_path, tmp_path)
        run_tesseract(tmp_path, out_path, config.language)

        i = i + 1


if __name__ == '__main__':
    main()
