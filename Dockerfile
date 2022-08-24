FROM python:3.10.5

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY stack.env ./

CMD ["python", "-u", "src/main.py"]
