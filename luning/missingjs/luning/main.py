import logging
from pathlib import Path
import subprocess
import sys
from typing import List

import yaml

from .paths import Paths
from .services import Service, Services

logger = logging.getLogger(__name__)


def show_usage():
    service_list = Services.get_all_supported()
    usage = f"""usage: luning <service-name> OPTIONS

services:
    {', '.join(service_list)}

options:

    list                 Show instance definitions

    init <inst-name>     Create instance definition

    start <inst-name>    Start container

    stop  <inst-name>    Stop container

"""
    print(usage)


def main():
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)

    service_name = sys.argv[1]

    if not Services.is_supported(service_name):
        print(f'unknown service: {service_name}')
        sys.exit(2)

    operation = sys.argv[2]

    service = Services.new(service_name)
    if operation == 'list':
        print(' '.join(sorted(service.instance_names())))
    elif operation == 'init':
        if len(sys.argv) < 4:
            print('usage: luning <service-name> init <inst-name>')
            sys.exit(1)
        inst_name = sys.argv[3]

        if service.has_instance(inst_name):
            print(f'instance {inst_name} of service {service_name} exists')
            sys.exit(5)

        try:
            service.create_instance(inst_name)
            print(service.instance(inst_name))
        except Exception as ex:
            print(str(ex), file=sys.stderr)
            sys.exit(5)

    elif operation == 'start':
        if len(sys.argv) < 4:
            print('usage: luning <service-name> start <inst-name>')
            sys.exit(1)
        inst_name = sys.argv[3]

        container_name = f'{service_name}-{inst_name}'
        if is_container_exists(container_name):
            start_container(container_name)
        else:
            create_container(service, inst_name, container_name)
    elif operation == 'stop':
        if len(sys.argv) < 4:
            print('usage: luning <service-name> start <inst-name>')
            sys.exit(1)
        inst_name = sys.argv[3]
        container_name = f'{service_name}-{inst_name}'
        stop_container(container_name)
    else:
        print('unknown operation {operation}')
        sys.exit(4)


def stop_container(container_name):
    command = f'docker container stop {container_name}'
    subprocess.run(command, shell=True)


def create_container(service: Service, inst_name, container_name):
    if not service.has_instance(inst_name):
        print(f'instance "{inst_name}" of service "{service.name}" not found')
        sys.exit(3)
    with service.instance(inst_name).open('rb') as fp:
        info = yaml.safe_load(fp)

    data_root = Paths.data_root_dir()
    data_dir = data_root / service.name / inst_name
    data_dir.mkdir(parents=True, exist_ok=True)

    image_and_ver = info['image']
    options = ' '.join(info['options'])
    mount_vols = ' '.join(transform_mount_volumes(info['mount_volumes'], data_dir))
    cmd = info.get('cmd', '')
    command = f"docker run -d --name {container_name} {options} {mount_vols} {image_and_ver} {cmd}"
    print(command)
    subprocess.run(command, shell=True)


def start_container(name):
    command = f"docker container start {name}"
    subprocess.run(command, shell=True)


def is_container_exists(name):
    command = f"docker ps -aq -f 'name=^{name}$' | grep ."
    return subprocess.run(command, shell=True, capture_output=True).returncode == 0


def transform_mount_volumes(mvs, data_dir: Path) -> List[str]:
    return ['-v ' + s.replace('${data_dir}', str(data_dir)) for s in mvs]


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    main()

