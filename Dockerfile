FROM python:3.5

WORKDIR /PriceScraper

ADD . /PriceScraper

RUN pip install -r requirements.txt

EXPOSE 1433

CMD ["python", "main.py"]
