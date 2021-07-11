FROM python:3.8

ADD ./requirements.txt /tmp/requirements.txt
ADD ./deploy/gunicorn.conf /workspace/gunicorn.conf
ADD ./starks /workspace/starks
ADD ./entrypoint.sh /entrypoint.sh
ADD ./init-kube-config.py /init-kube-config.py
RUN pip install -r /tmp/requirements.txt -i https://pypi.douban.com/simple \
    && pip install gunicorn awscli

EXPOSE 5000
WORKDIR "/workspace"
CMD ["/entrypoint.sh"]
