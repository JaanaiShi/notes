try:
    headers = {"Accept": "application/vnd.github.v3+json, application/json", "Authorization": token, "Content-Type": "application/json"}
    url = "https://api.github.com/repos/JaanaiShi/notes/pulls"
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    ret = response.text
    print(ret)
except Exception as e:
    print(e)
finally:
    return ret