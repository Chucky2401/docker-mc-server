#!/bin/sh

trap shutdown 1 2 3 6 9 14 15 20

set -Eeuo pipefail
pythonArg=$1
shift

function shutdown()
{
    stop-server
    sleep 10s
    echo "Server shutdown!"
}

export PATH=$PATH:/usr/local/bin/mcserver

cd "$(dirname "$0")"
python3 download-minecraft.py $pythonArg
echo "Install result: $?"

cd /mcserver
python3 start-server.py
javaPid=$(cat /mcserver/server.pid)

tail -n 1 -f /mcserver/logs/latest.log &
read

shutdown
