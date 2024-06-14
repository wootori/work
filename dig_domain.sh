#!/bin/bash

# 도메인 목록이 있는 파일 경로
#input_file="/home/jinwoo/tokyo_domain"
input_file="/home/jinwoo/dig_domain_list"

# 결과를 저장할 파일 경로
output_file="/home/jinwoo/dig_domain_결과"

# 입력 파일에서 도메인 읽기
while IFS= read -r domain
do
    # 각 도메인에 대한 검색 결과를 저장하는 변수 초기화
    result=""

    # 각 도메인에 대한 결과를 변수에 추가
    result+="도메인: $domain"$'\n'
    result+=$(dig +noall +answer "$domain")
#    result+=$'\n'  # 추가된 줄 바꿈 문자

    # 3번째 줄 추가
    result+=""$'\n'
    
    result+="--------------------------------------------------------------------------------------"
#    result+="--------------------------------------------------------------------------------------"$'\n'

    # 결과를 파일에 추가
    echo "$result" >> "$output_file"

done < "$input_file"
