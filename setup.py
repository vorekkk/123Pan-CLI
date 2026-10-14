"""Copy the single canonical Skill into wheel runtime resources."""
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPy(build_py):
    def run(self):
        super().run()
        source = Path(__file__).parent / 'skills' / 'pan123-cli'
        target = Path(self.build_lib) / 'pan123_cli' / 'skill_data'
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)


setup(cmdclass={'build_py': BuildPy})
