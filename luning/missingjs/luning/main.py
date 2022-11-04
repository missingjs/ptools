import argparse
import logging
import os.path
from pathlib import Path
import subprocess
import sys
from typing import List

import yaml

logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 3:
        print('usage: luning <service-name> OPTIONS')
        sys.exit(1)

    service_name = sys.argv[1]

    service_list = list_services()
    if service_name not in service_list:
        print(f'unknown service: {service_name}')
        sys.exit(2)

    operation = sys.argv[2]

    if operation == 'list':
        print(' '.join(conf.name[:-5] for conf in iter_instance_config(service_name)))
    elif operation == 'start':
        if len(sys.argv) < 4:
            print('usage: luning <service-name> start <inst-name>')
            sys.exit(1)
        inst_name = sys.argv[3]

        container_name = f'{service_name}-{inst_name}'
        if is_container_exists(container_name):
            start_container(container_name)
        else:
            create_container(service_name, inst_name, container_name)
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


def create_container(service_name, inst_name, container_name):
    conf = get_instance_config(service_name, inst_name)
    if not conf.exists():
        print(f'instance "{inst_name}" of service "{service_name}" not found')
        sys.exit(3)
    with conf.open('rb') as fp:
        info = yaml.safe_load(fp)

    data_root = Path(data_root_dir())
    data_dir = data_root / service_name / inst_name
    data_dir.mkdir(parents=True, exist_ok=True)

    image_and_ver = info['image']
    options = ' '.join(info['options'])
    mount_vols = ' '.join(transform_mount_volumes(info['mount_volumes'], data_dir))
    cmd = info['cmd']
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


def data_root_dir():
    return os.environ.get('LUNING_DATA_ROOT') or f'{os.path.expanduser("~")}/.luning/data'


def get_instance_config(service_name, inst_name):
    return Path(service_dir()) / service_name / f'{inst_name}.yaml'


def iter_instance_config(service_name):
    for f in (Path(service_dir())/service_name).iterdir():
        if f.name.endswith('.yaml'):
            yield f


def list_services():
    return [f.name for f in Path(service_dir()).iterdir()]


def project_dir():
    h = os.environ.get('LUNING_HOME')
    if h is not None:
        return h

    return str(Path(__file__).parent.parent.parent)


def service_dir():
    return f'{project_dir()}/services'


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    main()

