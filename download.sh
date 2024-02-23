#!/bin/bash

set +x
set +e

OUT="./content"

mkdir "$OUT" || true
rm master.zip || true

wget https://github.com/betagouv/beta.gouv.fr/archive/refs/heads/master.zip
unzip master.zip
mv beta.gouv.fr-master/content/_startups $OUT/startups-beta
rm master.zip
rm -rf beta.gouv.fr-master

wget https://github.com/betagouv/doc.incubateur.net-communaute/archive/refs/heads/master.zip
unzip master.zip
mv doc.incubateur.net-communaute-master $OUT/documentation-beta
rm master.zip
rm -rf doc.incubateur.net-communaute-master
