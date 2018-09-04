var block_urls={{info.block_urls}}
var direct_urls={{info.direct_urls}}
var proxies_str='{%- for item in info.proxies %}PROXY {{item}};{%- endfor %}';
function FindProxyForURL(url, host) {
if (shExpMatch(url,'http://cache.video.qiyi.com/vms*')) return proxies_str;
for(var i in direct_urls){
 var direct_url= direct_urls[i];
if (shExpMatch(url,direct_url)) return 'DIRECT';
 }
for(var i in block_urls){
var block_url=block_urls[i]
 if (shExpMatch(url,block_url)){
return proxies_str;
 }
}
  return 'DIRECT';
}