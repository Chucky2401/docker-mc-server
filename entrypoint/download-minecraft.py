import os
import urllib.request, json, requests
import subprocess, re
from tqdm import tqdm

## Get vanilla server
def vanilla():
    versionManifestUrl = -1
    serverUrl          = -1

    versionsManifest   = urllib.request.urlopen("https://launchermeta.mojang.com/mc/game/version_manifest.json")
    jsonVersions       = json.load(versionsManifest)
    versionChose       = os.environ['MC_VERSION']

    if versionChose == 'latest':
        versionChose = jsonVersions['latest']['release']

    print("* Looking for the " + versionChose + " version...")

    for i in jsonVersions['versions']:
        if i['id'] == versionChose:
            versionManifestUrl = i['url']
            break

    if versionManifestUrl == -1:
        return 101

    versionManifest = urllib.request.urlopen(versionManifestUrl)
    jsonVersion     = json.load(versionManifest)
    serverUrl       = jsonVersion['downloads']['server']['url']
    serverSize      = jsonVersion['downloads']['server']['size']

    if serverUrl == -1:
        return 102

    print("* Downloading Minecraft Server version " + versionChose + "...")
    serverJar = requests.get(serverUrl, stream=True)
    blockSize = 1024
    progressBar = tqdm(total=serverSize, unit='iB', unit_scale=True)
    with open('/mcserver/server.jar', 'wb') as file:
        for data in serverJar.iter_content(blockSize):
            progressBar.update(len(data))
            file.write(data)
    progressBar.close()

    if serverSize != 0 and progressBar.n != serverSize:
        return 103

    return 0



## Get fabric server
def fabric():
    serverUrl = -1

    versionsManifest  = urllib.request.urlopen("https://meta.fabricmc.net/v2/versions/game").read()
    installerManifest = urllib.request.urlopen("https://meta.fabricmc.net/v2/versions/installer").read()
    loaderManifest    = urllib.request.urlopen("https://meta.fabricmc.net/v2/versions/loader").read()

    jsonVersions      = json.loads(versionsManifest)
    jsonInstaller     = json.loads(installerManifest)
    jsonLoader        = json.loads(loaderManifest)

    versionChose      = os.environ['MC_VERSION']

    if versionChose == 'latest':
        versionChose = jsonVersions[0]['version']

    print("* Looking for the " + versionChose + " version...")

    versionInstaller = jsonInstaller[0]['version']
    versionLoader  = jsonLoader[0]['version']

    serverUrl = "https://meta.fabricmc.net/v2/versions/loader/" + versionChose + "/" + versionLoader + "/" + versionInstaller + "/server/jar"

    if serverUrl == -1:
        return 201

    print("* Downloading Minecraft Server version " + versionChose + "...")
    serverJar = requests.get(serverUrl, stream=True)
    serverSize = int(serverJar.headers.get('content-length', 0))
    blockSize = 1024
    progressBar = tqdm(total=serverSize, unit='iB', unit_scale=True)
    with open('/mcserver/server.jar', 'wb') as file:
        for data in serverJar.iter_content(blockSize):
            progressBar.update(len(data))
            file.write(data)
    progressBar.close()

    if serverSize != 0 and progressBar.n != serverSize:
        return 202

    return 0

## First rune
def firstRun():
    print("* First run to generate config files...")
    
    maxMem           = os.environ['MC_MAX_MEM']
    minMem           = os.environ['MC_MIN_MEM']

    process    = subprocess.Popen(["java", "-Xms" + minMem, "-Xmx" + maxMem, "-jar", "/mcserver/server.jar", "--nogui"], cwd='/mcserver', stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    processOut = process.communicate()
    process.terminate()

    result = processOut[1].decode('ascii')

    if result != "":
        return 104

    return 0

## eula.txt
def eula():
    print("* Replacing 'eula=false' by 'eula=true'...")
    keyword     = "eula=false"
    replacement = "eula=true"

    with open("/mcserver/eula.txt", "r") as file:
        eula = file.readlines()

    i = 0
    while i < len(eula):
        if keyword in eula[i]:
            eula[i] = eula[i].replace(keyword, replacement)
        i += 1
    
    with open("/mcserver/eula.txt", "w") as file:
        file.writelines(eula)
    
    return 0

## Server.properties
def properties():
    keyView = "view-distance=[0-9]+"
    keySim  = "simulation-distance=[0-9]+"
    keySync = "sync-chunk-writes=.+"
    repView = "view-distance=8"
    repSim  = "simulation-distance=4"
    repSync = "sync-chunk-writes=false"

    os.rename("/mcserver/server.properties", "/mcserver/server.properties_origin")

    serverPropertiesInput = open("/mcserver/server.properties_origin", "r")
    serverPropertiesOutput = open("/mcserver/server.properties", "w")

    for line in serverPropertiesInput:
        if re.search(keyView, line):
            print("* Replacing 'view-distance=x' by 'view-distance=8'...")
            serverPropertiesOutput.write(re.sub(keyView, repView, line))
            continue

        if re.search(keySim, line):
            print("* Replacing 'simulation-distance=x' by 'simulation-distance=4'...")
            serverPropertiesOutput.write(re.sub(keySim, repSim, line))
            continue

        if re.search(keySync, line):
            print("* Replacing 'sync-chunk-writes=true' by 'sync-chunk-writes=false'...")
            serverPropertiesOutput.write(re.sub(keySync, repSync, line))
            continue

        serverPropertiesOutput.write(line)

    serverPropertiesInput.close()
    serverPropertiesOutput.close()

    return 0

## Main
def main():
    result         = -1
    resultFirstRun = -1
    resultEula     = -1
    resultProp     = -1

    print("*********************************************************")
    print("*  __  __  _                                   __  _    *")
    print("* |  \/  |(_)                                 / _|| |   *")
    print("* | \  / | _  _ __    ___   ___  _ __   __ _ | |_ | |_  *")
    print("* | |\/| || || '_ \  / _ \ / __|| '__| / _` ||  _|| __| *")
    print("* | |  | || || | | ||  __/| (__ | |   | (_| || |  | |_  *")
    print("* |_|  |_||_||_| |_| \___| \___||_|    \__,_||_|   \__| *")
    print("*                                                       *")
    print("*          _____                                        *")
    print("*         / ____|                                       *")
    print("*        | (___    ___  _ __ __   __  ___  _ __         *")
    print("*         \___ \  / _ \| '__|\ \ / / / _ \| '__|        *")
    print("*         ____) ||  __/| |    \ V / |  __/| |           *")
    print("*        |_____/  \___||_|     \_/   \___||_|           *")
    print("*                                                       *")
    print("*********************************************************")
    print("")

    print("The " + os.environ['MC_LOADER'] + " Minecraft server will be installed and pre-configured")
    print("")

    if os.environ['MC_LOADER'] == 'vanilla':
        result = vanilla()

    if os.environ['MC_LOADER'] == 'fabric':
        result = fabric()

    if result == 0:
        print("Minecraft server has been downloaded!")
        print("")
        print("We will generate config files")
        resultFirstRun = firstRun()
    else:
        return resultFirstRun

    if resultFirstRun == 0:
        print("Config files has been generated!")
        print("")
        print("We will update eula.txt file to accept them!")
        resultEula = eula()
    else:
        return resultEula

    if resultEula == 0:
        print("EULA has been accepted! I hope you agree with it...")
        print("")
        print("Anyway! Updating server.properties to optimize performance!")
        resultProp = properties()
    else:
        return resultProp

    print("")
    print("Server optimized! Enjoy :*) !")

    return resultProp

if __name__ == '__main__':
    if len(os.listdir('/mcserver')) == 0:
        main()
    else:
        print(0)
