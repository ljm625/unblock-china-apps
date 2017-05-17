function FindProxyForURL(url,host)
{
    {%- for item in info.proxy_domain %}
    if (host == "{{item}}" || shExpMatch(host, "*{{item}}"))
        return "PROXY {{info.proxy_ip}}:{{info.proxy_port}}";
    {%- endfor %}
    return "DIRECT";
}