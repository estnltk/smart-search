# Kiirushinnang (ainult veebiliides ilma lemmatiseerijata)

Märkused:
* Lõplikud kiirushinnagud: [docker+gunicorn+flask](#tulemused-2)
* Gunicorn paneb aega otsa, aga annab skaleeruvuse

## Riist- ja tarkvara

|   |   |
|---|---|
|Hardware Model|HP EliteBook 840 G3|
|Mälu|16,0 GiB|
|Protsessor|Intel® Core™ i5-6200U CPU @ 2.30GHz × 4|
|OS Name|Ubuntu 22.04.1 LTS|
|OS Type|64-bit|

## Kiirushinnangud

### flask

#### Veebiserveri käivitamine

```bash
venv/bin/python3 flask_morf.py
```

#### Testprogrammi käivitamine

```bash
time ./test.sh 5000
```

#### Tulemused

|real|user|sys|1 päring keskmiselt|
|----|----|---|---|
|0m2,827s|0m0,489s|0m0,583s|0.00583s|
|0m2,694s|0m0,390s|0m0,386s|0.00386s|
|0m2,586s|0m0,338s|0m0,372s|0.00372s|

### gunicorn+flask

#### Veebiserveri käivitamine

```bash
/usr/bin/tini -s -- venv/bin/gunicorn --bind=0.0.0.0:7000 "--workers=1" "--timeout=30" "--worker-class=sync" --worker-tmp-dir=/dev/shm flask_morf:app
```

#### Testprogrammi käivitamine

```bash
time ./test.sh 7000
```

#### Tulemused

|real|user|sys|1 päring keskmiselt|
|----|----|---|---|
|0m3,127s|0m1,593s|0m1,282s|0.06282s|
|0m2,918s|0m1,119s|0m1,081s|0.06081s|
|0m3,103s|0m2,893s|0m2,478s|0.12478s|

### docker+gunicorn+flask

#### Veebiserveri käivitamine

```bash
docker build -t test_time .
docker run -p 7000:7000 test_time
```

#### Testprogrammi käivitamine

```bash
time ./test.sh 7000
```

#### Tulemused

|real|user|sys|1 päring keskmiselt|
|----|----|---|---|
|0m3,566s|0m5,040s|0m4,564s|0.24564s|
|0m3,788s|0m6,064s|0m5,341s|0.30341s|
|0m3,770s|0m5,917s|0m5,822s|0.30822s|



