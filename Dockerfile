FROM alpine:latest

LABEL Author="Chucky2401"
LABEL Description="Minecraft Server"
LABEL Version="0.1"

RUN \
    mkdir /mcserver ; \
    mkdir -m 755 /usr/local/bin/mcserver ; \
    mkdir /entrypoint

COPY --chmod=755 entrypoint/docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
COPY --chmod=755 entrypoint/download-minecraft.py /entrypoint/download-minecraft.py
COPY --chmod=444 entrypoint/mods.json /entrypoint/mods.json
COPY files/profile /etc/profile

RUN \
    echo "*** Update APK ***" ; \
    apk update ; apk upgrade -y ; \
    echo "*** Install OpenJDK ***" ; \
    apk add openjdk17-jdk ; \
    echo "*** Install Python3" ; \
    apk add python3 ; ln -sf python3 /usr/bin/python ; \
    echo "*** Python 3 Module" ; \
    apk add py3-pip ; pip3 install tqdm requests ; \
    echo "*** Add RCON" ; \
    apk add rcon ; \
    echo "*** Clean APK ***" ; \
    apk cache clean

EXPOSE 25565 25575
VOLUME /mcserver

ENV MC_LOADER=vanilla
ENV MC_VERSION=latest
ENV MC_MIN_MEM=1G
ENV MC_MAX_MEM=1G

ENTRYPOINT [ "sh", "/entrypoint/docker-entrypoint.sh" ]

CMD [ "--install" ]
