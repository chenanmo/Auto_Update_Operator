# 导入os模块
import os
import sys
import shutil
import filecmp
from datetime import datetime
import time
import httpx
from dotenv import load_dotenv
from ikuai import ikuai_server

# 加载.env文件中的环境变量
load_dotenv()

host_url = os.getenv('HOST_URL')
username = os.getenv('IKUAI_NAME')
password = os.getenv('IKUAI_PASSWORD')
chinaip_url = os.getenv('CHINAIP_URL')
operator_name = os.getenv('OPERATOR_NAME')
custom_runtime = os.getenv('CUSTOM_RUNTIME')
ip_lines = None


def cutting():  # 切割为5000个IP段1组
    lines = ip_lines.split('\n')
    chunks = [','.join(lines[i:i + 5000]) for i in range(0, len(lines), 5000)]
    return chunks


def detect_file_updates() -> bool:
    """检测下载文件是否有变动"""
    dir1 = 'old'
    dir2 = 'new'
    filename = 'ip.txt'
    file1 = os.path.join(dir1, filename)
    file2 = os.path.join(dir2, filename)

    if os.path.exists(file1) and os.path.exists(file2):
        same = filecmp.cmp(file1, file2)
        return not same  # 如果文件不一致，则返回True；一致则返回False
    elif os.path.exists(file2):
        print('检测到为第一运行,old文件夹为空')
        return True  # old文件夹下没有IP.txt文件，返回True
    else:
        print('old和new文件夹下都没有ip.txt文件，退出执行')
        sys.exit()


def download_chinaIP(x=0):
    """下载中国IP文件"""
    global ip_lines
    try:
        response = httpx.get(chinaip_url)
        if response.status_code == 200:
            content = response.text
            with open('new/ip.txt', 'w') as file:
                file.write(content)
            # print(content)
            ip_lines = content
        else:
            if x == 3:
                # print(e)
                print(f'下载营运商IP地址:“{operator_name}”失败,退出执行')
                sys.exit()
            else:
                print(f'下载营运商IP地址:“{operator_name}”失败,正在进行第{x}次重试')
                i = x + 1
                download_chinaIP(i)
    except Exception as e:
        if x == 3:
            # print(e)
            print(f'下载营运商IP地址: “{operator_name}”失败,退出执行')
            sys.exit()
        else:
            print(f'下载营运商IP地址:“{operator_name}”失败,正在进行第{x}次重试')
            i = x + 1
            download_chinaIP(i)


def search_china_operator_id(Operator_List: list[dict]) -> list[dict]:
    """

    :param Operator_List: 包含字典的营运商列表
    :return: 营运商的名字和ID
    """
    name = operator_name
    data: list[dict] = []
    for operator in Operator_List:
        if operator.get('name') == name:
            data.append({"name": operator.get('name'), "id": operator.get('id')})
    return data


if __name__ == '__main__':
    if not os.path.exists('old'):
        os.makedirs('old')
        print("old目录已创建")

    if not os.path.exists('new'):
        os.makedirs('new')
        print("new目录已创建")
    while True:
        # 获取当前时间
        current_time = time.strftime("%H:%M", time.localtime())
        # 判断是否到达指定时间
        if current_time == custom_runtime:
            now1 = datetime.now()
            current_time1 = now1.strftime("%Y-%m-%d %H:%M:%S")
            print('开始检测更新 ', current_time1)
            download_chinaIP()  # 下载最新的IP
            if detect_file_updates():  # 检测下载的IP和以前的是否一致,
                print('大陆IP有变动,开始更新')
                ikuai_Routing = ikuai_server(host_url=host_url, username=username, password=password)  # 登录爱快
                operator = ikuai_Routing.Operator_list()  # 获取爱快的自定义营运商列表
                if operator:
                    del_id = search_china_operator_id(operator)  # 获取可以删除的名字和ID
                    for i in del_id:
                        ikuai_Routing.Operator_DEL(i.get('name'), i.get('id'))  # 删除旧的大陆IP
                for ip in cutting():
                    ikuai_Routing.Operator_ADD(name=operator_name, ipgroup=ip)  # 上传新的大陆IP

                shutil.copy('new/ip.txt', 'old/ip.txt')
                now2 = datetime.now()
                current_time2 = now2.strftime("%H:%M:%S")
                print('更新完成 ', current_time2)
            else:
                now2 = datetime.now()
                current_time2 = now2.strftime("%Y-%m-%d %H:%M:%S")
                print('IP没有变化,不用更新 ', current_time2)

        # 每隔60秒检测一次
        time.sleep(60)
