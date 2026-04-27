FROM python:3.12-slim

WORKDIR /web

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY fe/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fe/ .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]