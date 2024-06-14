#!/bin/bash

domain_list_file="Domain_List"
confirmation_required_domains=""

while IFS= read -r domain; do
    response_code=$(curl -s -I "${domain}/.cloudbric/pron/" | awk '/HTTP\/1.1 [0-9]+/ {print $2}')

    echo "도메인: ${domain}"
    echo "응답 코드: ${response_code}"

    if [[ ${response_code} == "200" || ${response_code} == "202" || ${response_code} == "302" || ${response_code} == "301" ]]; then
        dig_result=$(dig +noall +answer "${domain}")
        echo "Dig 결과:"
        echo "${dig_result}"
    else
        confirmation_required_domains="${confirmation_required_domains}${domain}\n"
        echo "확인이 필요합니다. 응답 코드 - ${response_code}"
    fi

    echo "-------------------------"

done < "${domain_list_file}"

# 확인이 필요한 도메인들을 한 번에 출력
if [ -n "${confirmation_required_domains}" ]; then
    echo -e "확인이 필요한 도메인들:\n${confirmation_required_domains}"
fi

