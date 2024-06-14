import difflib
import json
import subprocess
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

with open('/home/jinwoo/serverlist.json', 'r') as file:
    data = json.load(file)

def extract_info(server):
    region = server['name'].split('/')[0].strip()
    info_dict = {item['name'][0]: {'server_name': item['name'], 'public_ip': item['info']['public_ip'], 'port': item['info']['port'], 'user': item['info']['user'], 'passwd': item['info']['passwd']} for item in server['item']}
    return region, info_dict

def compare_internal_files(old_info, new_info, file_path):
    old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path} | egrep -v \"^[[:space:]]*(#.*)?$\" | sed \"s/^[[:space:]]*//\""
    new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path} | egrep -v \"^[[:space:]]*(#.*)?$\" | sed \"s/^[[:space:]]*//\""


    try:
        old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
        new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

        print(f"\n------------'{file_path}' 비교 중------------")

        if old_result.strip() == new_result.strip():
            print(f"\n파일 '{file_path}'이(가) 동일합니다. 서로 파일 내용이 같습니다.")
            print("-------------------------------------------------------------------")
        else:
            print(f"\n파일 '{file_path}'이(가) 다릅니다.")

            differ = difflib.Differ()
            diff_result = list(differ.compare(old_result.splitlines(), new_result.splitlines()))

            changed_lines = [line for line in diff_result if line.startswith('- ') or line.startswith('+ ')]
            
            if changed_lines:
                print(f"\n{OLD_info.get('A', {}).get('server_name')}:")

                for line in changed_lines:
                    if line.startswith('- '):
                        print(f"{line[2:]}")
                
                print(f"\n{NEW_info.get('A', {}).get('server_name')}")
                for line in changed_lines:
                    if line.startswith('+ '):
                        print(f"{line[2:]}")
            else:
                print("변경된 내용이 없습니다.")
                
            print("-----------------------------------------------------------------")



    except subprocess.CalledProcessError as e:
        print(f"Error occurred while comparing {file_path}: {e}")
        return None


def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{command}': {e}")
        return None

user_input_1 = input("공용 리전의 이름을 입력하세요[ex) seo]: ").lower()
user_input_2 = input("신규 리전의 이름을 입력하세요[ex) lgw]: ").lower()

all_servers = []
for server_key in data:
    if isinstance(data[server_key], dict) and 'server_list' in data[server_key]:
        all_servers.extend(data[server_key]['server_list'])

selected_servers_1 = [server for server in all_servers if user_input_1 in server['name'].lower()]
selected_servers_2 = [server for server in all_servers if user_input_2 in server['name'].lower()]

if not selected_servers_1:
    print(f"Error: {user_input_1}에 해당하는 서버가 없습니다.")
    sys.exit(1)

if not selected_servers_2:
    print(f"Error: {user_input_2}에 해당하는 서버가 없습니다.")
    sys.exit(1)

if len(selected_servers_1) > 1:
    print("\n공용 리전을 다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_1, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("\n번호를 입력하세요: "))
    selected_servers_1 = [selected_servers_1[selected_index - 1]]

if len(selected_servers_2) > 1:
    print("\n신규 리전을 다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_2, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("\n번호를 입력하세요: "))
    selected_servers_2 = [selected_servers_2[selected_index - 1]]


file_paths = [
    '/etc/resolv.conf | grep nameserver',
    '/etc/nginx/sites-enabled/ssl_config',
    '/etc/nginx/sites-enabled/default.conf', 
    '/etc/nginx/sites-enabled/error_config', 
    '/etc/nginx/sites-enabled/letsencrypt_config',
    '/etc/nginx/fastcgi_params',
    '/etc/nginx/nginx.conf'
]

commands = [
    'ls -al /etc/nginx/letsencrypt_cf | tail -n +4',
    'openssl version',
    'php -version',
    'ulimit -a',
    '/etc/nginx/sbin/nginx -v',
    'ifconfig | grep -i mtu | head -1 | egrep -v "^[[:space:]]*(#.*)?$" | sed "s/^[[:space:]]*//"'
]


OLD_region, OLD_info = extract_info(selected_servers_1[0])
NEW_region, NEW_info = extract_info(selected_servers_2[0])


print("\n비교할 인스턴스 번호를 선택해주세요:")
print("1. AFC  2. WAF  3. PRON")

selected_instance = input("\n번호를 입력하세요: ")


if selected_instance == '1':
    print("\nAFC 비교 결과:\n")


    for file_path in file_paths:
        internal_diff_result = compare_internal_files(OLD_info.get('A', {}), NEW_info.get('A', {}), file_path)

        if internal_diff_result is not None:
            print(internal_diff_result)


    for command in commands:
        print(f"\n--------------------'{command}' 비교 중--------------------")
        old_command_result = run_command(f"sshpass -p {OLD_info['A']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {OLD_info['A']['port']} {OLD_info['A']['user']}@{OLD_info['A']['public_ip']} {command}")
        new_command_result = run_command(f"sshpass -p {NEW_info['A']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {NEW_info['A']['port']} {NEW_info['A']['user']}@{NEW_info['A']['public_ip']} {command}")


        if old_command_result is not None and new_command_result is not None:
            if old_command_result.strip() == new_command_result.strip():
                print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
                print("-------------------------------------------------------------------")
            else:
                print(f"\n{command} 명령어의 결과가 다릅니다.\n")
                differ = difflib.Differ()
                diff_result = list(differ.compare(old_command_result.splitlines(), new_command_result.splitlines()))


                changed_lines = [line for line in diff_result if line.startswith('- ') or line.startswith('+ ')]
                
                if changed_lines:
                    print(f"\n{OLD_info.get('A', {}).get('server_name')}:")
                    for line in changed_lines:
                        if line.startswith('- '):
                            print(f"{line[2:]}")
                    
                    print(f"\n{NEW_info.get('A', {}).get('server_name')}")
                    for line in changed_lines:
                        if line.startswith('+ '):
                            print(f"{line[2:]}")
                else:
                    print("변경된 내용이 없습니다.")
                    
                print("-----------------------------------------------------------------")
        else:
            print(f"{command} 명령어 실행 중 오류가 발생했습니다.")

elif selected_instance == '2':
    post_url_old = f"https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/auth"
    post_data_old = {'id': 'ebizdev', 'password': 'dlqlwm!23'}
    response_post_old = requests.post(post_url_old, data=post_data_old, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)

    wp_sessid_cookie_old = response_post_old.cookies.get("WP_SESSID")
    if wp_sessid_cookie_old:

        version_check_command_old = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_old}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/info/version | jq -r '.wapples | split(\".\") | .[0]'"
        version_check_result_old = run_command(version_check_command_old)


        if version_check_result_old is not None and int(version_check_result_old.strip()) >= 6:

            get_command_old = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_old}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{OLD_info.get('W', {}).get('public_ip')}:443/webapi/conf/rule | jq 'map(select((.rule_name == \"LDAP Injection\" or .rule_name == \"NoSQL Injection\" or .rule_name == \"XPath Injection\" or .rule_name == \"Cross Site Request Forgery\" or .rule_name == \"Content Spoofing\") and (.policy_name == \"Japan_trial_policy\" or .policy_name == \"Japan_common_policy\") and .level != 0)) | .[] | {{rule_name: .rule_name, policy_name: .policy_name}}'"
            get_response_old = run_command(get_command_old)

            print(f"\n{OLD_info.get('W', {}).get('server_name')} 룰 탐지모드 확인 결과:")
            print(get_response_old)
        else:
            print(f"\n{OLD_info.get('W', {}).get('server_name')}은 6버전이 아닙니다")


    post_url_new = f"https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/auth"
    post_data_new = {'id': 'ebizdev', 'password': 'dlqlwm!23'}
    response_post_new = requests.post(post_url_new, data=post_data_new, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)


    wp_sessid_cookie_new = response_post_new.cookies.get("WP_SESSID")
    if wp_sessid_cookie_new:

        version_check_command_new = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_new}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/info/version | jq -r '.wapples | split(\".\") | .[0]'"
        version_check_result_new = run_command(version_check_command_new)

        if version_check_result_new is not None and int(version_check_result_new.strip()) >= 6:

            get_command_new = f"curl --insecure -b 'WP_SESSID={wp_sessid_cookie_new}' -H 'Content-Type:application/x-www-form-urlencoded' -s GET https://{NEW_info.get('W', {}).get('public_ip')}:443/webapi/conf/rule | jq 'map(select((.rule_name == \"LDAP Injection\" or .rule_name == \"NoSQL Injection\" or .rule_name == \"XPath Injection\" or .rule_name == \"Cross Site Request Forgery\" or .rule_name == \"Content Spoofing\") and (.policy_name == \"Japan_trial_policy\" or .policy_name == \"Japan_common_policy\") and .level != 0)) | .[] | {{rule_name: .rule_name, policy_name: .policy_name}}'"
            get_response_new = run_command(get_command_new)

            print(f"\n{NEW_info.get('W', {}).get('server_name')} 룰 탐지 & 차단모드로 동작중인 정책들 확인 결과:")
            print(get_response_new)
        else:
            print(f"\n{NEW_info.get('W', {}).get('server_name')}은 6버전이 아닙니다")


elif selected_instance == '3':
    print("\nPRON 비교 결과:\n")

    for file_path in file_paths:
        internal_diff_result = compare_internal_files(OLD_info.get('P', {}), NEW_info.get('P', {}), file_path)
        if internal_diff_result is not None:
            print(internal_diff_result)

    for command in commands:
        print(f"\n--------------------'{command}' 비교 중--------------------")
        
        try:
            old_command_result = run_command(f"sshpass -p {OLD_info['P']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {OLD_info['P']['port']} {OLD_info['P']['user']}@{OLD_info['P']['public_ip']} {command}")
            new_command_result = run_command(f"sshpass -p {NEW_info['P']['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {NEW_info['P']['port']} {NEW_info['P']['user']}@{NEW_info['P']['public_ip']} {command}")

            if old_command_result is not None and new_command_result is not None:
                if old_command_result.strip() == new_command_result.strip():
                    print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
                    print("-------------------------------------------------------------------")
                else:
                    print(f"\n{command} 명령어의 결과가 다릅니다.\n")
                    differ = difflib.Differ()
                    diff_result = list(differ.compare(old_command_result.splitlines(), new_command_result.splitlines()))

                    changed_lines = [line for line in diff_result if line.startswith('- ') or line.startswith('+ ')]
                    
                    if changed_lines:
                        print(f"\n{OLD_info.get('P', {}).get('server_name')}:")
                        for line in changed_lines:
                            if line.startswith('- '):
                                print(f"{line[2:]}")
                        
                        print(f"\n{NEW_info.get('P', {}).get('server_name')}")
                        for line in changed_lines:
                            if line.startswith('+ '):
                                print(f"{line[2:]}")
                    else:
                        print("변경된 내용이 없습니다.")
                        
                    print("-----------------------------------------------------------------")
            else:
                print(f"{command} 명령어 실행 중 오류가 발생했습니다.")

        except subprocess.CalledProcessError as e:
            # "No such file or directory" 에러 발생 시 무시하고 계속 진행
            if "No such file or directory" not in str(e):
                print(f"{command} 명령어 실행 중 오류가 발생했습니다: {e}")


else:
    print("다시 입력해주세요.")
