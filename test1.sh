#!/bin/bash

# 원격 서버1에서 파일1 가져오기 및 변수에 저장
file1_content=$(sshpass -p didEl201% ssh -o StrictHostKeyChecking=no -oPort=7789 root@172.105.223.221 "cat /etc/hostname")
#file1_content=$(sshpass -p didEl201% ssh -oPort=7789 root@172.105.223.221 "cat /etc/hostname")

# 원격 서버2에서 파일2 가져오기 및 변수에 저장
file2_content=$(sshpass -p didEl201% ssh -o StrictHostKeyChecking=no -oPort=7789 root@172.104.88.145 "cat /etc/hostname")
#file2_content=$(sshpass -p didEl201% ssh -oPort=7789 root@172.104.88.145 "cat /etc/hostname")

# 파일1 내용 출력
echo "$file1_content"

# 파일2 내용 출력
echo "$file2_content"

# 두 파일 비교하고 중복된 내용 삭제하며 서로 다른 내용 출력
diff <(echo "$file1_content") <(echo "$file2_content") | awk '/^</ {print "서버1: " substr($0,3)} /^>/ {print "서버2: " substr($0,3)}'
