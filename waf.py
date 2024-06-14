import requests
import urllib3

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of IP addresses to send requests to
ip_addresses = [
    "139.162.113.147",
    "139.162.112.161",
    # Add more IP addresses here
]

# Fixed parts of the URL
base_url = "https://"
port = ":443"
endpoint_auth = "/webapi/auth"
endpoint_cdn = "/webapi/conf/users"

headers_post = {
    "Content-Type": "application/x-www-form-urlencoded",
}

for ip_address in ip_addresses:
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
                print(f"Usernames for {ip_address}: {usernames}")
            else:
                print(f"Request to {ip_address} failed with status code:", response.status_code)
        else:
            print(f"WP_SESSID cookie not found for {ip_address}.")
    else:
        print(f"POST request to {ip_address} failed with status code:", response_post.status_code)

