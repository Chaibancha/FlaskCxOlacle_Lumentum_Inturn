import requests

url = "http://10.103.66.42:5006/redirect_user?res=TH1E710263L.li.lumentuminc.net"

response = requests.get(url)

if response.status_code == 200:
    content = response.content

    print(content)
else:
    print("can't connect")

