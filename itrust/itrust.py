#!/usr/bin/env python3
import configparser
import sys

from docopt import docopt

from fabric.api import env, run, execute

def deploy_ssh_config(hosts):
    cmd = '''
srcfile=~/.ssh/config
[ -e $srcfile ] || touch $srcfile
bakfile=~/.ssh/config.bak.$(date +%Y_%m_%d_%H_%M_%S)
cp $srcfile $bakfile
python3 << EOF
import os
cfile = "$srcfile"
hosts = {hosts}
host_alias = set([k['name'] for k in hosts])
tmpfile = cfile + '.itemp'
write_enable = True
with open(cfile, 'rt') as fp, open(tmpfile, 'wt') as ofp:
    for line in fp:
        i = line.find('Host ')
        if i > -1:
            alias = line[i+5:].strip()
            write_enable = (alias not in host_alias)
        if write_enable:
            ofp.write(line)
with open(tmpfile, 'at') as fp:
    fp.write('\\n')
    for h in hosts:
        fp.write('Host {{}}\\n'.format(h['name']))
        fp.write('    HostName {{}}\\n'.format(h['ip']))
        fp.write('    Port {{}}\\n'.format(h['port']))
        fp.write('    User {{}}\\n'.format(h['user']))
        fp.write('    StrictHostKeyChecking no\\n')
        fp.write('    UserKnownHostsFile /dev/null\\n')
        fp.write('\\n')
os.rename(tmpfile, cfile)
EOF
'''
    run(cmd.format(hosts = hosts))

def collect_keys():
    cmd = '''
[ -f ~/.ssh/id_rsa ] || ssh-keygen -t rsa -q -N "" -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub
'''
    k = run(cmd)
    return k.stdout.strip()


def deploy(keys):
    cmd = '''
a=~/.ssh/authorized_keys
b=~/.ssh/auth_key_temp
[ -e $a ] && cp $a $b
cat >> $b << EOF
{k}
EOF
sort $b | uniq > $a 
rm $b
'''
    run(cmd.format(k = keys))

def main():
    '''
usage:
    itrust.py -f <file> [--ssh-config]

options:
    -f <file>      host file, ini format
    --ssh-config   generate ~/.ssh/config
'''
    args = docopt(main.__doc__, version = 'v1.0')

    gen_config = args['--ssh-config']

    ini_file = args['-f']
    config = configparser.ConfigParser()
    config.read(ini_file)

    hosts = parse_hosts(config)
    for h in hosts:
        hs = '{}@{}:{}'.format(h['user'], h['ip'], h['port'])
        env.hosts.append(hs)
        env.passwords[hs] = h['pass']

    env.parallel = True

    p = execute(collect_keys)
    keys = '\n'.join(p.values())
    execute(deploy, keys)

    if gen_config:
        execute(deploy_ssh_config, hosts)


def parse_hosts(config):
    hosts = []
    g = config['global']
    g_user = g.get('username')
    g_pass = g.get('password')
    g_port = g.get('port')
    for h in filter(lambda x: x != 'global', config.sections()):
        ip = config[h]['ip']
        username = config[h].get('username') or g_user
        password = config[h].get('password') or g_pass
        port = config[h].get('port') or g_port
        hosts.append({
            'ip': ip,
            'name': h,
            'port': port,
            'user': username,
            'pass': password
        })
    return hosts


if __name__ == '__main__':
    main()
