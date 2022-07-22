import json
import os.path
import subprocess
import sys

# server_config = {
#     'myserver': {
#         'remote_addr': 'abc.example.com',
#         'password': ['mypassword']
#     }
# }
 
def main():
    base_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.basename(os.path.realpath(__file__))

    if len(sys.argv) < 2:
        print(f'usage: python3 {file_name} <server-id>', file=sys.stderr)
        sys.exit(1)

    server_id = sys.argv[1]

    if server_id not in server_config:
        print(f'server "{server_id}" not exist', file=sys.stderr)
        sys.exit(2)

    base_config.update(server_config[server_id])

    gen_file = os.path.join(base_path, 'config-auto-generate.json')
    with open(gen_file, 'wt') as ofp:
        json.dump(base_config, ofp, indent=4)

    executable = os.path.join(base_path, 'trojan')
    print(f'executable: {executable}')
    print(f'config: {gen_file}')
    subprocess.run([executable, '-c', gen_file])

base_config = json.loads("""
{
    "run_type": "client",
    "local_addr": "127.0.0.1",
    "local_port": 1080,
    "remote_addr": "",
    "remote_port": 443,
    "password": [
        ""
    ],
    "log_level": 1,
    "ssl": {
        "verify": true,
        "verify_hostname": true,
        "cert": "",
        "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:AES128-SHA:AES256-SHA:DES-CBC3-SHA",
        "cipher_tls13": "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384",
        "sni": "",
        "alpn": [
            "h2",
            "http/1.1"
        ],
        "reuse_session": true,
        "session_ticket": false,
        "curves": ""
    },
    "tcp": {
        "no_delay": true,
        "keep_alive": true,
        "reuse_port": false,
        "fast_open": false,
        "fast_open_qlen": 20
    }
}
""")

if __name__ == '__main__':
    main()

