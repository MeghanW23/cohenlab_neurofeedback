import logging
import re
from collections.abc import Iterable
from contextlib import contextmanager
from os import fspath, makedirs
from pathlib import Path
from shutil import copyfileobj, rmtree
from tempfile import mkdtemp
from zipfile import ZipFile

from tqdm.auto import tqdm
from tqdm.utils import CallbackIOWrapper

log = logging.getLogger(__name__)


def create_dir(pth):
    """Equivalent of `mkdir -p`"""
    pth = Path(pth)
    if not pth.is_dir():
        try:
            makedirs(fspath(pth))
        except Exception as exc:
            log.warning("cannot create:%s:%s", pth, exc)


def is_iter(x):
    return isinstance(x, Iterable) and not isinstance(x, (str, bytes))


def hasext(fname, ext):
    if not is_iter(ext):
        ext = (ext,)
    ext = (("" if i[0] == "." else ".") + i.lower() for i in ext)
    return fspath(fname).lower().endswith(tuple(ext))


@contextmanager
def tmpdir(*args, **kwargs):
    d = mkdtemp(*args, **kwargs)
    yield d
    rmtree(d)


def extractall(fzip, dest, desc="Extracting"):
    """zipfile.Zipfile(fzip).extractall(dest) with progress"""
    dest = Path(dest).expanduser()
    with ZipFile(fzip) as zipf, tqdm(
            desc=desc,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
    ) as pbar:
        for i in zipf.infolist():
            if not getattr(i, "file_size", 0): # directory
                zipf.extract(i, fspath(dest))
            else:
                (dest / i.filename).parent.mkdir(parents=True, exist_ok=True)
                with zipf.open(i) as fi, (dest / i.filename).open(mode="wb") as fo:
                    copyfileobj(CallbackIOWrapper(pbar.update, fi), fo)
                mode = (i.external_attr >> 16) & 0o777
                if mode:
                    (dest / i.filename).chmod(mode)
                    log.debug(oct((i.external_attr >> 16) & 0o777))


def nsort(fnames):
    """Sort a file list, automatically detecting embedded numbers"""
    def path2parts(fname):
        parts = re.split(r"([0-9][0-9.]*e[-+][0-9]+|[0-9]+\.[0-9]+|[0-9]+)", fname)
        parts[1::2] = map(float, parts[1::2])
        return parts

    return sorted(fnames, key=path2parts)
