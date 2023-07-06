FROM ghcr.io/zhayujie/chatgpt-on-wechat:master

RUN sed -i "s/archive.ubuntu./mirrors.aliyun./g" /etc/apt/sources.list
RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list
RUN sed -i "s/security.debian.org/mirrors.aliyun.com\/debian-security/g" /etc/apt/sources.list
RUN sed -i "s/httpredir.debian.org/mirrors.aliyun.com\/debian-security/g" /etc/apt/sources.list

RUN pip install -U pip
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com

ENTRYPOINT ["/entrypoint.sh"]