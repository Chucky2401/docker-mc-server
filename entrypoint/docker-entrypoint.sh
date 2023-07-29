#!/bin/ash

set -Eeuo pipefail

function shutdown()
{
    stop-server
}

pythonArg=$1
shift

#python3 download-minecraft.py $pythonArg

#echo "Install result: $?"

cd /mcserver
exec java -Xms1G -Xmx1G -jar server.jar nogui

trap shutdown 1 2 3 6 9 14 15 20

exec "$@"
