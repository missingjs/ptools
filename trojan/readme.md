# Quick start

* infomation setup: `cp _setup_env.sh setup_env.sh`, then set the variables in it
* build image: `./build.sh`
* register cert (first time): `./cert.sh register`
* create service container: `./control.sh create`

# Setup auto renew certificate
* renew certificate: `./cert.sh renew`, restart trojan service: `./control.sh restart`, invoke these commands in crontab every two months
