FROM python:3

RUN pip install -U pipenv
RUN apt-get update && apt-get install -y tesseract-ocr-all 

WORKDIR /usr/src/app
COPY . .

RUN make install

CMD ["make", "run"]
