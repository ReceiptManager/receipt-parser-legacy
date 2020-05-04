# !/usr/bin/python3
# coding: utf-8
#
# 
#
# 
#
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


import os

from PIL import Image

BASE_PATH = ".\\"#os.getcwd()
INPUT_FOLDER = os.path.join(BASE_PATH, "data\\img")
TMP_FOLDER = os.path.join(BASE_PATH, "data\\tmp")
OUTPUT_FOLDER = os.path.join(BASE_PATH, "data\\txt")

# --- pytesseract prep
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
the_chosen_lang = 'deu'

# --- End of pytesseract prep

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
    # ImageMagick 6.8.8-10 Q8 x64 doesn't want high-commas around the 90.
    cmd = "convert" + " -rotate " + str(angle)
    #cmd += " '" + input_file + "' '" + output_file + "'"
    cmd += " " + input_file + " " + output_file
    print("Running", cmd)
    os.system(cmd)  # sharpen


def sharpen_image(input_file, output_file):
    """
    :param input_file: str
        Path to image to prettify
    :param output_file: str
        Path to output image
    :return: void
        Prettifies image and saves result
    """
    # ImageMagick must be known explicitly
    rotate_image(input_file, output_file)  # rotate
    cmd = "convert" +" -auto-level -sharpen 0x4.0 -contrast "
    #cmd += "'" + output_file + "' '" + output_file + "'"
    cmd += " " + output_file + " " + output_file
    print("Running", cmd)
    os.system(cmd)  # sharpen

def tess_to_txt(ipf, opf):
    f = open(opf, "w")
    print("Running tesseract on ", ipf, " to ", opf)
    the_text = u""+pytesseract.image_to_string(ipf, timeout=2, lang=the_chosen_lang)
    f.write(the_text)
    f.close()

def run_tesseract(input_file, output_file):
    """
    :param input_file: str
        Path to image to OCR
    :param output_file: str
        Path to output file
    :return: void
        Runs tesseract on image and saves result
    """
    try:
        tess_to_txt(input_file, output_file)
    except RuntimeError as timeout_error:
        # Tesseract processing is terminated
        pass
    #cmd = "tesseract -l deu "
    #cmd += "'" + input_file + "' '" + output_file + "'"
    #print("Running", cmd)
    #os.system(cmd)


def main():
    prepare_folders()
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
        # I did ImageMagick manually here
        # ScanTailor is also possible GUI workaround
        sharpen_image(input_path, tmp_path)
        run_tesseract(tmp_path, out_path)


if __name__ == '__main__':
    main()
