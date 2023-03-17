# MINIKUBEmega toimetamine

## Installimine

[Installimise juhend veebis](https://minikube.sigs.k8s.io/docs/start/)

Linuxi korral midagi sellist:

```cmdline
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube kubectl -- get po -A
```

## Keskkonnamuutujate seadistamine (soovituslik)

Lisa ~/.bashrc või ~/.zshrc faili:

```
alias kubectl="minikube kubectl --"
# kui tahta .yaml/.json konfifaile käsitsi redigeerida ja ei ole suurem vi fänn, siis üks neist
#export KUBE_EDITOR=nano
#export KUBE_EDITOR='code --wait'
```

## Käivita vajalikud teenused

```cmdline
minikube start
```

```cmdline
minikube tunnel
```

## Lemmatiseerija- ja demokonteinerite installimine, konfimine jms

Vaata skripti ```lykka_pysti.sh```


