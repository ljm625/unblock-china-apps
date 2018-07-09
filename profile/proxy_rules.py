# Define proxy Profile here.

def get_data_on_profile(profile,data):
    # Define profile here
    # Return a List with ip and port, example: ["127.0.0.1","1080"]
    if profile=='cnproxy':
        return [data.select("td:nth-of-type(1)")[0].text.strip("-").strip(),data.select("td:nth-of-type(2)")[0].text.strip()]
    elif profile=='proxynova':
        return [data.select("td:nth-of-type(1)")[0].abbr.attrs['title'].strip(),data.select("td:nth-of-type(2)")[0].text.strip()]
    else:
        return []
