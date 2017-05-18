function FindProxyForURL(url,host)
{
    if (url.substring(0, 5) == "http:") {
    {%- for item in info.proxy_domain %}
    if (shExpMatch(host, "(*.{{item}}|{{item}})"))
        return "PROXY {{info.proxy_ip}}:{{info.proxy_port}}; DIRECT";
    {%- endfor %}
    }
    return "DIRECT";
}