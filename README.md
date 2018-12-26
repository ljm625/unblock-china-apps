# HTTP Proxy Auto Fetching and act as reverse proxy.

This program is useful when you need specific HTTP Proxy, but since HTTP Proxy are easy to get, but usually are not stabilized.


The program will fetch the proxy from proxy websites, test them, then act as a proxy itself. For user, you just need to set proxy to the program and enjoy surfing.

It's very useful for some location restriction applications. But currently only support HTTP connections.

It also have a fake DNS Server module, which u can use and it will direct all host defined in the config to the proxy.(80 port and 53 port required.)

More detailed info pls check in Chinese.


## 中文

本程序主要用于解除网易云**等软件**的海外限制问题

目前已测试，在合适的规则下，支持各大热门网站。(对手机APP的支持未测试，因为Android和IOS对PAC的支持比较迷。。)

**为目前网易云唯一解决方案**
**运行本程序的服务器并不需要在中国！**



## How to use ?

只需要找到一个服务器/本机 运行以下命令即可 （需要提前装好docker）*强烈建议部署到VPS，所有设备均可使用*

**更新**

见后面的更新log吧，建议用新的async版，dockerhub以后也只更新asyncio版了

支持dns 工作模式


运行
```dockerfile
docker run -p 80:9090 -p 53:53 -p 53:53/udp -p 9000:9000 -p 9090:9090 -d ljm625/unblock-netease
```

如果因为某些原因导致ip获取错误，（比如**本机没有公网ip**），则请手动指定ip（本机ip即可，大多数情况下127.0.0.1 works fine）

运行：
```dockerfile

docker run -p 80:9090 -p 53:53 -p 53:53/udp -p 9000:9000 -p 9090:9090 -e "IPADDR=127.0.0.1" -d ljm625/unblock-netease
```

之后将设备的dns服务器改为服务器IP或者本机（127.0.0.1），打开网易云稍等片刻，即可享受国区网易云！


**旧版PAC工作模式**


```dockerfile
docker run -p 9000:9000 -p 9090:9090 -d ljm625/unblock-netease
```
如果因为某些原因导致ip获取错误，（比如**本机没有公网ip**），则请手动指定ip（本机ip即可，大多数情况下127.0.0.1 works fine）

运行：
```dockerfile

docker run -p 9000:9000 -p 9090:9090 **-e "IPADDR=127.0.0.1"** -d ljm625/unblock-netease
```

然后设置你的设备pac为 http://你的ip:9000/proxy.pac

Or 将你的网易云设置**http代理**为 你的ip:9090


**此外，还可配合proxifier使用，这样可以不使用DNS以及PAC**


## How it works?
程序主要使用爬虫抓取http代理公布网站，并且对抓取结果进行**测试**，选出最佳的代理，并建立反向代理。

每隔设定的间隔，程序将再次检测代理的存活状态，如果有需要，则会自动替换代理，作为用户，只需要尽情使用即可

对于发给程序的http请求，程序会**判断目标域名是否处于白名单**中，如果处于白名单中，才会使用反向代理，否则会直接通过本地网络进行转发

## Configuration Parameters

所有的设置都在config.yaml文件中

```yaml
proxy_url: 采集代理的proxy网站
proxy_domain:
  - 代理的http请求域名列表
dns_domain:
  - dns劫持的域名列表
candidate_num: 抓取的最多代理数目
validate_url: 验证代理的URL
speedtest_url : 测速的URL
timeout: 验证超时时间（S）
checker_timeout: 二次验证超时时间（S）
check_interval: 检测时间（S），建议至少10分钟,现在如果服务器代理出问题会自动尝试更换其他代理。
# Socket params 一些socket参数，不推荐改动
buffer_size: 4096
delay_time: 0.001
# 这两个参数现在没用了

# Proxy params
proxy_address: 代理IP，一般为0.0.0.0即可
proxy_port: 代理端口设置


dns_enabled : 是否启用DNS服务器
dns_port : DNS服务器端口

# CHANGE THE DNS IF NEEDED
upstream_dns : 上级查询dns

# Disable normal HTTP Proxy
# this is useful if u make a public server on the internet and avoid them to use it as a public HTTP Proxy. (Need to use with PAC or DNS)
disable_proxy : 是否启用白名单外的域名代理，如果使用dns模式，而且在公网服务器使用的话，强烈建议关闭，防止被攻击。
```


## Limitations and Improvements

- https的代理实现仍然在议程之中。

- 目前仅限http代理，比较大的问题是他只能在http上work，如果是其他conn，比如https则会出现问题，下一步是准备实现一个socks5的反代


## Update History
Update 2018/12/26 : 网易云修改了判断逻辑，并封杀了大量代理服务器。目前在实现新的代理站点抓取以及Socks5的支持，Work in Progress

Update 2018/08/08 : 网易云看来判断非常简单，没必要用这么重的解决方案了。推荐使用nginx 加header的方式实现。

Update 2018/08/07 : 最近更新太多。。PAC方法基本已死，没什么用了，推荐dns或者proxifier配合劫持网易云使用，亲测没问题。

集成了伪装dns的代码，用来修改dns代理。

换用python3.6 以及asyncio库重写了代理转发部分，效率大大提升

实现了代理模板，以及增加新的代理抓取服务器（低调！）

嗯，欢迎测试，有问题提issue吧。 Mac & Android测试通过 （我的Android好像是修改版app？）

Update 2017/11/02 : 更新了获取内网IP的方法，并将设定固定ip配置到了环境变量中

Update 2017/11/01 : Update Wiki details

Update 2017/11/01 : Update 了一下具体参数，代理效果更好

## Contributions

欢迎大家进行测试，提出issue，如果有任何问题，也可以发信到ljm625#gmail.com咨询


## TODO

拟实现当当前代理出现问题时，马上切换到之前抓取的备用代理使用，直到新的代理抓取完毕。

# English Version pending