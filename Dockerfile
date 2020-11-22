FROM python:3
RUN apt-get update && apt-get install -y tesseract-ocr-all imagemagick
RUN pip install poetry
WORKDIR /app
COPY . .
RUN poetry install

CMD ["poetry", "run"]
