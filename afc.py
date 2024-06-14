import json
import subprocess
import sys

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} 파일을 찾을 수 없습니다.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {file_path} 파일의 JSON 형식이 올바르지 않습니다.")
        sys.exit(1)

def extract_info(server):
    region = server['name'].split('/')[0].strip()
    info_dict = {item['name'][0]: {'public_ip': item['info']['public_ip'],
                                   'port': item['info']['port'],
                                   'user': item['info']['user'],
                                   'passwd': item['info']['passwd']} for item in server['item']}
    return region, info_dict

def compare_internal_files(old_info, new_info, file_path):
    old_ssh_command = f"sshpass -p {old_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {old_info['port']} {old_info['user']}@{old_info['public_ip']} cat {file_path}"
    new_ssh_command = f"sshpass -p {new_info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {new_info['port']} {new_info['user']}@{new_info['public_ip']} cat {file_path}"

    print(f"Old SSH Command for {file_path}:", old_ssh_command)
    print(f"New SSH Command for {file_path}:", new_ssh_command)

    try:
        old_result = subprocess.check_output(old_ssh_command, shell=True, text=True)
        new_result = subprocess.check_output(new_ssh_command, shell=True, text=True)

        print(f"내부 파일 '{file_path}' 비교 중...")

        if old_result.strip() == new_result.strip():
            return f"파일 '{file_path}'이(가) 동일합니다. 서로 파일 내용이 같습니다."
        else:
            return f"파일 '{file_path}'이(가) 다릅니다.\n\nOld Server:\n{old_result}\n\nNew Server:\n{new_result}"

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while comparing {file_path}: {e}")
        return None

def run_remote_command(info, command):
    ssh_command = f"sshpass -p {info['passwd']} ssh -o StrictHostKeyChecking=no -oHostKeyAlgorithms=+ssh-dss -p {info['port']} {info['user']}@{info['public_ip']} {command}"
    try:
        result = subprocess.check_output(ssh_command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{ssh_command}': {e}")
        return None

def get_user_input(prompt):
    return input(prompt).lower()

def select_server(servers, user_input):
    selected_servers = [server for server in servers if user_input in server['name'].lower()]

    if not selected_servers:
        print(f"Error: {user_input}에 해당하는 서버가 없습니다.")
        sys.exit(1)

    if len(selected_servers) > 1:
        print("다음 중 하나를 선택해주세요:")
        for i, server in enumerate(selected_servers, start=1):
            print(f"{i}. {server['name']}")

        selected_index = int(input("번호를 입력하세요: "))
        selected_servers = [selected_servers[selected_index - 1]]

    return selected_servers[0]

def compare_instances(OLD_info, NEW_info, file_paths, commands, instance_name):
    print(f"\n{instance_name} 비교 결과:")
    print(f"첫 번째 서버 정보:")
    for key, value in OLD_info.items():
        print(f"OLD_{instance_name}_{key}: {value}")

    print(f"\n두 번째 서버 정보:")
    for key, value in NEW_info.items():
        print(f"NEW_{instance_name}_{key}: {value}")

    for file_path in file_paths:
        internal_diff_result = compare_internal_files(OLD_info, NEW_info, file_path)
        print(f"\n내부 파일 비교 결과 for {file_path}:")
        if internal_diff_result is not None:
            print(internal_diff_result)
        else:
            print(f"내부 파일 비교 중 오류가 발생했습니다. {file_path}")

    for command in commands:
        print(f"\n외부 명령어 실행 결과 for {command}:")
        old_command_result = run_remote_command(OLD_info, command)
        new_command_result = run_remote_command(NEW_info, command)

        if old_command_result is not None and new_command_result is not None:
            if old_command_result.strip() == new_command_result.strip():
                print(f"{command} 명령어의 결과가 동일합니다. 서로 결과가 같습니다.")
            else:
                print(f"{command} 명령어의 결과가 다릅니다.")
                print(f"\nOld Server 결과:\n{old_command_result}\n\nNew Server 결과:\n{new_command_result}")
        else
