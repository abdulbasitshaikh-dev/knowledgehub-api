FROM python:3.12-slim

WORKDIR /code

COPY requirements-docker.txt .

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.13.0

RUN pip install --no-cache-dir \
    -r requirements-docker.txt

COPY . .

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /code

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]