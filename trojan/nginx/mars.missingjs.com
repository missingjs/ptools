server {
    listen 127.0.0.1:80;

    server_name 104.243.27.129;

    return 301 https://mars.missingjs.com$request_uri;
}

server {
    listen 0.0.0.0:80;
    listen [::]:80;

    server_name _;

    return 301 https://$host$request_uri;
}
