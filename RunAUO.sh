#!/bin/bash

  # 检查环境变量中是否设置了运行时间
  if [ -z "$CUSTOM_RUNTIME" ]; then
    echo "未设置自定义运行时间。请设置环境变量 CUSTOM_RUNTIME 为要运行的时间。"
    exit 1
  fi

data_dir="/data"

# 检测/data目录是否为空
if [ -z "$(ls -A $data_dir)" ]; then
    echo "目录为空。正在从GitHub拉取文件..."

    # 从GitHub上拉取文件到/data目录
    git clone https://github.com/chenanmo/Auto_Update_Operator.git $data_dir

    # 创建new和old文件夹
    mkdir $data_dir/new
    mkdir $data_dir/old

    echo "文件已从GitHub拉取，new/old目录已创建。"
fi

# 启动时先执行一次
python3 /data/main.py

# 死循环，持续检查时间并执行任务
while true
do
  # 获取当前时间
  current_time=$(date +"%H:%M")

  # 如果当前时间等于环境变量中定义的时间，则执行任务
  if [ "$current_time" == "$CUSTOM_RUNTIME" ]; then
    python3 /data/main.py
  fi

  # 每隔一段时间检查一次，避免过多消耗系统资源
  sleep 60  # 每隔60秒检查一次
done