FROM python:3.8

ADD ./requirements.txt /tmp/requirements.txt
ADD ./deploy/gunicorn.conf /workspace/gunicorn.conf
ADD ./starks /workspace/starks
RUN pip install -r /tmp/requirements.txt -i https://pypi.douban.com/simple \
    && pip install gunicorn

EXPOSE 5000
CMD ["gunicorn", "-c", "/workspace/gunicorn.conf", "starks.wsgi:application"]
