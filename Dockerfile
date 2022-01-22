FROM python:3.9

WORKDIR /usr/src/app

# We copy just the requirements.txt first to leverage Docker cache
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["/bin/bash", "./entrypoint.sh" ]