# OSはCentOS
FROM centos:latest

# 各パッケージをインストール
# pipやvirtualenvインストールも想定しています。
RUN yum -y update
RUN yum -y groupinstall "Development Tools"
RUN yum -y install \
           kernel-devel \
           kernel-headers \
           gcc-c++ \
           patch \
           libyaml-devel \
           libffi-devel \
           autoconf \
           automake \
           make \
           libtool \
           bison \
           tk-devel \
           zip \
           wget \
           tar \
           gcc \
           zlib \
           zlib-devel \
           bzip2 \
           bzip2-devel \
           readline \
           readline-devel \
           sqlite \
           sqlite-devel \
           openssl \
           openssl-devel \
           git \
           gdbm-devel \
           python-devel

# Python3.5.2をインストール
# Python3.5.2をダウンロード
RUN wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
RUN tar xzvf Python-3.5.2.tgz

# makeでインストール
WORKDIR ./Python-3.5.2
RUN ./configure --with-threads
RUN make install

# pipインストール(最新版)
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

# readlineインストール
RUN pip install readline

# virtualenvインストール
RUN pip install virtualenv

# scrapingに必要なものをインストール
RUN pip install requests
RUN pip install lxml
RUN pip install cssselect
RUN pip install beautifulsoup4

# csv出力に必要なものをインストール
RUN pip install pandas

RUN mkdir -p /src/sandbox
ADD . /src/sandbox
WORKDIR /src/sandbox

CMD ["python", "main.py"]
