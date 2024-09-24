"""NIfTI I/O"""
import gzip
import logging
import numbers
import os.path
import re
import sys

import nibabel as nib
import numpy as np

from ..fdio import create_dir, fspath, hasext
from . import RE_NII_GZ

RE_GZ = re.compile(r"^(.+)(\.gz)$", flags=re.I)
log = logging.getLogger(__name__)
if sys.version_info[0] < 3:
    string_types = basestring, # NOQA: F821
else:
    string_types = str,


def file_parts(fname, regex=RE_NII_GZ):
    """/path/file.nii.gz -> /path, file, .nii.gz"""
    fname = fspath(fname)
    base = os.path.basename(fname)
    root, ext = regex.search(base).groups()
    return os.path.dirname(fname), root, ext


def nii_ugzip(imfile, outpath=""):
    """Uncompress *.gz file"""
    assert hasext(imfile, "gz")
    dout, fout, ext = file_parts(imfile, RE_GZ)
    with gzip.open(fspath(imfile), "rb") as f:
        s = f.read()
    # write the uncompressed data
    fout = os.path.join(fspath(outpath) or dout, fout)
    with open(fout, "wb") as f:
        f.write(s)
    return fout


def nii_gzip(imfile, outpath=""):
    """Compress *.gz file"""
    imfile = fspath(imfile)
    with open(imfile, "rb") as f:
        d = f.read()
    # write the compressed data
    fout = imfile + ".gz"
    if outpath:
        fout = os.path.join(fspath(outpath), os.path.basename(fout))
    with gzip.open(fout, "wb") as f:
        f.write(d)
    return fout


def getnii(fim, nan_replace=None, output='image'):
    """
    Get image from NIfTI file.
    Arguments:
        fim: input file name for the NIfTI image
        nan_replace: the value to be used for replacing the NaNs in the image.
                     by default no change (None).
        output: option for choosing output: image, affine matrix or
                a dictionary with all info.
    Return:
        'image': outputs just an image (4D or 3D)
        'affine': outputs just the affine matrix
        'all': outputs all as a dictionary
    """
    nim = nib.load(fspath(fim))

    dim = nim.header.get('dim')
    dimno = dim[0]

    if output == 'image' or output == 'all':
        imr = np.asanyarray(nim.dataobj)
        # replace NaNs if requested
        if isinstance(nan_replace, numbers.Number):
            imr[np.isnan(imr)] = nan_replace

        imr = np.squeeze(imr)
        if dimno != imr.ndim and dimno == 4:
            dimno = imr.ndim

        # > get orientations from the affine
        ornt = nib.io_orientation(nim.affine)
        trnsp = tuple(np.flip(np.argsort(ornt[:, 0])))
        flip = tuple(np.int8(ornt[:, 1]))

        # > voxel size
        voxsize = nim.header.get('pixdim')[1:nim.header.get('dim')[0] + 1]
        # > rearrange voxel size according to the orientation
        voxsize = voxsize[np.array(trnsp)]

        # > dimensions
        dims = dim[1:nim.header.get('dim')[0] + 1]
        dims = dims[np.array(trnsp)]

        # > flip y-axis and z-axis and then transpose
        if dimno == 4:   # dynamic
            imr = np.transpose(imr[::-flip[0], ::-flip[1], ::-flip[2], :], (3,) + trnsp)
        elif dimno == 3: # static
            imr = np.transpose(imr[::-flip[0], ::-flip[1], ::-flip[2]], trnsp)

    if output == 'affine' or output == 'all':
        # A = nim.get_sform()
        # if not A[:3,:3].any():
        #     A = nim.get_qform()
        A = nim.affine

    if output == 'all':
        out = {
            'im': imr, 'affine': A, 'fim': fim, 'dtype': nim.get_data_dtype(), 'shape': imr.shape,
            'hdr': nim.header, 'voxsize': voxsize, 'dims': dims, 'transpose': trnsp, 'flip': flip}
    elif output == 'image':
        out = imr
    elif output == 'affine':
        out = A
    else:
        raise NameError("Unrecognised output request!")

    return out


def array2nii(im, A, fnii, descrip="", trnsp=None, flip=None, storage_as=None):
    """
    Store the numpy array 'im' to a NIfTI file 'fnii'.
    Arguments:
        'im':       image to be stored in NIfTI
        'A':        affine transformation
        'fnii':     output NIfTI file name.
        'descrip':  the description given to the file
        'trsnp':    transpose/permute the dimensions.
                    In NIfTI it has to be in this order: [x,y,z,t,...])
        'flip':     flip tuple for flipping the direction of x,y,z axes.
                    (1: no flip, -1: flip)
        'storage_as': uses the flip and displacement as given by the following
                    NifTI dictionary, obtained using
                    `getnii(filepath, output='all')`.
    """
    trnsp = trnsp or ()
    flip = flip or ()
    storage_as = storage_as or []

    if len(trnsp) not in [0, 3, 4] and len(flip) not in [0, 3]:
        raise ValueError("number of flip and/or transpose elements is incorrect.")

    # ---------------------------------------------------------------------------
    # > TRANSLATIONS and FLIPS
    # > get the same geometry as the input NIfTI file in the form of dictionary,
    # >>as obtained from getnii(..., output='all')

    # > permute the axis order in the image array
    if (isinstance(storage_as, dict) and 'transpose' in storage_as and 'flip' in storage_as):

        trnsp = (storage_as['transpose'].index(0), storage_as['transpose'].index(1),
                 storage_as['transpose'].index(2))

        flip = storage_as['flip']

    if not trnsp:
        im = im.transpose()
    # > check if the image is 4D (dynamic) and modify as needed
    elif len(trnsp) == 3 and im.ndim == 4:
        trnsp = tuple([t + 1 for t in trnsp] + [0])
        im = im.transpose(trnsp)
    else:
        im = im.transpose(trnsp)

    # > perform flip of x,y,z axes after transposition into proper NIfTI order
    if len(flip) == 3:
        im = im[::-flip[0], ::-flip[1], ::-flip[2], ...]

    res = nib.Nifti1Image(im, A, dtype=im.dtype)
    hdr = res.header
    hdr.set_sform(None, code='scanner')
    hdr['cal_max'] = np.max(im) # np.percentile(im, 90) #
    hdr['cal_min'] = np.min(im)
    hdr['descrip'] = descrip
    nib.save(res, fspath(fnii))


def niisort(fims, memlim=True):
    """
    Sort all input NIfTI images and check their shape.
    Output dictionary of image files and their properties.
    Options:
        memlim -- when processing large numbers of frames the memory may
        not be large enough.  memlim causes that the output does not contain
        all the arrays corresponding to the images.
    """
    # number of NIfTI images in folder
    Nim = 0
    # sorting list (if frame number is present in the form '_frm%d')
    sortlist = []

    for f in fims:
        if RE_NII_GZ.search(f):
            Nim += 1
            frm = re.search(r"(?<=_frm)\d*", f)
            if frm:
                frm = int(frm.group(0))
                freelists = [frm not in li for li in sortlist]
                listidx = [i for i, f in enumerate(freelists) if f]
                if listidx:
                    sortlist[listidx[0]].append(frm)
                else:
                    sortlist.append([frm])
            else:
                sortlist.append([None])

    if len(sortlist) > 1:
        # if more than one dynamic set is given, the dynamic mode is cancelled.
        dyn_flg = False
        sortlist = list(range(Nim))
    elif len(sortlist) == 1:
        dyn_flg = True
        sortlist = sortlist[0]
    else:
        raise ValueError("empty sortlist")

    # number of frames (can be larger than the # images)
    Nfrm = max(sortlist) + 1
    # sort the list according to the frame numbers
    _fims = ["Blank"] * Nfrm
    # list of NIfTI image shapes and data types used
    shape = []
    datype = []
    _nii = []
    for i in range(Nim):
        if dyn_flg:
            _fims[sortlist[i]] = fims[i]
            _nii = nib.load(fims[i])
            datype.append(_nii.get_data_dtype())
            shape.append(_nii.shape)
        else:
            _fims[i] = fims[i]
            _nii = nib.load(fims[i])
            datype.append(_nii.get_data_dtype())
            shape.append(_nii.shape)

    # check if all images are of the same shape and data type
    if _nii and shape.count(_nii.shape) != len(shape):
        raise ValueError("Input images are of different shapes.")
    if _nii and datype.count(_nii.get_data_dtype()) != len(datype):
        raise TypeError("Input images are of different data types.")
    # image shape must be 3D
    if _nii and len(_nii.shape) != 3:
        raise ValueError("Input image(s) must be 3D.")

    out = {
        'shape': _nii.shape[::-1], 'files': _fims, 'sortlist': sortlist,
        'dtype': _nii.get_data_dtype(), 'N': Nim}

    if memlim and Nfrm > 50:
        imdic = getnii(_fims[0], output='all')
        affine = imdic['affine']
    else:
        # get the images into an array
        _imin = np.zeros((Nfrm,) + _nii.shape[::-1], dtype=_nii.get_data_dtype())
        for i in range(Nfrm):
            if i in sortlist:
                imdic = getnii(_fims[i], output='all')
                _imin[i, :, :, :] = imdic['im']
                affine = imdic['affine']
        out['im'] = _imin[:Nfrm, :, :, :]

    out['affine'] = affine

    return out


def nii_modify(nii_fd, fimout="", outpath="", fcomment="", voxel_range=None):
    """
    Modify the NIfTI image given either as a file path or a dictionary,
    obtained by `getnii(file_path)`.

    @param nii_fd  : file or dict
    """
    voxel_range = voxel_range or []
    if isinstance(nii_fd, string_types) and os.path.isfile(nii_fd):
        dctnii = getnii(nii_fd, output="all")
        fnii = nii_fd
    if isinstance(nii_fd, dict) and "im" in nii_fd:
        dctnii = nii_fd
        if "fim" in dctnii:
            fnii = dctnii["fim"]

    if not outpath and fimout and "/" in fimout:
        opth = os.path.dirname(fimout)
        if not opth and isinstance(fnii, string_types) and os.path.isfile(fnii):
            opth = os.path.dirname(nii_fd)
        fimout = os.path.basename(fimout)
    elif not outpath and isinstance(fnii, string_types) and os.path.isfile(fnii):
        opth = os.path.dirname(fnii)
    else:
        opth = outpath
    log.debug("output path:%s", opth)
    create_dir(opth)

    if not fimout:
        if not fcomment:
            fcomment = "_nimpa-modified"
        fout = file_parts(fnii)[1] + fcomment + ".nii.gz"
    else:
        fout = os.path.splitext(fimout)[0] + ".nii.gz"
    log.debug("output floating and affine file names:%s", fout)
    fout = os.path.join(opth, fout)

    if len(voxel_range) == 1:                                               # set max value
        im = voxel_range[0] * dctnii["im"] / np.max(dctnii["im"])
    elif len(voxel_range) == 2:                                             # set range
        im = (dctnii["im"] - np.min(dctnii["im"])) * (np.ptp(voxel_range) /
                                                      np.ptp(dctnii["im"])) + voxel_range[0]
    else:
        return None

    # > output file name for the extra reference image
    array2nii(
        im,
        dctnii["affine"],
        fout,
        trnsp=(
            dctnii["transpose"].index(0),
            dctnii["transpose"].index(1),
            dctnii["transpose"].index(2),
        ),
        flip=dctnii["flip"],
    )

    return {"fim": fout, "im": im, "affine": dctnii["affine"]}
