FROM python:3.8

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt -i https://pypi.douban.com/simple \
    && pip install gunicorn awscli

ADD ./deploy/gunicorn.py /workspace/gunicorn.py
ADD ./deploy/entrypoint.sh /entrypoint.sh
ADD ./starks /workspace/starks
EXPOSE 5000
WORKDIR "/workspace"
CMD ["gunicorn", "-c", "/workspace/gunicorn.py", "starks.wsgi:application"]
