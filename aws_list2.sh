#!/bin/bash

# AWS 지역 목록 정의
regions=("us-east-1" "us-west-1" "us-west-2" "eu-west-1" "eu-central-1" "ap-southeast-1" "ap-southeast-2" "ap-northeast-1" "sa-east-1")

# 각 리전에 대해 실행 및 EC2 인스턴스 여부 확인
for region in "${regions[@]}"
do
    output=$(aws ec2 describe-instances --region $region)
    instance_count=$(echo $output | jq '.Reservations | length')
    # EC2 인스턴스가 있는 경우에만 출력
    if [[ $instance_count -gt 0 ]]; then
        echo "Region: $region"
        echo "--------------------------------------------------------------"
        echo "|                      DescribeInstances                     |"
        echo "+-------------------------------------------------+----------+"
        echo "$output" | jq -r '.Reservations[].Instances[] | "|\(.Tags[] | select(.Key=="Name").Value) | \(.State.Name) |"'
        echo "+-------------------------------------------------+----------+"
        echo ""
    fi
done
