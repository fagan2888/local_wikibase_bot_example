#!/usr/bin/env bash


# set config in config.py !!
source config.sh

mkdir $NAME
cd $NAME

wget https://raw.githubusercontent.com/wmde/wikibase-docker/master/docker-compose.yml

## change the ports
cat docker-compose.yml | sed -e "s/8181/$WIKIBASE_PORT/g" | sed -e "s/8282/$WDQS_FRONTEND/g" | sed -e "s/8989/$PROXY/g" > docker-compose.yml_ && mv -f docker-compose.yml_ docker-compose.yml


# start
docker-compose pull
docker-compose up -d

# get the docker id
# ID=$(docker inspect wikibasedockertmp_wikibase_1 | jq '.[0]["Id"]')
ID=$(docker ps | grep ${NAME}_wikibase_1 | cut -f1 -d' ')
# create a new bot account
sleep 10
docker exec -it $ID php /var/www/html/maintenance/createAndPromote.php ${USER} ${PASS} --bot

cd ..
