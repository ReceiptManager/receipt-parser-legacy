# A fuzzy receipt parser written in Python  

![CI](https://github.com/mre/receipt-parser/workflows/CI/badge.svg)
  
This is a fuzzy receipt parser written in Python. 
It extracts information like the shop, the date, and the total form receipts.
It can work as a standalone script or as part of the [IOS and Android application](https://github.com/ReceiptManager/Application).

## History

This project started as a hackathon idea. Read more about it on the [trivago techblog](http://tech.trivago.com/2015/10/06/python_receipt_parser/).
Also read the comments on [HackerNews](https://news.ycombinator.com/item?id=10338199)
There's also a [talk](https://www.youtube.com/watch?v=TuDeUsIlJz4) about the project.

## Dependencies

* [Tesseract Open Source OCR Engine](https://github.com/tesseract-ocr/tesseract)
* [ImageMagick](http://www.imagemagick.org/script/index.php)

## Usage

To convert all images from the `data/img/` folder to text using tesseract and parse the resulting text files, run

```
make run
```

### Docker

A Dockerfile is available with all dependencies needed to run the program.  
To build the image, run

```
make docker-build
```

To run it on the sample files, try

```
make docker-run
```

By default, running the image will execute the `make run` command. To use with your own images, run the following:

```
docker run -v <path_to_input_images>:/usr/src/app/data/img mre0/receipt-parser
```
