from pathlib import Path
import shutil
from typing import List

from .paths import Paths


class Service:

    def __init__(self, name: str):
        self.name_ = name

    @property
    def name(self) -> str:
        return self.name_

    @property
    def directory(self) -> Path:
        return Paths.service_dir() / self.name

    def instance_names(self) -> List[str]:
        return [p.name[:-5] for p in self.all_instances()]

    def all_instances(self) -> List[Path]:
        return list(self.directory.glob('*.yaml'))

    def instance(self, inst_name: str) -> Path:
        return self.directory / f'{inst_name}.yaml'

    def has_instance(self, inst_name: str) -> bool:
        return self.instance(inst_name).exists()

    def template(self) -> Path:
        return Paths.template_dir() / f'{self.name}.template.yaml'

    def create_instance(self, inst_name: str) -> None:
        if self.has_instance(inst_name):
            raise Exception(f'instance {inst_name} exists')
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=False)
        src = str(self.template())
        dst = str(self.instance(inst_name))
        shutil.copyfile(src, dst) 


class Services:
    
    @classmethod
    def get_all_supported(cls) -> List[str]:
        suffix = '.template.yaml'
        return [s.name[:-len(suffix)] for s in Paths.get_template_files() if str(s).endswith(suffix)]

    @classmethod
    def new(self, name: str) -> Service:
        return Service(name)

    @classmethod
    def is_supported(cls, name: str) -> bool:
        p = Paths.template_dir() / f'{name}.template.yaml'
        return p.exists()

    