#!/bin/bash

# 파일에 도메인 목록이 있는 경로
input_file="/home/jinwoo/tokyo_domain"

# 도메인 결과를 출력할 변수 초기화
while IFS= read -r domain
do
    # 각 도메인에 대한 결과를 변수에 추가
    echo "Domain: $domain"
    dig +noall +answer "$domain"
    echo ""
    echo "------------------------------------------------------------- ---------------------------------------"
done < "$input_file"

