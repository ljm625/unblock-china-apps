# Define proxy Profile here.

# def get_data_on_profile(profile,soup,number):
#     # Define profile here
#     # Return a List with ip and port, example: [["127.0.0.1","1080","http"]]
#     result=[]
#
#     if profile=='cnproxy':
#         proxy_list = soup.select("tbody tr")
#         for i in range(0, number):
#             try:
#                 result.append([proxy_list[i].select("td:nth-of-type(1)")[0].text.strip("-").strip(),
#                                proxy_list[i].select("td:nth-of-type(2)")[0].text.strip(), 'http'])
#             except Exception as e:
#                 pass
#     elif profile=='proxynova':
#         proxy_list = soup.select("tbody tr")
#         for i in range(0, number):
#             try:
#                 result.append( [proxy_list[i].select("td:nth-of-type(1)")[0].abbr.attrs['title'].strip(),
#                                 proxy_list[i].select("td:nth-of-type(2)")[0].text.strip(),'http'])
#             except:
#                 pass
#     elif profile=='spysone':
#
#         proxy_list = soup.select("tr.spy1x,tr.spy1xx")
#         for i in range(0,number):
#             proxy_list[i].select("td:nth-of-type(1)")
#         print(soup)
#     return result


def get_data_on_profile(profile,driver,number):
    # Define profile here
    # Return a List with ip and port, example: [["127.0.0.1","1080","http"]]
    result=[]

    if profile=='cnproxy':
        proxy_list = driver.find_elements_by_css_selector("tbody tr")
        for i in range(0, number):
            try:
                result.append([proxy_list[i].find_elements_by_css_selector("td:nth-of-type(1)")[0].text.strip("-").strip(),
                               proxy_list[i].find_elements_by_css_selector("td:nth-of-type(2)")[0].text.strip(), 'HTTP'])
            except Exception as e:
                pass
    elif profile=='proxynova':
        proxy_list = driver.find_elements_by_css_selector("tbody tr")
        for i in range(0, number):
            try:
                result.append( [proxy_list[i].find_elements_by_css_selector("td:nth-of-type(1)")[0].text.strip(),
                                proxy_list[i].find_elements_by_css_selector("td:nth-of-type(2)")[0].text.strip(),'HTTP'])
            except:
                pass
    elif profile=='spysone':

        proxy_list = driver.find_elements_by_css_selector("tr.spy1x,tr.spy1xx")
        if len(proxy_list)<number+2:
            number = len(proxy_list)-2
        for i in range(2,number+2):
            proxy_info = proxy_list[i].text.strip().split(" ")
            result.append([proxy_info[1].split(":")[0],proxy_info[1].split(":")[1],proxy_info[2]])
        print(driver)

    elif profile=='gatherproxy':

        proxy_list = driver.find_elements_by_css_selector("tr")
        if len(proxy_list)<number+2:
            number = len(proxy_list)-2
        for i in range(2,number+2):
            proxy_info = proxy_list[i].text.strip().split(" ")
            result.append([proxy_info[3],proxy_info[4],"SOCKS5"])
        print(driver)

    return result