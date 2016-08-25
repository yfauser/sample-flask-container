FROM tiangolo/uwsgi-nginx-flask:flask
RUN pip install netifaces
RUN pip install netaddr
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY ./uwsgi-streaming.conf /etc/nginx/conf.d/
COPY ./app /app
