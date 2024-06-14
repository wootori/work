#!/bin/bash

# AWS 지역 목록 정의
regions=("us-east-1" "us-west-1" "us-west-2" "eu-west-1" "eu-central-1" "ap-southeast-1" "ap-southeast-2" "ap-northeast-1" "sa-east-1")

# 각 리전에 대해 실행 및 EC2 인스턴스 여부 확인
for region in "${regions[@]}"
do
    output=$(aws ec2 describe-instances --region $region --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value | [0], State.Name]' --output table 2>&1)
    # EC2 인스턴스가 없는 경우에만 출력
    if [[ ! $output =~ "An error occurred" && ! -z $output ]]; then
        echo "Region: $region"
        echo "$output"
        echo ""
    fi
done

