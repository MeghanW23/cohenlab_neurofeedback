import logging
from os import W_OK, access, path, remove
from shutil import copyfileobj

try:
    from urllib.request import urlopen
except ImportError: # py27
    from urllib import urlopen
try:
    from urllib.parse import urlparse
except ImportError: # py27
    from urlparse import urlparse

import requests
from tqdm.auto import tqdm

from .fdio import Path, create_dir, fspath

log = logging.getLogger(__name__)


def get_file(fname, origin, cache_dir=None, chunk_size=None):
    """
    Downloads a file from a URL if it not already in the cache.
    By default the file at the url `origin` is downloaded to the
    cache_dir `~/.miutil`, and given the filename `fname`.
    The final location of a file
    `foo.zip` would therefore be `~/.miutil/foo.zip`.
    Vaguely based on:
    https://github.com/keras-team/keras/blob/master/keras/utils/data_utils.py

    Args:
      fname (str): Name of the file. If an absolute path
        `/path/to/file.txt` is specified the file will be saved at that
        location.
      origin (str): Original URL of the file.
      cache_dir (str): Location to store cached files, when None it
        defaults to `~/.miutil`.
    Returns:
      str: Path to the downloaded file
    """
    if cache_dir is None:
        cache_dir = path.join("~", ".miutil")
    cache_dir = path.expanduser(fspath(cache_dir))
    create_dir(cache_dir)
    if not access(cache_dir, W_OK):
        cache_dir = path.join("/tmp", ".miutil")
        create_dir(cache_dir)

    fpath = path.join(cache_dir, fname)

    if not path.exists(fpath):
        log.debug("Downloading %s from %s", fpath, origin)
        try:
            d = requests.get(origin, stream=True)
            with tqdm(
                    total=float(d.headers.get("Content-length") or 0),
                    desc=fname,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    leave=False,
            ) as fprog:
                with open(fpath, "wb") as fo:
                    for chunk in d.iter_content(chunk_size=chunk_size):
                        fo.write(chunk)
                        fprog.update(len(chunk))
                fprog.total = fprog.n
                fprog.refresh()
        except (Exception, KeyboardInterrupt):
            if path.exists(fpath):
                remove(fpath)
            raise

    return fpath


def urlopen_cached(url, outdir, fname=None, mode="rb"):
    """
    Download `url` to `outdir/fname`.
    Cache based on `url` at `outdir/fname`.url

    Args:
      url (str): source
      outdir (path-like): destination
      fname (str): optional, auto-detected from `url` if not given
      mode (str): for returned file object
    Returns:
      file
    """
    outdir = Path(outdir).expanduser()
    outdir.mkdir(exist_ok=True)
    if fname is None:
        fname = Path(urlparse(url).path).name
    fout = outdir / fname
    cache = outdir / f"{fspath(fname)}.url"
    if not fout.is_file() or not cache.is_file() or cache.read_text().strip() != url:
        fi = urlopen(url)
        with fout.open("wb") as raw:
            with tqdm.wrapattr(raw, "write", total=getattr(fi, "length", None)) as fo:
                copyfileobj(fi, fo)
        try:
            cache.write_text(url)
        except TypeError:
            cache.write_text(url.decode("U8"))
    return fout.open(mode)
