#!/usr/bin/env python
"""Usage:
  mbeautify <mfile>...

Arguments:
  <mfile>  : Path to `*.m` file
"""
import logging
from functools import wraps
from os import path
from zipfile import ZipFile

from argopt import argopt
from tqdm.contrib import tmap

from ..web import get_file
from . import get_engine, lru_cache

log = logging.getLogger(__name__)
MBEAUTIFIER_REV = "6005eeb8b17be8a40be32cea73005cf0d36de4e9"


@lru_cache()
@wraps(get_engine)
def ensure_mbeautifier(*args, **kwargs):
    eng = get_engine(*args, **kwargs)
    fn = get_file(
        f"MBeautifier-{MBEAUTIFIER_REV[:7]}.zip",
        f"https://github.com/davidvarga/MBeautifier/archive/{MBEAUTIFIER_REV}.zip",
    )
    outpath = path.join(path.dirname(fn), f"MBeautifier-{MBEAUTIFIER_REV}")
    if not path.exists(outpath):
        with ZipFile(fn) as fd:
            fd.extractall(path=path.dirname(outpath))
    assert path.exists(outpath), "Error extracting"
    log.debug("adding wrappers (%s) to MATLAB path", outpath)
    eng.addpath(outpath, nargout=0)
    return eng


def main(*args, **kwargs):
    args = argopt(__doc__).parse_args(*args, **kwargs)
    logging.basicConfig(level=logging.INFO)
    eng = ensure_mbeautifier()
    formatter = eng.MBeautify.formatFileNoEditor

    for fn in tmap(path.abspath, args.mfile):
        log.debug("file:%s", fn)
        try:
            formatter(fn, fn, nargout=0)
        except Exception as exc:
            log.error("file:%s:\n%s", fn, exc)


if __name__ == "__main__": # pragma: no cover
    main()
