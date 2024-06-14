#!/bin/bash

while IFS= read -r domain; do
#    echo "$domain"
    
    result=$(curl -s -v "$domain/.cloudbric/pron/" 2>&1 | awk '/^\* Connection / {next} /HTTP\/1.1 [0-9]+ [^\r]/ {p=0} {if(p) print} /{/{p=1}')

    if [ -z "$result" ]; then
        result="no body"
    fi

    if echo "$result" | grep -q "Immediate connect fail for"; then
        result="IPv6 연결 실패: Network is unreachable"
    fi

    echo "$domain: $result"
    echo "--------------------------"
done < "tokyo_domain"

