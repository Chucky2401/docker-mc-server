import os, argparse, sys, stat
import urllib.request, json, requests
import subprocess, re
import secrets
import string
import signal, time
from tqdm import tqdm

root = os.path.abspath(os.sep)

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

# -------------------------------------------------------------------------------------------------------------------- #

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

# -------------------------------------------------------------------------------------------------------------------- #

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
    
    os.remove("/mcserver/logs/latest.log")

    return 0

# -------------------------------------------------------------------------------------------------------------------- #

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

# -------------------------------------------------------------------------------------------------------------------- #

## Server.properties
def properties(password):
    keyView = "view-distance=[0-9]+"
    keySim  = "simulation-distance=[0-9]+"
    keySync = "sync-chunk-writes=(true|false)"

    repView = "view-distance=8"
    repSim  = "simulation-distance=4"
    repSync = "sync-chunk-writes=false"

    keyRconPort = "rcon.port=[0-9]+"
    keyRconEnable = "enable-rcon=(true|false)"
    keyRconPassword = "rcon.password="

    repRconPort = "rcon.port=25575"
    repRconEnable = "enable-rcon=true"
    repRconPassword = "rcon.password=" + password

    serverProperties = open("/mcserver/server.properties", "r+")
    properties = serverProperties.read()

    oldValue = re.search(keyView, properties).group(0)
    print(" * Replace " + oldValue + " by " + repView)
    properties = (re.sub(keyView, repView, properties))

    oldValue = re.search(keySim, properties).group(0)
    print(" * Replace " + oldValue + " by " + repSim)
    properties = (re.sub(keySim, repSim, properties))

    oldValue = re.search(keySync, properties).group(0)
    print(" * Replace " + oldValue + " by " + repSync)
    properties = (re.sub(keySync, repSync, properties))

    oldValue = re.search(keyRconEnable, properties).group(0)
    print(" * Replace " + oldValue + " by " + repRconEnable)
    properties = (re.sub(keyRconEnable, repRconEnable, properties))

    oldValue = re.search(keyRconPort, properties).group(0)
    print(" * Replace " + oldValue + " by " + repRconPort)
    properties = (re.sub(keyRconPort, repRconPort, properties))

    oldValue = re.search(keyRconPassword, properties).group(0)
    print(" * Replace " + oldValue + " by " + repRconPassword)
    properties = (re.sub(keyRconPassword, repRconPassword, properties))

    serverProperties.write(properties)
    serverProperties.close()

    return 0

# -------------------------------------------------------------------------------------------------------------------- #

def setRcon(password):
    rconStart = open("/usr/local/bin/mcserver/start-rcon", "w")
    rconStart.write("#!/bin/sh\n")
    rconStart.write("rcon -H 127.0.0.1 -p 25575 -P \"" + password + "\" -m\n")
    rconStart.close()

    rconSetOp = open("/usr/local/bin/mcserver/set-op", "w")
    rconSetOp.write("#!/bin/sh\n")
    rconSetOp.write("rcon -H 127.0.0.1 -p 25575 -P \"" + password + "\" -m /op $1\n")
    rconSetOp.close()

    rconRemoveOp = open("/usr/local/bin/mcserver/remove-op", "w")
    rconRemoveOp.write("#!/bin/sh\n")
    rconRemoveOp.write("rcon -H 127.0.0.1 -p 25575 -P \"" + password + "\" -m /deop $1\n")
    rconRemoveOp.close()

    rconStopServer = open("/usr/local/bin/mcserver/stop-server", "w")
    rconStopServer.write("#!/bin/sh\n")
    rconStopServer.write("rcon -H 127.0.0.1 -p 25575 -P \"" + password + "\" -m /stop\n")
    rconStopServer.write("rm -f server.pid\n")
    rconStopServer.close()

    # Define user right execute
    st = os.stat('/usr/local/bin/mcserver/start-rcon')
    os.chmod('/usr/local/bin/mcserver/start-rcon', st.st_mode | stat.S_IEXEC)

    st = os.stat('/usr/local/bin/mcserver/set-op')
    os.chmod('/usr/local/bin/mcserver/set-op', st.st_mode | stat.S_IEXEC)

    st = os.stat('/usr/local/bin/mcserver/remove-op')
    os.chmod('/usr/local/bin/mcserver/remove-op', st.st_mode | stat.S_IEXEC)

    st = os.stat('/usr/local/bin/mcserver/stop-server')
    os.chmod('/usr/local/bin/mcserver/stop-server', st.st_mode | stat.S_IEXEC)

    return 0

# -------------------------------------------------------------------------------------------------------------------- #

## Function to download mods
def downloadMods(optional = False):
    curseforgeToken = None
    modsFile = open('mods.json')
    modsList = json.load(modsFile)
    modsFile.close()

    versionsManifest  = urllib.request.urlopen("https://meta.fabricmc.net/v2/versions/game").read()
    jsonVersions      = json.loads(versionsManifest)
    versionChose      = os.environ['MC_VERSION']
    if versionChose == 'latest':
            versionChose = jsonVersions[0]['version']

    curseforgeMods = 0

    for mod in modsList['mandatory']:
        if mod["source"] == "curseforge":
            curseforgeMods += 1

    if curseforgeMods >= 1:
        curseforgeToken = readSecret("curseforge_token")

    print(" * Downloading mandatory mods...")
    for mod in modsList['mandatory']:
        if mod['source'] == "modrinth" and mod['enable']:
            modrinthMod(mod['name'], mod['id'], versionChose)
        
        if mod['source'] == "curseforge" and mod['enable'] and curseforgeToken is not None:
            curseforgeMod(mod['name'], mod['id'], versionChose, curseforgeToken)
        elif mod['source'] == "curseforge" and mod['enable'] and curseforgeToken is None:
            print("Mod: " + mod['name'] + ", will be ignore, because CurseForge token API has not been provided.")
            continue

        if not mod['enable']:
            continue
        
        print("")

    if optional:
        print("")
        print(" * Downloading optional mods...")
        for mod in modsList['optional']:
            if mod['source'] == "modrinth" and mod['enable']:
                modrinthMod(mod['name'], mod['id'], versionChose)
            
            if mod['source'] == "curseforge" and mod['enable'] and curseforgeToken is not None:
                curseforgeMod(mod['name'], mod['id'], versionChose, curseforgeToken)
            elif mod['source'] == "curseforge" and mod['enable'] and curseforgeToken is None:
                print("Mod: " + mod['name'] + ", will be ignore.")
                continue

            if not mod['enable']:
                continue
        
        print("")

# -------------------------------------------------------------------------------------------------------------------- #

def modrinthMod(name, id, versionMC):
    modManifest = requests.get("https://api.modrinth.com/v2/project/" + id + "/version?game_versions=[\"" + versionMC + "\"]&loaders=[\"fabric\"]")
    jsonMod     = modManifest.json()

    numberTry   = 0
    maxTry      = 3
    downloaded  = False

    filename = ""
    modUrl   = ""
    size     = 0

    for mod in jsonMod:
        if len(mod['files']) == 1:
            filename = mod['files'][0]['filename']
            modUrl   = mod['files'][0]['url']
            size     = mod['files'][0]['size']
            break
        else:
            for file in mod['files']:
                if file['primary'] == True:
                    filename = file['filename']
                    modUrl   = file['url']
                    size     = file['size']
                    break

    while numberTry < 3 and downloaded == False:
        print(" ** Downloading " + name + " (" + filename + ") #" + str(numberTry+1) + "/" + str(maxTry) + "...")
        try:
            serverJar = requests.get(modUrl, stream=True)
            if size == 0:
                size = int(serverJar.headers.get('content-length', 0))
            blockSize = 1024
            progressBar = tqdm(total=size, unit='iB', unit_scale=True)
            with open("/mcserver/mods/"+filename, 'wb') as file:
                for data in serverJar.iter_content(blockSize):
                    progressBar.update(len(data))
                    file.write(data)
                downloaded = True
            break
        except:
            numberTry += 1
        progressBar.close()


    if size != 0 and progressBar.n != size:
        print(" ** Failed")

# -------------------------------------------------------------------------------------------------------------------- #

def curseforgeMod(name, id, versionMC, token):
    getHeaders = {
        "Accept" : "application/json",
        "x-api-key" : token
    }

    modManifest = requests.get("https://api.curseforge.com/v1/mods/" + str(id) + "/files?gameVersion=" + versionMC + "&modLoaderType=fabric", headers=getHeaders)
    jsonMod     = modManifest.json()

    numberTry   = 0
    maxTry      = 3
    downloaded  = False

    filename = ""
    modUrl   = ""
    size     = 0

    if len(jsonMod['data']) == 1:
        filename = jsonMod['data'][0]['fileName']
        size     = jsonMod['data'][0]['fileLength']
        modUrl   = jsonMod['data'][0]['downloadUrl']

    while numberTry < maxTry and downloaded == False:
        print(" ** Downloading " + name + " (" + filename + ") #" + str(numberTry+1) + "/" + str(maxTry) + "...")
        try:
            serverJar = requests.get(modUrl, stream=True)
            if size == 0:
                size = int(serverJar.headers.get('content-length', 0))
            blockSize = 1024
            progressBar = tqdm(total=size, unit='iB', unit_scale=True)
            with open("/mcserver/mods/"+filename, 'wb') as file:
                for data in serverJar.iter_content(blockSize):
                    progressBar.update(len(data))
                    file.write(data)
                downloaded = True
            break
        except:
            numberTry += 1
        progressBar.close()


    if size != 0 and progressBar.n != size:
        print(" ** Failed")

# -------------------------------------------------------------------------------------------------------------------- #

## Secret for Docker
def readSecret(name, default=None, cast_to=str, autocast_name=True, getenv=True, safe=True, secrets_dir=os.path.join(root, 'run', 'secrets')):
    name_secret = name.lower() if autocast_name else name
    name_env = name.upper() if autocast_name else name

    value = None

    # try to read from secret file
    try:
        with open(os.path.join(secrets_dir, name_secret), 'r') as secret_file:
            value = secret_file.read().rstrip('\n')
    except IOError as e:
        # try to read from env if enabled
        if getenv:
            value = os.environ.get(name_env)

    # set default value if no value found
    if value is None:
        value = default

    # try to cast
    try:
        # so None wont be cast to 'None'
        if value is None:
            raise TypeError('value is None')

        # special case bool
        if cast_to == bool:
            if value not in ('True', 'true', 'False', 'false'):
                raise ValueError('value %s not of type bool' % value)
            value = 1 if value in ('True', 'true') else 0

        # try to cast
        return cast_to(value)

    except (TypeError, ValueError) as e:
        # whether exception should be thrown
        if safe:
            return default
        raise e
    
# -------------------------------------------------------------------------------------------------------------------- #

## Main
def install():
    result         = -1
    resultFirstRun = -1
    resultEula     = -1
    resultProp     = -1
    resultRcon     = -1

    #alphabet = string.ascii_letters + string.digits + string.punctuation
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))

    rconPassword = readSecret("RCON_PASSWORD", default=password)

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
        resultProp = properties(rconPassword)
    else:
        return resultProp
    
    if resultProp == 0:
        resultRcon = setRcon(rconPassword)

    print("")
    print("Server optimized!")

    return resultRcon

# -------------------------------------------------------------------------------------------------------------------- #

class GracefulKiller:
    kill_now = False
    process = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    #def exit_gracefully(self, *args):
    def exit_gracefully(self, signum, frame):
        #subprocess.Popen(["stop-server"])
        self.process.terminate()
        self.process.communicate()
        self.kill_now = True

# -------------------------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Install Minecraft Server and optimize it')
    parser.add_argument("--install", '-i', action="store_true", help="Install the server")
    parser.add_argument("--update", "-u", action="store_true", help="Update the server")
    parser.add_argument("--optional-mods", "-o", action="store_true", help="Download optional mods")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()

    mainResult    = -1
    installResult = -1
    modsResult    = -1

    if args.install:
        if len([f for f in os.listdir("/mcserver") if not f == "start-server.py"]) == 0:
            installResult = install()
        else:
            installResult = 0

    if os.environ['MC_LOADER'] != "fabric":
        modsResult = 0
        
    if os.environ['MC_LOADER'] == 'fabric' and installResult == 0:
        try:
            os.listdir('/mcserver/mods')
        except FileNotFoundError:
            os.mkdir('/mcserver/mods')
        
        if len(os.listdir('/mcserver/mods')) == 0:
            print("")
            print("Downloading mods for better performance...")
            modsResult = downloadMods(args.optional_mods)

    if installResult == 0 and modsResult == 0:
        mainResult = 0
    
    if installResult != 0:
        mainResult = installResult

    if modsResult != 0:
        mainResult = modsResult

    print("")
    print(" * Server installation status: " + str(mainResult))
    print("")

    if mainResult == 0:
        killer = GracefulKiller()
        startServer = subprocess.Popen(["python3", "/mcserver/start-server.py"], cwd="/mcserver")
        killer.process = startServer

        while not killer.kill_now:
            time.sleep(1)
    
    quit(mainResult)
