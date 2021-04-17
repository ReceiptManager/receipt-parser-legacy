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
from scipy.ndimage import interpolation as inter

from receipt_parser_core import Receipt
from receipt_parser_core.config import read_config

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
    with WandImage(filename=input_file) as img:
        width, height = img.size
        if width < height:
            angle = 0

        print(ORANGE + '\t~: ' + RESET + 'Rotate image by: ' + str(angle) + "°" + RESET)
        with img.clone() as rotated:
            rotated.rotate(angle)
            rotated.save(filename=output_file)

def deskew_image(image, delta=1, limit=5):
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)

    print(ORANGE + '\t~: ' + RESET + 'Deskew image by: ' + str(best_angle) + ' angle' + RESET)

    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
              borderMode=cv2.BORDER_REPLICATE)

    return rotated

def sharpen_image(input_file, output_file):
    """
    :param input_file: str
        Path to image to prettify
    :param output_file: str
        Path to output image
    :return: void
        Prettifies image and saves result
    """

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
            img.save(transfer)

        with Image.open(transfer) as img:
            image_data = pytesseract.image_to_string(img, lang=language, timeout=60, config="--psm 6")

            out = open(output_file, "w", encoding='utf-8')
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

    img = cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 2)

    return img


def remove_shadows(img):
    rgb_planes = cv2.split(img)

    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)

    result = cv2.merge(result_planes)

    return result


def detect_orientation(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    print(ORANGE + '\t~: ' + RESET + 'Get rotation angle:' + str(angle) + RESET)

    return image


def enhance_image(img, tmp_path ,high_contrast=True, gaussian_blur=True, rotate=True): 
    img = rescale_image(img)

    if rotate:
        cv2.imwrite(tmp_path, img)
        rotate_image(tmp_path, tmp_path)
        img = cv2.imread(tmp_path)

    img = deskew_image(img)
    img = remove_shadows(img)

    if high_contrast:
        img = grayscale_image(img)

    if gaussian_blur:
        img = remove_noise(img)

    return img


def process_receipt(config, filename, rotate=True, grayscale=True, gaussian_blur=True):
    input_path = INPUT_FOLDER + "/" + filename

    output_path = OUTPUT_FOLDER + "/" + filename.split(".")[0] + ".txt"

    print(ORANGE + '~: ' + RESET + 'Process image: ' + ORANGE + input_path + RESET)
    prepare_folders()

    try:
        img = cv2.imread(input_path)
    except FileNotFoundError:
        return Receipt(config=config, raw="")

    tmp_path = os.path.join(
        TMP_FOLDER, filename
    )
    img = enhance_image(img, tmp_path,grayscale, gaussian_blur)

    print(ORANGE + '~: ' + RESET + 'Temporary store image at: ' + ORANGE + tmp_path + RESET)

    cv2.imwrite(tmp_path, img)

    sharpen_image(tmp_path, tmp_path)
    run_tesseract(tmp_path, output_path, config.language)

    print(ORANGE + '~: ' + RESET + 'Store parsed text at: ' + ORANGE + output_path + RESET)
    raw = open(output_path, 'r').readlines()

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
        img = enhance_image(img, tmp_path)
        cv2.imwrite(tmp_path, img)

        sharpen_image(tmp_path, tmp_path)
        run_tesseract(tmp_path, out_path, config.language)

        i = i + 1


if __name__ == '__main__':
    main()
