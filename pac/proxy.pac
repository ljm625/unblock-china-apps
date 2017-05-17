function FindProxyForURL(url,host)
{
    if (host == "126.com" || shExpMatch(host, "*126.com"))
        return "PROXY 127.0.0.1:9090";
    if (host == "163.com" || shExpMatch(host, "*163.com"))
        return "PROXY 127.0.0.1:9090";
    return "DIRECT";
}