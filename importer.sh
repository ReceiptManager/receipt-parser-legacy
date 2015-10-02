#!/bin/bash

# Script that imports receipts, runs some image preprocessing
# and runs a text recognition tool afterwards.

# Path to scanned receipts on my USB stick. Please adjust.
RECEIPT_SOURCE="/Volumes/NO\\ NAME/DCIM/PHOTO/IMG*"
RECEIPT_DEST="img"

#TODO: ENABLE COPY
#cp ${RECEIPT_SOURCE} ${RECEIPT_DEST}

mkdir -p txt
mkdir -p rotated
mkdir -p preprocessed

for receipt in ${RECEIPT_DEST}/*
do
  echo "Rotating $receipt..."
  receipt_rotated_name="rotated/$(basename $receipt)"
  convert -rotate 90 "$receipt" "$receipt_rotated_name"

  echo "Image preprocessing..."
  receipt_preprocessed_name="preprocessed/$(basename $receipt)"
  convert -auto-level -sharpen 0x4.0 -contrast "$receipt_rotated_name" "$receipt_preprocessed_name"

  echo "OCR text recognition..."
  receipt_txt_name="txt/$(basename $receipt)"
  tesseract -l deu "$receipt_preprocessed_name" $receipt_txt_name

  # TODO: Increase Gamma for non-detected images
  #convert -auto-gamma -sharpen 0x4.0 -contrast "$receipt_rotated_name" "$receipt_preprocessed_name"
done
