# 使用官方的python#使用官方的python:3.12.2-alpine3.19镜像作为基础镜像
FROM python:3.12.2-alpine3.19


# 复制脚本
COPY RunAUO.sh /usr/local/bin
#更换apline源为国内源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    #解决apline的时区问题
    apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    # 安装基本软件
    apk add --no-cache git bash dash && \
    # 安装python模块
    pip install --upgrade pip && \
    pip install httpx && \
    # 清理缓存
    rm -rf /var/cache/apk/* && \
    # 给权限
    chmod +x /usr/local/bin/RunAUO.sh


# 设置工作目录为/data
WORKDIR /data

# 启动执行脚本为run.sh
CMD ["RunAUO.sh"]