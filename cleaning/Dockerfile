FROM python:3.13

RUN apt-get update && apt-get install ffmpeg -y

WORKDIR /app
RUN mkdir /scrapped-data
RUN mkdir /cleaned-data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8123

CMD ["uvicorn", "app.main:app", "--port", "8123", "--host", "0.0.0.0"]
