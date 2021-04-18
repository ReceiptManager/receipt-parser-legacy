FROM python:3.7
RUN apt-get update && apt-get install -y tesseract-ocr-all imagemagick ffmpeg libsm6 libxext6
RUN pip install poetry
WORKDIR /app
COPY . .

RUN mkdir -p /app/data/img
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/txt

RUN poetry install

CMD ["make", "run"]
