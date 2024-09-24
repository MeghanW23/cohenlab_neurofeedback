import logging
import os
import re
import sys
from ast import literal_eval
from functools import lru_cache
from os import getenv, path
from platform import system
from subprocess import STDOUT, CalledProcessError, check_output
from textwrap import dedent

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

from ..fdio import Path, extractall, fspath, tmpdir

__all__ = ["get_engine"]
IS_WIN = any(sys.platform.startswith(i) for i in ["win32", "cygwin"])
MATLAB_RUN = "matlab -nodesktop -nosplash -nojvm".split()
if IS_WIN:
    MATLAB_RUN += ["-wait", "-log"]
log = logging.getLogger(__name__)
_MCR_URL = {
    99: ("https://ssd.mathworks.com/supportfiles/downloads/R2020b/Release/4"
         "/deployment_files/installer/complete/"),
    713: "https://www.fil.ion.ucl.ac.uk/spm/download/restricted/utopia/MCR/"}
MCR_ARCH = {"Windows": "win64", "Linux": "glnxa64", "Darwin": "maci64"}[system()]
MCR_URL = {
    "Windows": {
        99: _MCR_URL[99] + "win64/MATLAB_Runtime_R2020b_Update_4_win64.zip",
        713: _MCR_URL[713] + "win64/MCRInstaller.exe"},
    "Linux": {
        99: _MCR_URL[99] + "glnxa64/MATLAB_Runtime_R2020b_Update_4_glnxa64.zip",
        713: _MCR_URL[713] + "glnxa64/MCRInstaller.bin"},
    "Darwin": {
        99: _MCR_URL[99] + "maci64/MATLAB_Runtime_R2020b_Update_4_maci64.dmg.zip",
        713: _MCR_URL[713] + "maci64/MCRInstaller.dmg"}}[system()] # yapf: disable


class VersionError(ValueError):
    pass


def check_output_u8(*args, **kwargs):
    return check_output(*args, **kwargs).decode("utf-8").strip()


def env_prefix(key, dir):
    try:
        os.environ[key] = f"{os.environ[key]}{os.pathsep}{fspath(dir)}"
    except KeyError:
        os.environ[key] = fspath(dir)


@lru_cache()
def get_engine(name=None):
    try:
        from matlab import engine
    except ImportError:
        try:
            log.warning(
                dedent("""\
                Python could not find the MATLAB engine.
                Attempting to install automatically."""))
            log.debug(_install_engine())
            log.info("installed MATLAB engine for Python")
            from matlab import engine
        except CalledProcessError:
            raise ImportError(
                dedent("""\
                Please install MATLAB and its Python module.
                See https://www.mathworks.com/help/matlab/matlab_external/\
install-the-matlab-engine-for-python.html
                or
                https://www.mathworks.com/help/matlab/matlab_external/\
install-matlab-engine-api-for-python-in-nondefault-locations.html
                It's likely you need to do:

                cd "{setup_dir}"
                {exe} -m pip install 'setuptools<66'
                {exe} setup.py build --build-base="BUILDDIR" install --prefix="{pre}"

                - Fill in any temporary directory name for BUILDDIR
                  (e.g. /tmp/builddir).

                Alternatively, use `get_runtime()` instead of `get_engine()`.
                """).format(
                    setup_dir=path.join(matlabroot(default="matlabroot"), "extern", "engines",
                                        "python"), exe=sys.executable, pre=sys.prefix))
    log.debug("Starting MATLAB")
    try:
        eng = engine.connect_matlab(name=name or getenv("SPM12_MATLAB_ENGINE", None))
    except engine.EngineError:
        log.error("MATLAB hasn't properly cleaned up. Try restarting your computer.")
        raise
    log.debug("MATLAB started")
    return eng


def _matlab_run(command, jvm=False, auto_exit=True):
    if auto_exit and not command.endswith("exit"):
        command = command + ", exit"
    return check_output_u8(MATLAB_RUN + ([] if jvm else ["-nojvm"]) + ["-r", command],
                           stderr=STDOUT)


def matlabroot(default=None):
    if IS_WIN:
        try:
            res = _matlab_run("display(matlabroot);")
        except (CalledProcessError, FileNotFoundError):
            if default:
                return default
            raise
        return re.search(r"^([A-Z]:\\.*)\s*$", res, flags=re.M).group(1)

    try:
        res = check_output_u8(["matlab", "-n"])
    except (CalledProcessError, FileNotFoundError):
        if default:
            return default
        raise
    return re.search(r"MATLAB\s+=\s+(\S+)\s*$", res, flags=re.M).group(1)


def _install_engine():
    src = path.join(matlabroot(), "extern", "engines", "python")
    with open(path.join(src, "setup.py")) as fd:
        # check version support
        supported = literal_eval(
            re.search(r"supported_version.*?=\s*(.*?)$", fd.read(), flags=re.M).group(1))
        if ".".join(map(str, sys.version_info[:2])) not in map(str, supported):
            raise VersionError(
                dedent("""\
                Python version is {info[0]}.{info[1]},
                but the installed MATLAB only supports Python versions: [{supported}]
                """.format(info=sys.version_info[:2], supported=", ".join(supported))))
    with tmpdir() as td:
        cmd = [sys.executable, "setup.py", "build", "--build-base", td, "install"]
        try:
            return check_output_u8(cmd + ["--prefix", sys.prefix], cwd=src)
        except CalledProcessError:
            log.warning("Normal install failed. Attempting `--user` install.")
            try:
                return check_output_u8(cmd + ["--user"], cwd=src)
            except CalledProcessError:
                ml_ver = src.split(path.sep)[-4].lstrip("R")
                if ml_ver < '2020b':
                    raise
                eng_ver = {
                    '2020b': '9.9', '2021a': '9.10', '2021b': '9.11', '2022a': '9.12',
                    '2022b': '9.13', '2023a': '9.14'}
                pin = f"=={eng_ver[ml_ver]}.*" if ml_ver in eng_ver else ""
                return check_output_u8([
                    sys.executable, "-m", "pip", "install", "matlabengine" + pin])


@lru_cache()
def get_runtime(cache="~/.mcr", version=99):
    cache = Path(cache).expanduser()
    mcr_root = cache
    i = mcr_root / f"v{version}"
    if i.is_dir():
        mcr_root = i
    else:
        from miutil.web import urlopen_cached

        log.info("Downloading to %s", cache)
        with tmpdir() as td:
            with urlopen_cached(MCR_URL[version], cache) as fd:
                if MCR_URL[version].endswith(".zip"):
                    extractall(fd, td)
            log.info("Installing ... (may take a few min)")
            if version == 99:
                check_output_u8([
                    fspath(Path(td) / ("setup" if system() == "Windows" else "install")), "-mode",
                    "silent", "-agreeToLicense", "yes", "-destinationFolder",
                    fspath(mcr_root)])
            elif version == 713:
                install = cache / MCR_URL[version].rsplit("/", 1)[-1]
                if system() == "Linux":
                    install.chmod(0o755)
                    check_output_u8([
                        fspath(install), "-P", f'bean421.installLocation="{fspath(cache)}"',
                        "-silent"])
                else:
                    raise NotImplementedError(
                        dedent("""\
                        Don't yet know how to handle
                        {0}
                        for {1!r}.
                        """).format(fspath(install), system()))
            else:
                raise IndexError(version)
            mcr_root /= f"v{version}"
            log.info("Installed")

    # bin
    if (mcr_root / "bin" / MCR_ARCH).is_dir():
        env_prefix("PATH", mcr_root / "bin" / MCR_ARCH)
    else:
        log.warning("Cannot find MCR bin")

    # libs
    env_var = {"Linux": "LD_LIBRARY_PATH", "Windows": "PATH",
               "Darwin": "DYLD_LIBRARY_PATH"}[system()]
    if (mcr_root / "runtime" / MCR_ARCH).is_dir():
        env_prefix(env_var, mcr_root / "runtime" / MCR_ARCH)
    else:
        log.warning("Cannot find MCR libs")

    # python module
    pydist = mcr_root / "extern" / "engines" / "python" / "dist"
    if pydist.is_dir():
        if fspath(pydist) not in sys.path:
            sys.path.insert(1, fspath(pydist))
    else:
        log.warning("Cannot find MCR Python dist")

    return mcr_root
