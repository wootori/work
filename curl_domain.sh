#!/bin/bash

# Path to file containing domain list
#input_file="/home/jinwoo/domain_list"
input_file="/home/jinwoo/moya_domain_list"
# Set each IP address as a variable
AVSB3="108.61.160.62"
AVSB2="149.28.27.238"
AVSB1="198.13.57.2"
AVIB1="45.76.206.71"
AVB11="108.61.201.72"

# Execute the curl command for each domain and save the results
while IFS= read -r domain
do
    echo "Domain: $domain"

    # Execute curl command for each IP to get response code
    for ip_var in AVSB3 AVSB2 AVSB1 AVIB1 AVB11
    do
        ip="${!ip_var}" # Use a variable to get the IP value

        # Execute curl command for each domain and print the result
        response=$(curl -I --resolve "$domain:80:$ip" "http://$domain" 2>&1 | awk '/HTTP\/1.1 [0-9]+/ {print $2}' )
        
        # Print the result directly to the terminal
        echo "${ip_var}: ${response:-error}"
    done

    echo "--------------------------"
done < "$input_file"

