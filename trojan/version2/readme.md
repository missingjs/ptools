# Setup instruction

## Install docker and docker-compose

* [install docker](https://docs.docker.com/engine/install/ubuntu/)
* [install docker compose](https://docs.docker.com/compose/install/compose-plugin/#installing-compose-on-linux-systems)

## Prepare configuartion
1. **create config script**

```bash
$ cp _setup_env.sh setup_env.sh
```

2. **edit**

## generate docker compose file

```bash
$ ./generate.sh
```

This script will create volumes under `$volume_directory` (defined in `setup_env.sh`), and finally generate `docker-compose.yml` in current directory.

## Register SSL certificate

Register SSL certificate in Letsencrypt (with certbot) before launch docker containers. It only needs to be run once.

```bash
$ ./cert.sh register
```

## Start service

```bash
$ docker compose up -d
```

It must be run under current directory, where `docker-compose.yml` was settled.

## Setup web content

1. Prepare your web content. Put Each site in it's own directory, and use `index.html` as index page. Then put these sites under one top directory.

2. Set `web_source` (in `setup_env.sh`) as the top directory. If you want to exclude some sites, set the paths to `web_source_blacklist`. All paths set to both variables separated by colon.

3. Deploy web content. 

```bash
$ ./webcont.sh setup
```

### Recommanded static web site templates
* [website-templates](https://github.com/learning-zone/website-templates), size of more than 600M
* [template](https://github.com/toidicode/template), size of about 2.4G

You can call this command from crontab. The program will choose one site randomly, then copy all contents to `$volume_directory/var/www/html/`, where the nginx server can access.

## Setup crontab

```bash
$ ./cron-setup.sh
```

It'll append job to crontab file, so you'd better check it manually after this script executed.

# Utility commands

These commands will be executed in scripts introduced in previous chapters. Normally there's no need to execute by hand.

## Stop service

```bash
$ docker compose down
```

## Renew certificate

```bash
$ ./cert.sh renew
```

You can renew certificate every two months. Nomally through crontab. See [Setup crontab](#Setup crontab)

