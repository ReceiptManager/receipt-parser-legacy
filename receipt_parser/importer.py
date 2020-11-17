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

from receipt_parser.config import read_config

BASE_PATH = os.getcwd()
INPUT_FOLDER = os.path.join(BASE_PATH, "data/img")
TMP_FOLDER = os.path.join(BASE_PATH, "data/tmp")
OUTPUT_FOLDER = os.path.join(BASE_PATH, "data/txt")


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
    print("Rotate image: ", input_file, " ~> ", output_file)
    image = cv2.imread(input_file)
    # convert the image to grayscale and flip the foreground
    # and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # grab the (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    #if angle < -45:
    #    angle = -(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
   # else:
     #   angle = -angle

    # rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    cv2.imshow("Input", image)
    cv2.imshow("Rotated", rotated)
    cv2.waitKey(0)
    print("[INFO] angle: {:.3f}".format(angle))

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
    print("Increase image contrast and sharp image")
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

    print("Parse image using pytesseract")
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
    print("Found the following images in", INPUT_FOLDER)
    print(images)

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

        sharpen_image(input_path, tmp_path)
        run_tesseract(tmp_path, out_path, config.language)


if __name__ == '__main__':
    main()
