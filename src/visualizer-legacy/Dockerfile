FROM python:3.7
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt gunicorn==20.0.4

COPY . /app
EXPOSE 5008

ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5008", "main:app" ]