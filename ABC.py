import difflib
import json
import subprocess
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# JSON 파일에서 데이터 읽기
with open('/home/jinwoo/serverlist.json', 'r') as file:
    data = json.load(file)

# 서버 정보 추출 함수
def extract_info(server):
    region = server['name'].split('/')[0].strip()
    info_dict = {
        item['name'][0]: {
            'server_name': item['name'],
            'public_ip': item['info']['public_ip'],
            'port': item['info']['port'],
            'user': item['info']['user'],
            'passwd': item['info']['passwd']
        } for item in server['item']
    }
    return region, info_dict

# 내부 파일 비교 함수
def compare_internal_files(old_info, new_info, file_path):
    old_ssh_command = create_ssh_command(old_info, file_path)
    new_ssh_command = create_ssh_command(new_info, file_path)

    try:
        old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
        new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

        print(f"\n------------'{file_path}' 비교 중------------")

        if old_result.strip() == new_result.strip():
            print(f"\n파일 '{file_path}'이(가) 동일합니다. 서로 파일 내용이 같습니다.")
        else:
            print(f"\n파일 '{file_path}'이(가) 다릅니다.")
            print_diff(old_info, new_info, old_result, new_result)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while comparing {file_path}: {e}")

# SSH 명령어 생성 함수
def create_ssh_command(info, file_path):
    return f"sshpass -p {info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {info['port']} {info['user']}@{info['public_ip']} cat {file_path} | egrep -v \"^[[:space:]]*(#.*)?$\" | sed \"s/^[[:space:]]*//\""

# 명령어 실행 함수
def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{command}': {e}")
        return None

# 서버 선택 함수
def select_server(user_input, servers):
    selected_servers = [server for server in servers if user_input in server['name'].lower()]

    if not selected_servers:
        print(f"Error: {user_input}에 해당하는 서버가 없습니다.")
        sys.exit(1)

    if len(selected_servers) > 1:
        print(f"\n{user_input}을(를) 다음 중 하나로 선택해주세요:")
        for i, server in enumerate(selected_servers, start=1):
            print(f"{i}. {server['name']}")

        selected_index = int(input("\n번호를 입력하세요: "))
        return [selected_servers[selected_index - 1]]
    else:
        return selected_servers

# 인스턴스 비교 함수
def compare_instance(old_info, new_info, file_paths, commands):
    OLD_region, OLD_info = extract_info(old_info)
    NEW_region, NEW_info = extract_info(new_info)

    print("\n비교할 인스턴스 번호를 선택해주세요:")
    print("1. AFC  2. WAF  3. PRON")

    selected_instance = input("\n번호를 입력하세요: ")

    if selected_instance == '1':
        compare_afc_instance(OLD_info, NEW_info, file_paths, commands)
    elif selected_instance == '2':
        compare_waf_instance(OLD_info, NEW_info)
    elif selected_instance == '3':
        compare_pron_instance(OLD_info, NEW_info, file_paths, commands)
    else:
        print("다시 입력해주세요.")

data[server_key]:
        all_servers.extend(data[server_key]['server_list'])

selected_servers_1 = select_server(user_input_1, all_servers)
selected_servers_2 = select_server(user_input_2, all_servers)

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

compare_instance(selected_servers_1[0], selected_servers_2[0], file_paths, commands)


# AFC 인스턴스 비교 함수
def compare_afc_instance(old_info, new_info, file_paths, commands):
    print("\nAFC 비교 결과:\n")
    compare_internal_files(old_info.get('A', {}), new_info.get('A', {}), file_paths)
    compare_commands(old_info.get('A', {}), new_info.get('A', {}), commands)

# WAF 인스턴스 비교 함수
def compare_waf_instance(old_info, new_info):
    # WAF 비교 로직 추가
    pass

# PRON 인스턴스 비교 함수
def compare_pron_instance(old_info, new_info, file_paths, commands):
    print("\nPRON 비교 결과:\n")
    compare_internal_files(old_info.get('P', {}), new_info.get('P', {}), file_paths)
    compare_commands(old_info.get('P', {}), new_info.get('P', {}), commands)

# 명령어 비교 함수
def compare_commands(old_info, new_info, commands):
    for command in commands:
        print(f"\n--------------------'{command}' 비교 중--------------------")
        old_command_result = run_command(create_ssh_command(old_info, command))
        new_command_result = run_command(create_ssh_command(new_info, command))

        if old_command_result is not None and new_command_result is not None:
            if old_command_result.strip() == new_command_result.strip():
                print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
            else:
                print(f"\n{command} 명령어의 결과가 다릅니다.\n")
                print_diff(old_info, new_info, old_command_result, new_command_result)
        else:
            print(f"{command} 명령어 실행 중 오류가 발생했습니다.")

# 파일 비교 결과 출력 함수
def print_diff(old_info, new_info, old_result, new_result):
    differ = difflib.Differ()
    diff_result = list(differ.compare(old_result.splitlines(), new_result.splitlines()))

    changed_lines = [line for line in diff_result if line.startswith('- ') or line.startswith('+ ')]

    if changed_lines:
        print(f"\n{old_info.get('server_name')}:")
        for line in changed_lines:
            if line.startswith('- '):
                print(f"{line[2:]}")

        print(f"\n{new_info.get('server_name')}")
        for line in changed_lines:
            if line.startswith('+ '):
                print(f"{line[2:]}")
    else:
        print("변경된 내용이 없습니다.")
        
    print("-----------------------------------------------------------------")

# 메인 코드 시작
user_input_1 = input("공용 리전의 이름을 입력하세요[ex) seo]: ").lower()
user_input_2 = input("신규 리전의 이름을 입력하세요[ex) lgw]: ").lower()

all_servers = []
for server_key in data:
    if isinstance(data[server_key], dict) and 'server_list' in data[server_key]:
        all_servers.extend(data[server_key]['server_list'])

# 선택한 리전에 해당하는 서버 선택
selected_servers_1 = select_server(user_input_1, all_servers)
selected_servers_2 = select_server(user_input_2, all_servers)

# 선택한 서버 비교
compare_instance(selected_servers_1[0], selected_servers_2[0], file_paths, commands)


