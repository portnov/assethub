FROM python:2.7
MAINTAINER Ilya V. Portnov <portnov84@rambler.ru>
ENV PYTHONUNBUFFERED 1

#RUN git clone http://git.iportnov.tech/portnov/assethub.git /assethub/
RUN mkdir /assethub/
WORKDIR /assethub/
#RUN git checkout master
ADD requirements.txt .

RUN pip install -U -r /assethub/requirements.txt

ADD assethub/ .
add install-database.sh /

EXPOSE 8000
CMD python /assethub/manage.py runserver 0.0.0.0:8000

