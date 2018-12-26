# Define proxy Profile here.

def get_data_on_profile(profile,soup,number):
    # Define profile here
    # Return a List with ip and port, example: [["127.0.0.1","1080","http"]]
    result=[]

    if profile=='cnproxy':
        proxy_list = soup.select("tbody tr")
        for i in range(0, number):
            try:
                result.append([proxy_list[i].select("td:nth-of-type(1)")[0].text.strip("-").strip(),
                               proxy_list[i].select("td:nth-of-type(2)")[0].text.strip(), 'http'])
            except Exception as e:
                pass
    elif profile=='proxynova':
        proxy_list = soup.select("tbody tr")
        for i in range(0, number):
            try:
                result.append( [proxy_list[i].select("td:nth-of-type(1)")[0].abbr.attrs['title'].strip(),
                                proxy_list[i].select("td:nth-of-type(2)")[0].text.strip(),'http'])
            except:
                pass
    elif profile=='spysone':
        proxy_list = soup.select("tr.spy1x,tr.spy1xx")
        for i in range(0,number):
            proxy_list[i].select("td:nth-of-type(1)")
        print(soup)
    return result