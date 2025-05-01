FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000
EXPOSE 8501

RUN chmod +x start.sh

CMD ["bash", "start.sh"]
