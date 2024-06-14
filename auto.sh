#!/bin/bash

# 함수: JSON 파일에서 정보 추출
#function get_info() {
#    local json_file=$1
#    local prefix=$2
#    jq -r --arg prefix "$prefix" '.server_list[] | select(.name | startswith($prefix)) | .item[].info' "$json_file"
#}

#function get_info() {
#    local json_file=$1
#    local prefix=$2
#    jq -r --arg prefix "$prefix" '.[] | select(.name | startswith($prefix)) | .info.public_ip, .info.port, .info.user, .info.passwd' "$json_file"
#}

function get_info() {
    local json_file=$1
    local prefix=$2
    jq -r --arg prefix "$prefix" '.[].server_list[] | select(.name | startswith($prefix)) | .item[] | .info.public_ip, .info.port, .info.user, .info.passwd' "$json_file"
}



# 함수: 리눅스 파일 비교
function compare_files() {
    local old_file=$1
    local new_file=$2
    local result_file=$3
    sshpass -p "$old_passwd" ssh -o StrictHostKeyChecking=no "$old_user@$old_ip" "cat $old_file" > "$result_file.old"
    sshpass -p "$new_passwd" ssh -o StrictHostKeyChecking=no "$new_user@$new_ip" "cat $new_file" > "$result_file.new"
    diff "$result_file.old" "$result_file.new" > "$result_file"
}


# 메인 스크립트

# 1. OLD 리전 정보 입력
read -p "OLD 리전 정보를 입력해주세요 (ex. seo1): " old_region
old_json="/home/jinwoo/serverlist.json"
old_afc=$(get_info "$old_json" "a")
old_waf=$(get_info "$old_json" "w")
old_pron=$(get_info "$old_json" "p")

# 2. NEW 리전 정보 입력
read -p "NEW 리전 정보를 입력해주세요 (ex. ljw1): " new_region
new_json="/home/jinwoo/serverlist.json"
new_afc=$(get_info "$new_json" "a")
new_waf=$(get_info "$new_json" "w")
new_pron=$(get_info "$new_json" "p")

echo "$old_json"
echo "$old_afc"
echo "$old_waf"
echo "$old_pron"
echo "---------------------"
echo "$new_json"
echo "$new_afc"
echo "$new_waf"
echo "$new_pron"


# 3. 인스턴스 번호 선택
read -p "비교할 인스턴스 번호를 선택해주세요 (1.AFC, 2.WAF, 3.PRON): " instance_num
case $instance_num in
    1)
        old_ip=$(echo "$old_afc" | jq -r .ip)
        old_user=$(echo "$old_afc" | jq -r .user)
        old_passwd=$(echo "$old_afc" | jq -r .passwd)

        new_ip=$(echo "$new_afc" | jq -r .ip)
        new_user=$(echo "$new_afc" | jq -r .user)
        new_passwd=$(echo "$new_afc" | jq -r .passwd)

        compare_files "/etc/nginx/fastcgi_params" "/etc/nginx/fastcgi_params" "/etc/nginx/fastcgi_params_comparison_result.txt"
        ;;
    2)
        old_ip=$(echo "$old_waf" | jq -r .ip)
        old_user=$(echo "$old_waf" | jq -r .user)
        old_passwd=$(echo "$old_waf" | jq -r .passwd)

        new_ip=$(echo "$new_waf" | jq -r .ip)
        new_user=$(echo "$new_waf" | jq -r .user)
        new_passwd=$(echo "$new_waf" | jq -r .passwd)

        compare_files "/etc/nginx/conf.d/" "/etc/nginx/conf.d/" "/etc/nginx/conf.d_comparison_result.txt"
        ;;
    3)
        old_ip=$(echo "$old_pron" | jq -r .ip)
        old_user=$(echo "$old_pron" | jq -r .user)
        old_passwd=$(echo "$old_pron" | jq -r .passwd)

        new_ip=$(echo "$new_pron" | jq -r .ip)
        new_user=$(echo "$new_pron" | jq -r .user)
        new_passwd=$(echo "$new_pron" | jq -r .passwd)

        compare_files "/etc/nginx/fastcgi_params" "/etc/nginx/fastcgi_params" "/etc/nginx/fastcgi_params_comparison_result.txt"
        ;;
    *)
        echo "다시 입력해주세요."
        exit 1
        ;;
esac

echo "[비교한 대상]의 내용은 서로 같습니다."