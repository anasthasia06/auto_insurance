FROM python:3.10-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml
COPY . .
EXPOSE 8000
CMD ["uvicorn", "auto_insurance.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
