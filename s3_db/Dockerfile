FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

RUN echo "alias ls='ls --color=auto'" >> ~/.bashrc

COPY . .

CMD ["python", "app.py"]
