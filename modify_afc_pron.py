import difflib
import json
import subprocess
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# InsecureRequestWarning 경고 메시지 비활성화
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# JSON 파일 불러오기
with open('/home/jinwoo/serverlist.json', 'r') as file:
    data = json.load(file)

# 함수 정의: 서버에서 정보 추출
def extract_info(server):
    region = server['name'].split('/')[0].strip()
    info_dict = {item['name'][0]: {'server_name': item['name'], 'public_ip': item['info']['public_ip'], 'port': item['info']['port'], 'user': item['info']['user'], 'passwd': item['info']['passwd']} for item in server['item']}
    return region, info_dict

# 함수 정의: 내부 파일 비교
def compare_internal_files(old_info, new_info, file_path):
    old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path}"
    new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path}"

    # 디버깅 정보 출력
#    print(f"Old SSH Command for {file_path}:", old_ssh_command)
#    print(f"New SSH Command for {file_path}:", new_ssh_command)

    try:
        # SSH로 내부 파일 내용 가져오기
        old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
        new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

        # 진행 중인 작업을 출력
        print("------------------------------------------------------------")
        print(f"내부 파일 '{file_path}' 비교 중...")

        # 파일 내용 비교
        if old_result.strip() == new_result.strip():
           return f"파일 '{file_path}'이(가) 동일합니다. 서로 파일 내용이 같습니다."
        else:
            return f"파일 '{file_path}'이(가) 다릅니다.\n\nOld Server:\n{old_result}\n\nNew Server:\n{new_result}"

        # 파일 내용 비교
        differ = difflib.Differ()
        diff_result = list(differ.compare(old_result.splitlines(), new_result.splitlines()))

        # 변경된 부분만 출력
        print('\n'.join(line for line in diff_result if line.startswith('- ') or line.startswith('+ ')))


    except subprocess.CalledProcessError as e:
        print(f"Error occurred while comparing {file_path}: {e}")
        return None



# 함수 정의: 외부 명령어 실행
def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{command}': {e}")
        return None

# 사용자로부터 서버 이름 입력 받기
user_input_1 = input("공용 리전의 이름을 입력하세요[ex) seo]: ").lower()
user_input_2 = input("신규 리전의 이름을 입력하세요[ex) lgw]: ").lower()

# 입력받은 서버 이름과 매칭되는 서버만 가져오기
all_servers = []
for server_key in data:
    if isinstance(data[server_key], dict) and 'server_list' in data[server_key]:
        all_servers.extend(data[server_key]['server_list'])

# 서버 이름이 포함되어 있는 경우만 선택
selected_servers_1 = [server for server in all_servers if user_input_1 in server['name'].lower()]
selected_servers_2 = [server for server in all_servers if user_input_2 in server['name'].lower()]

# 서버가 선택되지 않았을 경우 에러 출력 후 종료
if not selected_servers_1:
    print(f"Error: {user_input_1}에 해당하는 서버가 없습니다.")
    sys.exit(1)

if not selected_servers_2:
    print(f"Error: {user_input_2}에 해당하는 서버가 없습니다.")
    sys.exit(1)

# 서버이름이 여러개일 경우 사용자에게 선택하도록 함
if len(selected_servers_1) > 1:
    print("\n공용 리전을 다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_1, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("번호를 입력하세요: "))
    selected_servers_1 = [selected_servers_1[selected_index - 1]]

if len(selected_servers_2) > 1:
    print("\n신규 리전을 다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_2, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("번호를 입력하세요: "))
    selected_servers_2 = [selected_servers_2[selected_index - 1]]

# 사용자로부터 비교할 파일 목록 입력 받기
file_paths = [
#    '/etc/resolv.conf | grep nameserver',
#    '/etc/nginx/sites-enabled/ssl_config',
#    '/etc/nginx/sites-enabled/default.conf', 
#    '/etc/nginx/sites-enabled/error_config', 
#    '/etc/nginx/sites-enabled/letsencrypt_config',
#    '/etc/nginx/fastcgi_params',
#    '/etc/nginx/mime.types',
#    '/etc/nginx/nginx.conf'
    '/etc/resolv.conf | grep nameserver | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"',
    '/etc/nginx/sites-enabled/ssl_config | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"',
    '/etc/nginx/sites-enabled/default.conf | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"', 
    '/etc/nginx/sites-enabled/error_config | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"', 
    '/etc/nginx/sites-enabled/letsencrypt_config | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"',
    '/etc/nginx/fastcgi_params | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"',
    '/etc/nginx/mime.types | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"',
    '/etc/nginx/nginx.conf | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"'
    # 추가하고 싶은 내부 파일 경로들을 계속 추가하세요
]

# 외부 명령어 목록 입력
commands = [
    'ls -al /etc/nginx/letsencrypt_cf',
    'openssl version',
    'php -version',
    'ulimit -a',
    '/etc/nginx/sbin/nginx -v',
#    'ifconfig | grep -i mtu  | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"'
    'ifconfig | grep -i mtu | head -1 | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"'
#    'ifconfig | grep mtu | awk "{{print $4}}"'
#    'cat /etc/nginx/sites-enabled/ssl_config | egrep -v "^[[:space:]]*(#.*)?$"'
#   'cat /etc/nginx/sites-enabled/ssl_config | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"'
]

# 변수 초기화
OLD_region, OLD_info = extract_info(selected_servers_1[0])
NEW_region, NEW_info = extract_info(selected_servers_2[0])

# 디버깅 정보 출력
#print("Old Server Info:", OLD_region, OLD_info)
#print("New Server Info:", NEW_region, NEW_info)

# 비교할 인스턴스 번호 선택
print("\n비교할 인스턴스 번호를 선택해주세요:")
print("1. AFC  2. WAF  3. PRON")
#print("2. WAF")
#print("3. PRON")

selected_instance = input("번호를 입력하세요: ")

# 선택된 인스턴스 번호에 따라 출력
if selected_instance == '1':
    print("\nAFC 비교 결과:")
#    print("첫 번째 서버 정보:")
#    print("OLD_AFC_name:", OLD_region)
#    print("OLD_AFC_name:", OLD_info.get('A', {}).get('name'))
#    print("OLD_AFC_public_ip:", OLD_info.get('A', {}).get('public_ip'))
#    print("OLD_AFC_port:", OLD_info.get('A', {}).get('port'))
#    print("OLD_AFC_user:", OLD_info.get('A', {}).get('user'))
#    print("OLD_AFC_passwd:", OLD_info.get('A', {}).get('passwd'))

#    print("\n두 번째 서버 정보:")
#    print("NEW_AFC_name:", NEW_region)
#    print("NEW_AFC_public_ip:", NEW_info.get('A', {}).get('public_ip'))
#    print("NEW_AFC_port:", NEW_info.get('A', {}).get('port'))
#    print("NEW_AFC_user:", NEW_info.get('A', {}).get('user'))
#    print("NEW_AFC_passwd:", NEW_info.get('A', {}).get('passwd'))

    # 내부 파일 비교
    for file_path in file_paths:
        internal_diff_result = compare_internal_files(OLD_info.get('A', {}), NEW_info.get('A', {}), file_path)
        # 비교 결과 출력
        print("------------------------------------------------------------")
        print(f"\n내부 파일 비교 결과 for {file_path}:")
        if internal_diff_result is not None:
            print(internal_diff_result)
        else:
            print(f"내부 파일 비교 중 오류가 발생했습니다. {file_path}")

    # 외부 명령어 실행 및 결과 비교
    for command in commands:
        print("------------------------------------------------------------")
        print(f"\n외부 명령어 실행 결과 for {command}:")
        old_command_result = run_command(f"sshpass -p {OLD_info['A']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {OLD_info['A']['port']} {OLD_info['A']['user']}@{OLD_info['A']['public_ip']} {command}")
        new_command_result = run_command(f"sshpass -p {NEW_info['A']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {NEW_info['A']['port']} {NEW_info['A']['user']}@{NEW_info['A']['public_ip']} {command}")

        # 결과 비교
        if old_command_result is not None and new_command_result is not None:
            if old_command_result.strip() == new_command_result.strip():
                print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
            else:
                print(f"{command} 명령어의 결과가 다릅니다.")
                print(f"\nOld Server 결과:\n{old_command_result}\n\nNew Server 결과:\n{new_command_result}")
#                print("------------------------------------------------------------")
        else:
            print(f"{command} 명령어 실행 중 오류가 발생했습니다.")

# '2'와 '3'에 대한 비교 로직을 추가하세요.
elif selected_instance == '2':
    # 첫 번째 서버에 대한 POST 요청으로 Set-Cookie 값 가져오기
    post_url_old = f"https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/auth"
    post_data_old = {'id': 'ebizdev', 'password': 'dlqlwm!23'}
    response_post_old = requests.post(post_url_old, data=post_data_old, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)

    # Set-Cookie 값 추출
    wp_sessid_cookie_old = response_post_old.cookies.get("WP_SESSID")
    if wp_sessid_cookie_old:
#        print(f"첫 번째 서버 Set-Cookie 값: {wp_sessid_cookie_old}")

        # 첫 번째 서버 버전 확인
        version_check_command_old = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_old}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/info/version | jq -r '.wapples | split(\".\") | .[0]'"
        version_check_result_old = run_command(version_check_command_old)
#        print(f"첫 번째 서버 버전 확인 결과: {version_check_result_old}")

        # 버전이 6 이상인 경우에만 GET 요청 보내기
        if version_check_result_old is not None and int(version_check_result_old.strip()) >= 6:
            # 각 서버에 대한 GET 요청 보내기
            get_command_old = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_old}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/conf/rule | jq 'map(select((.rule_name == \"LDAP Injection\" or .rule_name == \"NoSQL Injection\" or .rule_name == \"XPath Injection\" or .rule_name == \"Cross Site Request Forgery\" or .rule_name == \"Content Spoofing\") and (.policy_name == \"Japan_trial_policy\" or .policy_name == \"Japan_common_policy\") and .level != 0)) | .[] | {{rule_name: .rule_name, level: .level, policy_name: .policy_name}}'"
            get_response_old = run_command(get_command_old)

            # 중간 결과물 출력
#            print("\n첫 번째 서버 GET 요청 결과:")
            print(f"\n{OLD_info.get('W', {}).get('server_name')} 룰 탐지모드 확인 결과:")
            print(get_response_old)
        else:
            print(f"\n{OLD_info.get('W', {}).get('server_name')}은 6버전이 아닙니다")

    # 두 번째 서버에 대한 POST 요청으로 Set-Cookie 값 가져오기
    post_url_new = f"https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/auth"
    post_data_new = {'id': 'ebizdev', 'password': 'dlqlwm!23'}
    response_post_new = requests.post(post_url_new, data=post_data_new, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)

    # Set-Cookie 값 추출
    wp_sessid_cookie_new = response_post_new.cookies.get("WP_SESSID")
    if wp_sessid_cookie_new:
#        print(f"두 번째 서버 Set-Cookie 값: {wp_sessid_cookie_new}")

        # 두 번째 서버 버전 확인
        version_check_command_new = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_new}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/info/version | jq -r '.wapples | split(\".\") | .[0]'"
        version_check_result_new = run_command(version_check_command_new)
#        print(f"두 번째 서버 버전 확인 결과: {version_check_result_new}")

        # 버전이 6 이상인 경우에만 GET 요청 보내기
        if version_check_result_new is not None and int(version_check_result_new.strip()) >= 6:
            # 각 서버에 대한 GET 요청 보내기
            get_command_new = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_new}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/conf/rule | jq 'map(select((.rule_name == \"LDAP Injection\" or .rule_name == \"NoSQL Injection\" or .rule_name == \"XPath Injection\" or .rule_name == \"Cross Site Request Forgery\" or .rule_name == \"Content Spoofing\") and (.policy_name == \"Japan_trial_policy\" or .policy_name == \"Japan_common_policy\") and .level != 0)) | .[] | {{rule_name: .rule_name, policy_name: .policy_name}}'"
            get_response_new = run_command(get_command_new)

            # 중간 결과물 출력
            print(f"\n{NEW_info.get('W', {}).get('server_name')} 룰 탐지 & 차단모드로 동작중인 정책들 확인 결과:")
            print(get_response_new)
        else:
            print(f"\n{NEW_info.get('W', {}).get('server_name')}은 6버전이 아닙니다")

            # 결과 출력
#            print(f"\nWAF 비교 결과 for {NEW_info.get('W', {}).get('public_ip')}:")
#            if get_response_new:
#                print(get_response_new)
#            else:
#                print("두 번째 서버 GET 요청 중 오류가 발생했습니다.")
#        else:
#            print("두 번째 서버의 버전이 6 미만이므로 GET 요청을 보낼 수 없습니다.")
#    else:
#        print("두 번째 서버의 POST 요청 중 오류가 발생했습니다.")


elif selected_instance == '3':
    print("\nPRON 비교 결과:")
    print("첫 번째 서버 정보:")
    print("OLD_PRON_name:", OLD_region)
    print("OLD_PRON_public_ip:", OLD_info.get('P', {}).get('public_ip'))
    print("OLD_PRON_port:", OLD_info.get('P', {}).get('port'))
    print("OLD_PRON_user:", OLD_info.get('P', {}).get('user'))
    print("OLD_PRON_passwd:", OLD_info.get('P', {}).get('passwd'))

    print("\n두 번째 서버 정보:")
    print("NEW_PRON_name:", NEW_region)
    print("NEW_PRON_public_ip:", NEW_info.get('P', {}).get('public_ip'))
    print("NEW_PRON_port:", NEW_info.get('P', {}).get('port'))
    print("NEW_PRON_user:", NEW_info.get('P', {}).get('user'))
    print("NEW_PRON_passwd:", NEW_info.get('P', {}).get('passwd'))

    # 내부 파일 비교
    for file_path in file_paths:
        internal_diff_result = compare_internal_files(OLD_info.get('P', {}), NEW_info.get('P', {}), file_path)
        # 비교 결과 출력
        print("------------------------------------------------------------")
        print(f"\n내부 파일 비교 결과 for {file_path}:")
        if internal_diff_result is not None:
            print(internal_diff_result)
        else:
            print(f"내부 파일 비교 중 오류가 발생했습니다. {file_path}")

    # 외부 명령어 실행 및 결과 비교
    for command in commands:
        print("------------------------------------------------------------")
        print(f"\n외부 명령어 실행 결과 for {command}:")
        old_command_result = run_command(f"sshpass -p {OLD_info['P']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {OLD_info['P']['port']} {OLD_info['P']['user']}@{OLD_info['P']['public_ip']} {command}")
        new_command_result = run_command(f"sshpass -p {NEW_info['P']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {NEW_info['P']['port']} {NEW_info['P']['user']}@{NEW_info['P']['public_ip']} {command}")

        # 결과 비교
        if old_command_result is not None and new_command_result is not None:
            if old_command_result.strip() == new_command_result.strip():
                print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
            else:
                print(f"{command} 명령어의 결과가 다릅니다.")
                print(f"\nOld Server 결과:\n{old_command_result}\n\nNew Server 결과:\n{new_command_result}")
        else:
            print(f"{command} 명령어 실행 중 오류가 발생했습니다.")

else:
    print("다시 입력해주세요.")
