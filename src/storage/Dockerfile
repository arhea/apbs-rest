# FROM python:2.7-alpine
FROM python:3.7
WORKDIR /app
COPY requirements.txt requirements-prod.txt /app/
RUN python -m pip install -r requirements-prod.txt

        # && rm .env
        # && ls -la
ENV STORAGE_CACHE_DIR="/app/.minio_cache" \
    MINIO_URL="localhost:9000" \
    MINIO_ACCESS_KEY="xxx" \
    MINIO_SECRET_KEY="yyyyyyyy" \
    MINIO_JOB_BUCKET="jobs" \
    FLASK_RUN_PORT="5001" \
    FLASK_RUN_HOST="0.0.0.0" \
    FLASK_DEBUG="1" \
    FLASK_APP="main.py"
RUN echo $FLASK_APP

COPY . ./

EXPOSE 5001
# ENTRYPOINT [ "python" ]
# CMD [ "main.py" ]
# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]

ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5001", "main:app" ]