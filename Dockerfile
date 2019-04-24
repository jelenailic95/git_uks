FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD . /code

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/

EXPOSE 8000

RUN ["chmod", "+x","./entrypoint.sh"]