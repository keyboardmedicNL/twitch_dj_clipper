FROM python:3

WORKDIR /usr/src/app

COPY requirements ./
RUN pip install --no-cache-dir -r requirements

COPY . .

CMD [ "python", "main.py" ]
