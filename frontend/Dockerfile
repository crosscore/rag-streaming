# frontend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "alias ls='ls --color=auto'" >> ~/.bashrc

COPY . .

# 必要なディレクトリが存在することを確認
RUN mkdir -p static templates

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
