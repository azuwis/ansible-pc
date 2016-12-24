#!/bin/sh

# Note: keep stdout clean, as it may be used to pass data back in the future,
# and it is used to signal NotImplemented.

set -e
cmd="$1"
shift

echo ">> external-handler.sh: ${cmd}" 1>&2

case "$cmd" in
    pre-perform)
        cat >"/etc/nginx/sites-enabled/zauth_server_names_hash_bucket_size.conf" <<EOF
server_names_hash_bucket_size 128;
EOF
        ;;
    perform)
        echo "domain: ${domain}" 1>&2
        echo "z_domain: ${z_domain}" 1>&2
        echo "cert_path: ${cert_path}" 1>&2
        echo "key_path: ${key_path}" 1>&2
        echo "port: ${port}" 1>&2
        cat >"/etc/nginx/sites-enabled/zauth_${domain}_${z_domain}.conf" <<EOF
server {
    listen [::]:${port} ssl;
    listen ${port} ssl;
    server_name ${z_domain};
    ssl_certificate ${cert_path};
    ssl_certificate_key ${key_path};

    return 200;
}
EOF
        ;;
    post-perform)
        /etc/init.d/nginx reload 1>&2
        ;;
    pre-cleanup)
        ;;
    cleanup)
        echo "domain: ${domain}" 1>&2
        rm -f "/etc/nginx/sites-enabled/zauth_${domain}_"*.conf
        rm -f /etc/nginx/sites-enabled/zauth_server_names_hash_bucket_size.conf
        ;;
    post-cleanup)
        /etc/init.d/nginx reload 1>&2
        ;;
    *)
        echo "NotImplemented"
        exit 1
        ;;
esac
