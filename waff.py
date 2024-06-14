import requests
import urllib3
import json

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read IP addresses and names from serverlist.json where name starts with "W"
with open("serverlist.json", "r") as json_file:
    server_list = json.load(json_file)

# Filter servers with names starting with "W" and extract IP and name
filtered_servers = [(server["info"]["public_ip"], server["name"]) for server in server_list if server["name"].startswith("W")]

# Fixed parts of the URL
base_url = "https://"
port = ":443"
endpoint_auth = "/webapi/auth"
endpoint_cdn = "/webapi/conf/users"

headers_post = {
    "Content-Type": "application/x-www-form-urlencoded",
}

for ip_address, name in filtered_servers:
    # Make a POST request to obtain the WP_SESSID cookie for each IP address
    post_data = {
        "id": "ebizdev",
        "password": "dlqlwm!23"
    }

    response_post = requests.post(f"{base_url}{ip_address}{port}{endpoint_auth}", headers=headers_post, data=post_data, verify=False)

    if response_post.status_code == 200:
        wp_sessid_cookie = response_post.cookies.get("WP_SESSID")
        if wp_sessid_cookie:
            cookies = {
                "WP_SESSID": wp_sessid_cookie
            }

            # Make a GET request using the obtained WP_SESSID cookie
            url = f"{base_url}{ip_address}{port}{endpoint_cdn}"
            response = requests.get(url, headers=headers_post, cookies=cookies, verify=False)

            if response.status_code == 200:
                data = response.json()
                usernames = [user["username"] for user in data]
                print(f"Name: {name}, IP Address: {ip_address}, Usernames: {usernames}")
            else:
                print(f"Request to {ip_address} failed with status code:", response.status_code)
        else:
            print(f"WP_SESSID cookie not found for {ip_address}.")
    else:
        print(f"POST request to {ip_address} failed with status code:", response_post.status_code)

