#!/bin/bash

# Read list of domains from file
input_file="/home/jinwoo/aws_route53_region"
while IFS= read -r domain
do
    # Look up Route 53 records for your domain and filter desired fields
    echo "Querying records for domain: $domain"
    aws route53 list-resource-record-sets --hosted-zone-id Z1ZFDA7V94CUP1 --output json | jq -r ".ResourceRecordSets[] | select(.Name == \"$domain.cbricdns.net.\") | {Name, Failover, SetIdentifier, Value: .ResourceRecords[].Value}"
    echo "----------------------------------------"
done < "$input_file" 
