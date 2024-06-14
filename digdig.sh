#!/bin/bash

domain_list_file="Domain_List"

while IFS= read -r domain; do
    response_code=$(curl -I "${domain}/.cloudbric/pron/" | awk '/HTTP\/1.1 [0-9]+/ {print $2}')

    echo "도메인: ${domain}"
    echo "응답 코드: ${response_code}"

    if [[ ${response_code} == "200" || ${response_code} == "202" ]]; then
        dig_result=$(dig +noall +answer "${domain}")
        echo "Dig 결과:"
        echo "${dig_result}"
    else
        echo "확인이 필요합니다. 응답 코드 - ${response_code}"
    fi

    echo "-------------------------"

done < "${domain_list_file}"

