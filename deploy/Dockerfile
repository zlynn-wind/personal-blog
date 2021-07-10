FROM python:3.8

ADD ./requirements.txt /tmp/requirements.txt
ADD ./deploy/gunicorn.py /workspace/gunicorn.py
ADD ./starks /workspace/starks
RUN pip install -r /tmp/requirements.txt -i https://pypi.douban.com/simple \
    && pip install gunicorn

EXPOSE 5000
WORKDIR "/workspace"
CMD ["gunicorn", "-c", "/workspace/gunicorn.py", "starks.wsgi:application"]
