"""Thin wrapper around dcm2niix binary"""
__author__ = "Casper da Costa-Luis <https://github.com/casperdcl>"
__date__ = "2022"
# version detector. Precedence: installed dist, git, 'UNKNOWN'
try:
    from ._dist_ver import __version__
except ImportError:  # pragma: nocover
    try:
        from setuptools_scm import get_version

        __version__ = get_version(root="../..", relative_to=__file__)
    except (ImportError, LookupError):
        __version__ = "UNKNOWN"
__all__ = ['bin', 'bin_path', 'main']

import os
import platform
from pathlib import Path

system = platform.system()
bin_name = "dcm2niix" + (".exe" if system == 'Windows' else "")
# 1: builtin
bin_path = Path(__file__).resolve().parent / bin_name

if not bin_path.is_file():
    p = Path(os.getenv('DCM2NIIX', ''))  # 2: env PATH
    if p.is_file():
        bin_path = p
    else:  # 3: download
        from miutil.fdio import extractall
        from miutil.web import urlopen_cached
        tag = {'Linux': "lnx", 'Darwin': "mac", 'Windows': "win"}[system]
        url = f"https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_{tag}.zip"
        if system == 'Darwin':
            raise NotImplementedError(f"Please download & install {url} first")
        with urlopen_cached(url, bin_path.parent) as fd:
            extractall(fd, bin_path.parent)
            assert bin_path.is_file()

bin = str(bin_path)


def main(args=None):
    if args is None:
        import sys
        args = sys.argv[1:]
    from subprocess import run
    run([bin] + args)
