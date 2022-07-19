## install docker and docker-compose
    * [install docker](https://docs.docker.com/engine/install/ubuntu/)
    * [install docker compose](https://docs.docker.com/compose/install/compose-plugin/#installing-compose-on-linux-systems)

## prepare configuartion
```bash
cp _setup_env.sh setup_env.sh
```
then edit with correct infomation

## generate docker compose file
```bash
./generate.sh
```

## setup certificate
```bash
./cert.sh register
```
only needs to be run once

## start service
```bash
docker compose up -d
```
must be run under current directory

## stop service
```bash
docker compose down
```
must be run under current directory

## renew certificate
```bash
./cert.sh renew
```

