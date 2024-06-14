import requests
import urllib3
import json

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read IP addresses and names from serverlist.json where name starts with "W"
with open("serverlist.json", "r") as json_file:
    data = json.load(json_file)

filtered_servers = []

for group_key, group_data in data.items():
    if "server_list" in group_data:
        for server_group in group_data["server_list"]:
            for server in server_group["item"]:
                if server["name"].startswith("W"):
                    name = server["name"]
                    public_ip = server["info"]["public_ip"]
                    filtered_servers.append((name, public_ip))

# Fixed parts of the URL
base_url = "https://"
port = ":443"
endpoint_auth = "/webapi/auth"
endpoint_users = "/webapi/conf/users"

headers_post = {
    "Content-Type": "application/x-www-form-urlencoded",
}

for name, ip_address in filtered_servers:
    try:
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
                url = f"{base_url}{ip_address}{port}{endpoint_users}"
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
    except Exception as e:
        print(f"An error occurred for {ip_address}: {str(e)}. Skipping...")
        continue  # Skip to the next server if an error occurs
