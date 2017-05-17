# 解除网易云音乐海外限制
docker run -p 9000:9000 -p 9090:9090 -m 256m -d ljm625/unblock-netease

然后设置你的设备pac为 http://你的ip:9000/proxy.pac 即可

这个PAC只会代理网易..可以自己修改config.yaml更改匹配规则&PAC生成规则

文档施工中..
