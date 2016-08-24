FROM tiangolo/uwsgi-nginx-flask:flask
RUN pip install netifaces
COPY ./app /app
