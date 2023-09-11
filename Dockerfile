FROM alpine:latest

LABEL Author="Chucky2401"
LABEL Description="Minecraft vanilla or fabric Server"
LABEL Version="1.0"

RUN \
    mkdir /mcserver ; \
    mkdir -m 755 /usr/local/bin/mcserver ; \
    mkdir /entrypoint

COPY --chmod=755 entrypoint/docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
COPY --chmod=755 entrypoint/download-minecraft.py /entrypoint/download-minecraft.py
COPY --chmod=444 entrypoint/mods.json /entrypoint/mods.json
COPY --chmod=755 files/start-server.py /mcserver/start-server.py

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
ENV PATH="${PATH}:/usr/local/bin/mcserver"

HEALTHCHECK --interval=1m --timeout=5s --start-period=30s --retries=2 \
    CMD ps ax | grep -v grep | grep $(cat /mcserver/server.pid) || exit 1

WORKDIR /entrypoint
ENTRYPOINT [ "python3", "download-minecraft.py" ]

CMD [ "--install" ]
