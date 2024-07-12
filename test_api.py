import requests

def callAPI(url,data):
    r=requests.post(url,json=data)
    return r.text

if __name__=="__main__":
    baseurl="http://0.0.0.0:8000"
    data={
        "user": "XXX",
        "pw": "SSS",
    }
    r=callAPI(f"{baseurl}/api/v1/setuser",data)
    #r=callAPI(f"{baseurl}/api/v1/deluser",data)

    print(r)