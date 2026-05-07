
# DokcerでたてたサーバーにSSHで接続


https://qiita.com/tkek321/items/346deb99f595308b8ada


Dockerfile

```
FROM ubuntu:16.04

# 1
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# 2
# ssh設定ファイルの書換え
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# 3
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# 4
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# 5
# 手元の公開鍵をコピー
COPY id_rsa.pub /root/authorized_keys

# 6
# ssh用の port を晒す
EXPOSE 22

# 7
# 公開鍵を使えるようにする (パーミッション変更など)
CMD mkdir ~/.ssh && \
    mv ~/authorized_keys ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys &&  \
    # 最後に ssh を起動
    /usr/sbin/sshd -D

```



https://skydum.hatenablog.com/entry/2022/05/06/220820


```
# syntax=docker/dockerfile:1-labs
FROM centos:7

RUN yum update -y
RUN yum install -y xinetd
RUN yum install -y telnet-server

# rootで同時に接続したいユーサー数の数だけ書く
# 一般ユーザーの場合は記載する必要なし
RUN echo "pts/0" >> /etc/securetty
RUN echo "pts/1" >> /etc/securetty
RUN echo "pts/2" >> /etc/securetty

RUN echo "root:root" | chpasswd

RUN adduser user
RUN echo "user:user" | chpasswd

COPY <<EOF /etc/xinetd.d/telnet
service telnet
{
    flags = REUSE
    socket_type = stream
    wait = no
    user = root
    server = /usr/sbin/in.telnetd
    log_on_failure += USERID
    disable = no
}
EOF

COPY <<EOF /docker-entrypoint.sh
#!/bin/bash
xinetd -dontfork -stayalive
EOF

RUN chmod 777 docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
```


1つのDockerコンテナでサービスをたくさん動かす
https://www.itmedia.co.jp/enterprise/articles/1602/17/news004.html


https://www.itmedia.co.jp/enterprise/articles/1602/17/news004_3.html



Ubuntu+Python3(任意のバージョン)の実行環境を構築するDockerfile

https://qiita.com/ntatsuya/items/ef8f48d5e482d4b0f100

```
# 必要そうなものをinstall
RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential libreadline-dev \ 
libncursesw5-dev libssl-dev libsqlite3-dev libgdbm-dev libbz2-dev liblzma-dev zlib1g-dev uuid-dev libffi-dev libdb-dev

#任意バージョンのpython install
RUN wget --no-check-certificate https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz \
&& tar -xf Python-3.9.5.tgz \
&& cd Python-3.9.5 \
&& ./configure --enable-optimizations\
&& make \
&& make install

#サイズ削減のため不要なものは削除
RUN apt-get autoremove -y

#必要なpythonパッケージをpipでインストール
#RUN pip3 install --upgrade pip && pip3 install --no-cache-dir jupyterlab

#requirements.txtなら以下のように
#RUN pip3 install -r ./requirements.txt
```



Dockerコンテナの環境でリモート開発
https://chigusa-web.com/blog/vs-codeでdockerのpython環境でリモート開発/




Docker Compose 徹底解説 - SlideShare
https://www.google.co.jp/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjzhPm1wqj7AhXMgFYBHRRzDDAQFnoFCLMCEAE&url=https%3A%2F%2Fwww.slideshare.net%2Fzembutsu%2Fdocker-compose-guidebook&usg=AOvVaw0okeyuCVMt99h8plvhk1Nh



###### tags: `docker`