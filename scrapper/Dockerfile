FROM python:3.13

WORKDIR /app
RUN mkdir /exported-data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "api.app:app", "--port", "8080", "--host", "0.0.0.0"]
