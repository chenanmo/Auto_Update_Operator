# ikuai_server_api

import httpx
import json
import base64
import hashlib


class ikuai_server:
    login_url = None
    api_url = None
    cookies = None
    username = None
    password = None

    def __init__(self, host_url: str, username: str, password: str) -> list:
        """

        :param host_url: 爱快后台地址 格式http://192.168.1.1
        :param username: 爱快登录用户名
        :param password: 爱快登录密码
        :return: 第一页,前100个自定义营运商的列表
        """
        self.username = username
        self.password = password
        self.api_url = host_url + '/Action/call'  # api调用地址
        self.login_url = host_url + '/Action/login'  # 登录地址
        self.__login()

    def Operator_list(self):
        payload = {
            "func_name": "custom_isp",
            "action": "show",
            "param": {
                "TYPE": "total,data",
                "limit": "0,100",
                "ORDER_BY": "",
                "ORDER": ""
            }
        }

        response = httpx.request("POST", self.api_url, json=payload, cookies=self.cookies)
        return response.json()["Data"]['data']

    def Operator_ADD(self, name: str, ipgroup: str, comment: str = ""):
        """

        :param name: 自定义营运商的名字
        :param ipgroup: 需要添加的IP,最多不超过5000个
        :param comment: 备注,可填可不填
        """
        payload = {
            "func_name": "custom_isp",
            "action": "add",
            "param": {
                "name": name,
                "ipgroup": ipgroup,
                "comment": comment
            }
        }

        response = httpx.request("POST", self.api_url, json=payload, cookies=self.cookies)
        if response.json()["Result"] == 30000:
            print(f"上传{name}成功")
        else:
            print(f"上传{name}失败")

    def Operator_DEL(self, name: str, id: int):
        """
        :param name: 被删除的营运商名字
        :param id: 被删除的营运商ID
        """
        payload = {
            "func_name": "custom_isp",
            "action": "del",
            "param": {"id": id}
        }

        response = httpx.request("POST", self.api_url, json=payload, cookies=self.cookies)
        if response.json()["Result"] == 30000:
            print(f"删除营运商“{name}”成功, ID为{id}")
        else:
            print(f"上传营运商“{name}”失败, ID为{id}")

    def __login(self):
        # 登录爱快后台
        payload = {
            "username": self.username,
            "passwd": self.__encode_password__(),
            "pass": self.__encode_pass__(),
            "remember_password": ""
        }

        response = httpx.request("POST", self.login_url, json=payload)
        if response.json()["Result"] == 10000:
            self.cookies = response.cookies
            print("登录爱快成功")
        else:
            print('登录爱快失败,账号或密码错误')

    def __encode_password__(self):
        """将密码转为MD5"""
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        hash_value = md5.hexdigest()
        return hash_value

    def __encode_pass__(self) -> str:
        """将密码加盐转为base64"""
        d = ("salt_11" + self.password).encode("ASCII")
        encode_pass = base64.b64encode(d).decode()
        return encode_pass
