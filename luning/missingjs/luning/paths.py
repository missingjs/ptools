import os
from pathlib import Path
from typing import List


class Paths:

    @classmethod
    def project_dir(cls) -> Path:
        h = os.environ.get('LUNING_HOME')
        if h is not None:
            return Path(h)

        from missingjs import luning
        return Path(f'{luning.__file__}/../../..').resolve()

    @classmethod
    def project_dir_s(cls) -> str:
        return str(cls.project_dir_p())

    @classmethod
    def service_dir(cls) -> Path:
        return cls.project_dir() / 'services'

    @classmethod
    def service_dir_s(cls) -> str:
        return str(cls.service_dir())

    @classmethod
    def template_dir(cls) -> Path:
        return cls.project_dir() / 'templates'

    @classmethod
    def template_dir_s(cls) -> str:
        return str(cls.template_dir())

    @classmethod
    def get_template_files_s(cls) -> List[str]:
        return [str(p) for p in cls.get_template_files()]

    @classmethod
    def get_template_files(cls) -> List[Path]:
        return list(Path(cls.template_dir()).glob('*.template.yaml'))

    @classmethod
    def data_root_dir(cls) -> Path:
        return Path(cls.data_root_dir_s())

    @classmethod
    def data_root_dir_s(cls) -> str:
        return os.environ.get('LUNING_DATA_ROOT') or f'{os.path.expanduser("~")}/.luning/data'
