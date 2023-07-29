#!/bin/bash

set -Eeuo pipefail

echo "*** Add route for Local Network"
GATEWAY=$(/bin/ip route | grep default | awk '{print $3}')
INTERFACE=$(/bin/ip route | grep default | awk '{print $5}')
/bin/ip route add to 192.168.1.0/24 via $GATEWAY dev $INTERFACE

echo "*** Start OpenVPN"
/usr/sbin/openvpn --config /root/.openvpn/Sweden.ovpn --log-append /root/.openvpn/logs/openvpn.log --daemon

echo "*** Waiting OpenVPN connected"
sleep 15

echo "*** Start Deluged"
/usr/bin/python3 /usr/bin/deluged -c /config --logfile=/config/deluged.log --loglevel=info

echo "*** Done"

exec "$@"
