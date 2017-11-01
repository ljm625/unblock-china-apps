# 解除网易云音乐海外限制
docker run -p 9000:9000 -p 9090:9090 -m 256m -d ljm625/unblock-netease

然后设置你的设备pac为 http://你的ip:9000/proxy.pac 即可

这个PAC只会代理网易..可以自己修改config.yaml更改匹配规则&PAC生成规则

软件分为2部分，一个为pac的host，一个是http代理，如果你不需要pac的话，请直接http代理到9090端口

文档施工中..

Update 2017/11/01 : 只是Update一下，刚刚测试了目前还是存活状态，但是mac的Pac可能有点问题，not sure why，mac可以用proxifier暂时解决一下，选择HTTP代理，端口9090
