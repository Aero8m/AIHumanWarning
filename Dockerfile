FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories
RUN apk add ninja gcc g++

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY migrations migrations
COPY boot.sh run.py ./

RUN chmod +x boot.sh


EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
