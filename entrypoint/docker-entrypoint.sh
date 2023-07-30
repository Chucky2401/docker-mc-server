#!/bin/sh

trap shutdown 1 2 3 6 9 14 15 20

set -Eeuo pipefail
pythonArg=$1
shift

function shutdown()
{
    stop-server
    wait "$javaPid"
}

export PATH=$PATH:/usr/local/bin/mcserver

cd "$(dirname "$0")"
python3 download-minecraft.py $pythonArg
echo "Install result: $?"

cd /mcserver
javaExtraArgs="--add-modules=jdk.incubator.vector -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20"
exec java -Xms1G -Xmx1G $javaExtraArgs -jar server.jar --nogui &
javaPid=`pgrep -f java | xargs`

sleep 30s

echo "[hit enter key to exit] or run 'docker stop <container>'"
read

shutdown

echo "Server shutdown!"
