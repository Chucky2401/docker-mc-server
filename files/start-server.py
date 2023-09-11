import subprocess, re, tempfile, os, sys
import time, signal
from datetime import datetime

class GracefulKiller:
    kill_now = False
    process = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        subprocess.Popen(["stop-server"])
        self.process.communicate()
        time.sleep(1)
        self.kill_now = True

# -------------------------------------------------------------------------------------------------------------------- #

def main():
    matchLastLine = "^\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\]: RCON running on \d.\d.\d.\d:\d{,5}"
    serverStarted = False

    killer = GracefulKiller()

    maxMem       = "-Xms" + os.environ['MC_MAX_MEM']
    minMem       = "-Xmx" + os.environ['MC_MIN_MEM']
    mcServerArgs = ["nohup", "java", minMem, maxMem, "--add-modules=jdk.incubator.vector", "-XX:+UseG1GC", "-XX:+ParallelRefProcEnabled", "-XX:MaxGCPauseMillis=200", "-XX:+UnlockExperimentalVMOptions", "-XX:+DisableExplicitGC", "-XX:+AlwaysPreTouch", "-XX:G1HeapWastePercent=5", "-XX:G1MixedGCCountTarget=4", "-XX:InitiatingHeapOccupancyPercent=15", "-XX:G1MixedGCLiveThresholdPercent=90", "-XX:G1RSetUpdatingPauseTimePercent=5", "-XX:SurvivorRatio=32", "-XX:+PerfDisableSharedMem", "-XX:MaxTenuringThreshold=1", "-Dusing.aikars.flags=https://mcflags.emc.gs", "-Daikars.new.flags=true", "-XX:G1NewSizePercent=30", "-XX:G1MaxNewSizePercent=40", "-XX:G1HeapRegionSize=8M", "-XX:G1ReservePercent=20", "-jar", "/mcserver/server.jar", "--nogui"]

    print("Starting Minecraft Server...")

    with tempfile.NamedTemporaryFile() as out, tempfile.TemporaryFile() as err:
        out.write(str(f"{datetime.now()}\n").encode("utf-8"))
        mcServerProcess = subprocess.Popen(mcServerArgs, cwd='/mcserver', stdin=subprocess.DEVNULL, stdout=out, stderr=err, preexec_fn=os.setpgrp)
        killer.process = mcServerProcess

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

    tailLog = subprocess.Popen(["tail", "-n", "1", "-f", "/mcserver/logs/latest.log"], cwd="/mcserver")

    while not killer.kill_now:
        time.sleep(1)

    tailLog.terminate()
    print("Server stopped!")

# -------------------------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()

    sys.exit()
