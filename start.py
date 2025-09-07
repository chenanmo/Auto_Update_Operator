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
import ipaddress

# 加载.env文件中的环境变量
load_dotenv()

host_url = os.getenv('HOST_URL')
username = os.getenv('IKUAI_NAME')
password = os.getenv('IKUAI_PASSWORD')
chinaip_url = os.getenv('CHINAIP_URL')
operator_name = os.getenv('OPERATOR_NAME')
custom_runtime = os.getenv('CUSTOM_RUNTIME')
ip_lines = None


def is_valid_cidr(cidr_str):
    try:
        ipaddress.ip_network(cidr_str)
        return True
    except ValueError:
        return False


def cutting():  # 切割为5000个IP段1组
    global ip_lines

    # 过滤掉注释行、空行和无效的CIDR
    filtered_lines = []
    for line in ip_lines.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and is_valid_cidr(line):
            filtered_lines.append(line)

    chunks = [','.join(filtered_lines[i:i + 5000]) for i in range(0, len(filtered_lines), 5000)]
    return chunks


def get_valid_ip_lines(content):
    """从内容中提取有效的IP行"""
    valid_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and is_valid_cidr(line):
            valid_lines.append(line)
    return valid_lines


def detect_file_updates() -> bool:
    """检测下载文件是否有变动，只比较有效的IP行"""
    dir1 = 'old'
    dir2 = 'new'
    filename = 'ip.txt'
    file1 = os.path.join(dir1, filename)
    file2 = os.path.join(dir2, filename)

    if os.path.exists(file1) and os.path.exists(file2):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()

        # 只比较有效的IP行
        valid_lines1 = get_valid_ip_lines(content1)
        valid_lines2 = get_valid_ip_lines(content2)

        return valid_lines1 != valid_lines2
    elif os.path.exists(file2):
        print('检测到为第一运行,old文件夹为空')
        return True
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
                time.sleep(30)
                download_chinaIP(x + 1)
    except Exception as e:
        if x == 3:
            # print(e)
            print(f'下载营运商IP地址: “{operator_name}”失败,退出执行')
            sys.exit()
        else:
            print(f'下载营运商IP地址:“{operator_name}”失败,正在进行第{x}次重试')
            time.sleep(30)
            download_chinaIP(x + 1)


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

def run_once():
    """单次执行：下载、比对、更新"""
    now1 = datetime.now()
    print('开始检测更新 ', now1.strftime("%Y-%m-%d %H:%M:%S"))
    download_chinaIP()
    if detect_file_updates():
        print('大陆IP有变动,开始更新')
        ikuai_Routing = ikuai_server(host_url=host_url,
                                   username=username,
                                   password=password)
        operator = ikuai_Routing.Operator_list()
        if operator:
            del_id = search_china_operator_id(operator)
            for i in del_id:
                ikuai_Routing.Operator_DEL(i.get('name'), i.get('id'))
        for ip in cutting():
            ikuai_Routing.Operator_ADD(name=operator_name, ipgroup=ip)
        shutil.copy('new/ip.txt', 'old/ip.txt')
        print('更新完成 ', datetime.now().strftime("%H:%M:%S"))
    else:
        print('IP没有变化,不用更新 ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    if not os.path.exists('old'):
        os.makedirs('old')
        print("old目录已创建")

    if not os.path.exists('new'):
        os.makedirs('new')
        print("new目录已创建")

    run_once()
    while True:
        # 获取当前时间
        current_time = time.strftime("%H:%M", time.localtime())
        # 判断是否到达指定时间
        if current_time == custom_runtime:
            run_once()
        # 每隔60秒检测一次
        time.sleep(60)
