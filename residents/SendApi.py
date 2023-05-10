import requests
import json
def send_api(API_HOST, path, method, headers, body):
    url = API_HOST + path
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)

        elif method == "POST":
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False).encode("utf8"),
            )

        elif method == "DELETE":
            response = requests.delete(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False).encode("utf8"),
            )
        elif method == "PUT":
            response = requests.put(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False).encode("utf8"),
            )

    except Exception as ex:
        print(ex)
