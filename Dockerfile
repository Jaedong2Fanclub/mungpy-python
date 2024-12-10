#FROM python:3.7-slim-buster

FROM python:3.7-slim-stretch

# RUN apt-get update && apt-get install -y git python3-dev gcc \
#     && rm -rf /var/lib/apt/lists/*

# RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
#     sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
#     apt-get update --allow-insecure-repositories && \
#     apt-get install -y --allow-unauthenticated git python3-dev gcc && \
#     rm -rf /var/lib/apt/lists/*

# RUN apt-get update --fix-missing && apt-get install -y git python3-dev gcc \
#     && rm -rf /var/lib/apt/lists/*

# 기본 저장소를 archive.debian.org로 교체하고 업데이트 수행
# RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
#     sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
#     echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends git python3-dev gcc && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# 기본 저장소를 archive.debian.org로 교체하고 업데이트 수행
# RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
#     sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
#     echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends git python3-dev gcc && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    apt-get update && \
    apt-get install -y --no-install-recommends git python3-dev gcc g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# OpenSSL 업데이트 추가
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    wget https://www.openssl.org/source/openssl-1.1.1t.tar.gz && \
    tar -xvzf openssl-1.1.1t.tar.gz && \
    cd openssl-1.1.1t && \
    ./config && make && make install && \
    echo "/usr/local/lib64" > /etc/ld.so.conf.d/openssl-1.1.1.conf && \
    ldconfig && \
    cd .. && rm -rf openssl-1.1.1t*

# 기존 OpenSSL 심볼릭 링크 업데이트
RUN ln -sf /usr/local/bin/openssl /usr/bin/openssl

# 불필요한 OpenSSL 라이브러리 제거
RUN apt-get remove -y libssl-dev && apt-get autoremove -y

RUN openssl version


COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY app app/

RUN python app/server.py

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
