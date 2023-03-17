#!/bin/bash

export VERSION=2023.03.14
#--------------------------------
export NAME=lemmatiseerija

kubectl create deployment ${NAME} --image=tilluteenused/${NAME}:${VERSION}
# kubectl get pods | grep ${NAME} # lemmatiseerija deployment peab nüüd olemas olema

kubectl expose deployment ${NAME} --type=LoadBalancer --port=7000
# kubectl get service ${NAME}  # lemmatiseerija service peab nüüd olemas olema

# näited: lemmatiseerija veebiteenus peab nüüd töötama
curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"peeti keaks","params":{"vmetltjson":[]}}' \
    $(kubectl get service/lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7000/process|jq

#--------------------------------
export NAME=demo-lemmatiseerija # NB! konteineri nimes on alakriips(ud)

kubectl create deployment ${NAME} --image=tilluteenused/${NAME//-/_}:${VERSION}
# kubectl get pods | grep ${NAME} # deployment peab nüüd olemas olema

kubectl expose deployment ${NAME} --type=LoadBalancer --port=7777
# kubectl get service ${NAME}  # service peab nüüd olemas olema

#kubectl set env  deployment/${NAME} LEMMATIZER_PORT=7000 # seda pole vaja, see juba on vaikimisi
kubectl set env  deployment/${NAME} LEMMATIZER_IP=$(kubectl get service/lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"')
# kubectl set env  deployment/${NAME} --list # keskonnamuutuja peab nüüd olema defineeritud
# kubectl logs $(kubectl get pods -o name|grep pod/${NAME}) # logist peab olema näha, et demo teab lemmatiseerija IPd

# näited: lemmatiseerimise demo peab nüüd töötama
google-chrome http://$(kubectl get service/demo-lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7777/paring
google-chrome http://$(kubectl get service/demo-lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7777/lemmad
google-chrome http://$(kubectl get service/demo-lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7777/json

#--------------------------------
export NAME=demo-smartsearch-webpage # NB! konteineri nimes on alakriips(ud)

kubectl create deployment ${NAME} --image=tilluteenused/${NAME//-/_}:${VERSION}
# kubectl get pods | grep ${NAME} # deployment peab nüüd olemas olema

kubectl expose deployment ${NAME} --type=LoadBalancer --port=7070
# kubectl get service ${NAME}  # service peab nüüd olemas olema

#kubectl set env  deployment/${NAME} LEMMATIZER_PORT=7000 # seda pole vaja, see juba on vaikimisi
kubectl set env  deployment/${NAME} LEMMATIZER_IP=$(kubectl get service/lemmatiseerija --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"')
# kubectl set env  deployment/${NAME} --list # keskonnamuutuja peab nüüd olema defineeritud
# kubectl logs $(kubectl get pods -o name|grep pod/${NAME}) # logist peab olema näha, et demo teab lemmatiseerija IPd

# näited: tekstiotsingu demo peab nüüd töötama 
google-chrome http://$(kubectl get service/demo-smartsearch-webpage --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7070/tekstid

google-chrome http://$(kubectl get service/demo-smartsearch-webpage --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7070/otsi
google-chrome http://$(kubectl get service/demo-smartsearch-webpage --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7070/otsils

google-chrome http://$(kubectl get service/demo-smartsearch-webpage --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7070/otsijson
google-chrome http://$(kubectl get service/demo-smartsearch-webpage --output='jsonpath="{.status.loadBalancer.ingress[0].ip}"'|tr -d '"'):7070/otsilsjson