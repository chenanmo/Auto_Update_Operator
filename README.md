# 自动更新爱快自定义运营商工具
## 使用方法
```text
# 环境变量中添加以下环境变量
HOST_URL = 'http://192.168.10.1' # 爱快路由器地址
IKUAI_NAME = 'test' # 爱快登录用户名
IKUAI_PASSWORD = 'test1234' # 爱快登录密码
CHINAIP_URL = '' # IP文件下载地址,
OPERATOR_NAME = 'test' # 自定义运营商名字
CUSTOM_RUNTIME = '16:00' # 运行时间
PS:
可新建一个账户,但是必须给多线负载修改权限和新功能可读写权限
下载的文件格式要求为txt,内容格式如下(1行一个IP段)
14.192.60.0/22
14.192.76.0/22
14.196.0.0/15
14.204.0.0/15
14.208.0.0/12
27.0.128.0/21
27.0.160.0/21
27.0.188.0/22
27.0.204.0/22
27.0.208.0/21

```