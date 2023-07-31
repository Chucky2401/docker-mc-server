import subprocess, re, tempfile, os, sys
import time
from datetime import datetime

def main():
    matchLastLine = "^\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\]: RCON running on \d.\d.\d.\d:\d{,5}"
    serverStarted = False

    maxMem       = "-Xms" + os.environ['MC_MAX_MEM']
    minMem       = "-Xmx" + os.environ['MC_MIN_MEM']
    mcServerArgs = ["nohup", "java", minMem, maxMem, "--add-modules=jdk.incubator.vector", "-XX:+UseG1GC", "-XX:+ParallelRefProcEnabled", "-XX:MaxGCPauseMillis=200", "-XX:+UnlockExperimentalVMOptions", "-XX:+DisableExplicitGC", "-XX:+AlwaysPreTouch", "-XX:G1HeapWastePercent=5", "-XX:G1MixedGCCountTarget=4", "-XX:InitiatingHeapOccupancyPercent=15", "-XX:G1MixedGCLiveThresholdPercent=90", "-XX:G1RSetUpdatingPauseTimePercent=5", "-XX:SurvivorRatio=32", "-XX:+PerfDisableSharedMem", "-XX:MaxTenuringThreshold=1", "-Dusing.aikars.flags=https://mcflags.emc.gs", "-Daikars.new.flags=true", "-XX:G1NewSizePercent=30", "-XX:G1MaxNewSizePercent=40", "-XX:G1HeapRegionSize=8M", "-XX:G1ReservePercent=20", "-jar", "/mcserver/server.jar", "--nogui"]

    print("Starting Minecraft Server...")

    with tempfile.NamedTemporaryFile() as out, tempfile.TemporaryFile() as err:
        out.write(str(f"{datetime.now()}\n").encode("utf-8"))
        mcServerProcess = subprocess.Popen(mcServerArgs, cwd='/mcserver', stdin=subprocess.DEVNULL, stdout=out, stderr=err, preexec_fn=os.setpgrp)

        f = open(out.name, 'r')
        while serverStarted == False:
            for line in f.readlines():
                print(line, end='')
                if re.match(matchLastLine, line):
                    print(" * Server started (" + str(mcServerProcess.pid) + ")!")
                    serverStarted = True
                    break
            time.sleep(0.5)

    latestLog = open("/mcserver/logs/latest.log", "a")
    latestLog.write("\n")
    latestLog.close()

    serverPid = open("/mcserver/server.pid", "w")
    serverPid.write(str(mcServerProcess.pid))
    serverPid.close()

    print("")
    print("Have fun!")

if __name__ == '__main__':
    main()

    quit()
