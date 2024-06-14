import json
import subprocess
import sys

# JSON 파일 불러오기
with open('/home/jinwoo/serverlist.json', 'r') as file:
    data = json.load(file)

# 함수 정의: 서버에서 정보 추출
def extract_info(server):
    region = server['name'].split('/')[0].strip()
    info_dict = {item['name'][0]: {'public_ip': item['info']['public_ip'], 'port': item['info']['port'], 'user': item['info']['user'], 'passwd': item['info']['passwd']} for item in server['item']}
    return region, info_dict

'''
# 함수 정의: 다양한 파일 비교
def compare_additional_files(old_info, new_info, file_paths):
    results = {}
    for file_path in file_paths:
        old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path}"
        new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path}"

        # 디버깅 정보 출력
        print(f"Old SSH Command for {file_path}:", old_ssh_command)
        print(f"New SSH Command for {file_path}:", new_ssh_command)

        try:
            # SSH로 파일 내용 가져오기
            old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
            new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

            # diff로 파일 비교
            diff_command = f"diff -u <(echo '{old_result.strip()}') <(echo '{new_result.strip()}')"
            diff_result = subprocess.check_output(diff_command, shell=True, text=True)

            results[file_path] = diff_result
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while comparing {file_path}: {e}")
            results[file_path] = None

    return results
'''
def compare_additional_files(old_info, new_info, file_paths):
    results = {}
    for file_path in file_paths:
        old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} ls {file_path}"
        new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} ls {file_path}"

        # 디버깅 정보 출력
        print(f"Old SSH Command for {file_path}:", old_ssh_command)
        print(f"New SSH Command for {file_path}:", new_ssh_command)

        try:
            # SSH로 파일이 존재하는지 확인
            subprocess.check_output(old_ssh_command, shell=True, text=True)
            subprocess.check_output(new_ssh_command, shell=True, text=True)

            # SSH로 파일 내용 가져오기
            old_result = subprocess.check_output(f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path}", shell=True, text=True)
            new_result = subprocess.check_output(f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path}", shell=True, text=True)

            # diff로 파일 비교
            diff_command = f"diff -u <(echo '{old_result.strip()}') <(echo '{new_result.strip()}')"
            diff_result = subprocess.check_output(diff_command, shell=True, text=True)

            results[file_path] = diff_result
        except subprocess.CalledProcessError as e:
            if "No such file or directory" in e.output:
                print(f"File not found: {file_path}")
                results[file_path] = None
            else:
                print(f"Error occurred while comparing {file_path}: {e}")
                results[file_path] = None

    return results


# 사용자로부터 비교할 파일 목록 입력 받기
file_paths = [
    '/etc/nginx/sites-enabled/ssl_config',
    '/etc/nginx/sites-enabled/default.conf',
    '/etc/nginx/sites-enabled/error_config',
    '/etc/nginx/sites-enabled/letsencrypt_config',
    '/etc/nginx/fastcgi_params',
    '/etc/nginx/mime.types',
    '/etc/nginx/nginx.conf',
    '/etc/nginx/letsencrypt_cf',
    '/tmp/openssl_version',  # 임시 파일로 openssl version 결과 저장
    '/tmp/php_version',      # 임시 파일로 php -version 결과 저장
    '/tmp/ulimit_output',    # 임시 파일로 ulimit -a 결과 저장
    '/tmp/nginx_version'     # 임시 파일로 /etc/nginx/sbin/nginx -v 결과 저장
]


'''
# 함수 정의: 내부 파일 비교
def compare_internal_files(old_info, new_info, file_path):
    old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path}"
    new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path}"

    # 디버깅 정보 출력
    print("Old SSH Command:", old_ssh_command)
    print("New SSH Command:", new_ssh_command)

    try:
        # SSH로 내부 파일 내용 가져오기
        old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
        new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

        # 진행 중인 작업을 출력
        print(f"내부 파일 '{file_path}' 비교 중...")

        # 파일 내용 비교
        if old_result.strip() == new_result.strip():
            return f"파일 '{file_path}'이(가) 동일합니다."
        else:
            return f"파일 '{file_path}'이(가) 다릅니다.\n\nOld Server:\n{old_result}\n\nNew Server:\n{new_result}"

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None
'''

# 사용자로부터 서버 이름 입력 받기
user_input_1 = input("첫 번째 서버의 이름을 입력하세요: ").lower()
user_input_2 = input("두 번째 서버의 이름을 입력하세요: ").lower()

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
    print("다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_1, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("번호를 입력하세요: "))
    selected_servers_1 = [selected_servers_1[selected_index - 1]]

if len(selected_servers_2) > 1:
    print("다음 중 하나를 선택해주세요:")
    for i, server in enumerate(selected_servers_2, start=1):
        print(f"{i}. {server['name']}")

    selected_index = int(input("번호를 입력하세요: "))
    selected_servers_2 = [selected_servers_2[selected_index - 1]]

# 변수 초기화
OLD_region, OLD_info = extract_info(selected_servers_1[0])
NEW_region, NEW_info = extract_info(selected_servers_2[0])

# 디버깅 정보 출력
print("Old Server Info:", OLD_region, OLD_info)
print("New Server Info:", NEW_region, NEW_info)

# 비교할 인스턴스 번호 선택
print("비교할 인스턴스 번호를 선택해주세요:")
print("1. AFC")
print("2. WAF")
print("3. PRON")

selected_instance = input("번호를 입력하세요: ")

# 선택된 인스턴스 번호에 따라 출력
if selected_instance == '1':
    print("\nAFC 비교 결과:")
    print("첫 번째 서버 정보:")
    print("OLD_AFC_name:", OLD_region)
    print("OLD_AFC_public_ip:", OLD_info.get('A', {}).get('public_ip'))
    print("OLD_AFC_port:", OLD_info.get('A', {}).get('port'))
    print("OLD_AFC_user:", OLD_info.get('A', {}).get('user'))
    print("OLD_AFC_passwd:", OLD_info.get('A', {}).get('passwd'))

    print("\n두 번째 서버 정보:")
    print("NEW_AFC_name:", NEW_region)
    print("NEW_AFC_public_ip:", NEW_info.get('A', {}).get('public_ip'))
    print("NEW_AFC_port:", NEW_info.get('A', {}).get('port'))
    print("NEW_AFC_user:", NEW_info.get('A', {}).get('user'))
    print("NEW_AFC_passwd:", NEW_info.get('A', {}).get('passwd'))

'''
    # 내부 파일 비교
    diff_result = compare_internal_files(OLD_info.get('A', {}), NEW_info.get('A', {}), '/etc/resolv.conf')

    # 비교 결과 출력
    if diff_result is not None:
        print("내부 파일 비교 결과:")
        print(diff_result)
    else:
        print("내부 파일 비교 중 오류가 발생했습니다.")
'''
# 다양한 파일 비교
additional_diff_results = compare_additional_files(OLD_info.get('A', {}), NEW_info.get('A', {}), file_paths)

# 비교 결과 출력
for file_path, diff_result in additional_diff_results.items():
    print(f"\n비교 결과 for {file_path}:")
    if diff_result is not None:
        print(diff_result)
    else:
        print(f"비교 중 오류가 발생했습니다. {file_path}")


