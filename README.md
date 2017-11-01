# 解除网易云音乐海外限制

本程序主要用于解除网易云**等软件**的海外限制问题

**运行本程序的服务器并不需要在中国！**

## How to use ?

只需要找到一个服务器/本机 运行以下命令即可 （需要提前装好docker）
docker run -p 9000:9000 -p 9090:9090 -d ljm625/unblock-netease

然后设置你的设备pac为 http://你的ip:9000/proxy.pac

Or 将你的网易云设置**http代理**为 你的ip:9090

如果你是在一台没有公网地址的机器运行（比如本机），请修改配置文件，将ip取消注释并设置为127.0.0.1 OR **不使用PAC文件**

## How it works?
程序主要使用爬虫抓取http代理公布网站，并且对抓取结果进行**测试**，选出最佳的代理，并建立反向代理。

每隔设定的间隔，程序将再次检测代理的存活状态，如果有需要，则会自动替换代理，作为用户，只需要尽情使用即可

对于发给程序的http请求，程序会**判断目标域名是否处于白名单**中，如果处于白名单中，才会使用反向代理，否则会直接通过本地网络进行转发

## Configuration Parameters

所有的设置都在config.yaml文件中

```
proxy_url: 采集代理的proxy网站
proxy_domain:
  - 代理的http请求域名列表

candidate_num: 抓取的最多代理数目
validate_url: 验证代理的URL
timeout: 验证超时时间（S）
checker_timeout: 二次验证超时时间（S）
check_interval: 检测时间（S）
# Socket params 一些socket参数，不推荐改动
buffer_size: 4096
delay_time: 0.001

# Proxy params
proxy_port: 代理端口设置
# proxy_ip: "127.0.0.1" ## 这个项默认是屏蔽的，如果你取消这行的注释，会在pac文件中强制使用你定义的ip（用于某些没有公网ip的机器，如本机）

```


## Limitations and Improvements

- 目前仅限http代理，比较大的问题是他只能在http上work，如果是其他conn，比如https则会出现问题，下一步是准备实现一个socks5的反代

- 目前对各个代理网站规则内置，拟实现一个模版系统，存储不同代理网站的抓取规则

## Update History

Update 2017/11/01 : Update Wiki details

Update 2017/11/01 : Update 了一下具体参数，代理效果更好

## Contributions

欢迎大家进行测试，提出issue，如果有任何问题，也可以发信到ljm625#gmail.com咨询


# English Version pending