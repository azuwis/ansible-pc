#!/bin/sh
(
curl -Ls https://github.com/felixonmars/dnsmasq-china-list/raw/master/accelerated-domains.china.conf | sed -e 's!/114.114.114.114$!/127.0.0.53!' | grep -Fv cn.debian.org
while read -r domain
do
  echo "server=/$domain/127.0.0.53"
done <<EOF
app.arukas.io
bnbsky.com
dl.google.com
download.documentfoundation.org
duckdns.org
flypig.info
ipv4.tunnelbroker.net
lan
netease.com
wswebcdn.com
EOF
cat <<EOF
no-resolv
server=127.0.0.54
EOF
) > chn-domains-dnsmasq.conf
