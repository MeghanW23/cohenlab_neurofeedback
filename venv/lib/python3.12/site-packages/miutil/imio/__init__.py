import re

from ..fdio import fspath

RE_NII_GZ = re.compile(r"^(.+)(\.nii(?:\.gz)?)$", flags=re.I)
RE_NPYZ = re.compile(r"^(.+)(\.np[yz])$", flags=re.I)


def imread(fname, *args, **kwargs):
    """Read any supported filename"""
    if RE_NII_GZ.search(fspath(fname)):
        from .nii import getnii

        return getnii(fname, *args, **kwargs)
    elif RE_NPYZ.search(fspath(fname)):
        import numpy as np

        res = np.load(fname, *args, **kwargs)
        if hasattr(res, "keys") and len(res.keys()) == 1:
            res = res[list(res.keys())[0]]
        return res
    raise ValueError("Unknown image type: " + fname)
