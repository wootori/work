#!/bin/bash

# 서버1, 서버2 입력 받기
read -p "입력 (예: aljw1): " server1
read -p "입력 (예: altr1): " server2

# serverlist.json 파일 경로
serverlist_path="/home/jinwoo/serverlist.json"
echo "$serverlist_path"

# 서버1 정보 추출
server1_info=$(jq -r --arg server "$server1" '.[$server].server_list[] | select(.name == $server) | .item[0].info' "$serverlist_path")

# 서버2 정보 추출
server2_info=$(jq -r --arg server "$server2" '.[$server].server_list[] | select(.name == $server) | .item[0].info' "$serverlist_path")

# 서버1의 SSH 연결 정보 추출
server1_ip=$(echo "$server1_info" | jq -r '.public_ip')
server1_user="root"
server1_password=$(echo "$server1_info" | jq -r '.passwd')
server1_port=$(echo "$server1_info" | jq -r '.port')

# 서버2의 SSH 연결 정보 추출
server2_ip=$(echo "$server2_info" | jq -r '.public_ip')
server2_user="root"
server2_password=$(echo "$server2_info" | jq -r '.passwd')
server2_port=$(echo "$server2_info" | jq -r '.port')

# 서버1과 서버2의 /etc/nginx/conf.d/ 디렉터리 내용 비교
server1_ls=$(sshpass -p "$server1_password" ssh -o StrictHostKeyChecking=no -p "$server1_port" "$server1_user"@"$server1_ip" "ls -al /etc/nginx/conf.d/")
server2_ls=$(sshpass -p "$server2_password" ssh -o StrictHostKeyChecking=no -p "$server2_port" "$server2_user"@"$server2_ip" "ls -al /etc/nginx/conf.d/")

echo "$server1_password"
echo "$server2_password"

echo "$server1_port"
echo "$server2_port"

echo "$server1_user"@"$server1_ip"
echo "$server1_user"@"$server1_ip"

# 두 디렉터리 내용 비교
result=$(diff <(echo "$server1_ls") <(echo "$server2_ls"))

# 비교 결과 출력
echo "서버1 /etc/nginx/conf.d/ 디렉터리 내용:"
echo "$server1_ls"
echo

echo "서버2 /etc/nginx/conf.d/ 디렉터리 내용:"
echo "$server2_ls"
echo

if [ -z "$result" ]; then
    echo "두 디렉터리는 동일합니다."
else
    echo "두 디렉터리는 다릅니다:"
    echo "$result"
fi
