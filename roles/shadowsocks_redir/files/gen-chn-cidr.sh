#!/bin/sh
curl 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest' | grep ipv4 | grep CN | awk -F\| '{ printf("            %s/%d,\n", $4, 32-log($5)/log(2)) }' > chn-cidr
cat <<EOF >> chn-cidr
            64.62.200.2/32,
            1.1.1.0/24,
EOF
