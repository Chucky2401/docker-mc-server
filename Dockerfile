FROM alpine:latest

LABEL Author="Chucky2401"
LABEL Description="Minecraft Server"
LABEL Version="0.1"

#ADD src/* /root/
#COPY docker-entrypoint.sh /usr/local/bin/

RUN \
    cd / ; \
    echo "*** Update APK ***" ; \
    apk update ; apk upgrade -y ; \
    echo "*** Install OpenJDK ***" ; \
    apk add openjdk17-jdk ; \
    echo "*** Install Python3" ; \
    apk add python3 ; ln -sf python3 /usr/bin/python ; \
    echo "*** Python 3 Module" ; \
    apk add py3-pip ; pip3 install tqdm requests ; \
    echo "*** Clean APK ***" ; \
    apk cache clean ; \
    echo "**** Create directory ***" ; \
    mkdir /mcserver

EXPOSE 25565
VOLUME /mcserver

ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

CMD ["sh"]
