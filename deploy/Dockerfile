FROM python:3.8

ADD ./requirements.txt /tmp/requirements.txt
ADD ./deploy/gunicorn.conf /workspace/gunicorn.conf
ADD ./deploy/entrypoint.sh /entrypoint.sh
ADD ./starks /workspace/starks
RUN pip install -r /tmp/requirements.txt -i https://pypi.douban.com/simple \
    && pip install gunicorn awscli

EXPOSE 5000
WORKDIR "/workspace"
CMD ["/entrypoint.sh"]
