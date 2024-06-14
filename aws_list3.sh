#!/bin/bash

# AWS 지역 목록 정의
regions=("us-east-2" "us-east-1" "us-west-1" "us-west-2" "af-south-1" "ap-east-1" "ap-south-2" "ap-southeast-3" "ap-southeast-4" "ap-south-1" "ap-northeast-3" "ap-northeast-2" "ap-southeast-1" "ap-southeast-2" "ap-northeast-1" "ca-central-1" "ca-west-1" "eu-central-1" "eu-west-1" "eu-west-2" "eu-south-1" "eu-west-3" "eu-south-2" "eu-north-1" "eu-central-2" "il-central-1" "me-south-1" "me-central-1" "sa-east-1")

# 모든 지역에 대해 조회
for region in "${regions[@]}"
do
    echo "Region: $region"
    aws ec2 describe-instances --region $region --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value | [0], State.Name, PublicIpAddress]' --output table
    echo ""
done
