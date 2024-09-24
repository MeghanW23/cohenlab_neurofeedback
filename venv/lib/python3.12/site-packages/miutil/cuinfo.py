#!/usr/bin/env python3
"""CUDA helpers
Usage:
  cuinfo [options]

Options:
  -n, --num-devices   : print number of devices (ignores `-d`)
  -f, --nvcc-flags    : print out flags for use nvcc compilation
  -c, --compute       : print out compute capabilities (strip periods)
  -d ID, --dev-id ID  : select device ID [default: None:int] for all
"""
import pynvml
from argopt import argopt

__all__ = ["num_devices", "compute_capability", "memory", "name", "nvcc_flags"]


def nvmlDeviceGetCudaComputeCapability(handle):
    major = pynvml.c_int()
    minor = pynvml.c_int()
    try:      # pynvml>=11
        get_fn = pynvml.nvml._nvmlGetFunctionPointer
    except AttributeError:
        get_fn = pynvml.get_func_pointer
    fn = get_fn("nvmlDeviceGetCudaComputeCapability")
    ret = fn(handle, pynvml.byref(major), pynvml.byref(minor))
    try:      # pynvml>=11
        check_ret = pynvml.nvml._nvmlCheckReturn
    except AttributeError:
        check_ret = pynvml.check_return
    check_ret(ret)
    return [major.value, minor.value]


def num_devices():
    """returns total number of devices"""
    pynvml.nvmlInit()
    return pynvml.nvmlDeviceGetCount()


def get_handle(dev_id=-1):
    """allows negative indexing"""
    pynvml.nvmlInit()
    dev_id = num_devices() + dev_id if dev_id < 0 else dev_id
    try:
        return pynvml.nvmlDeviceGetHandleByIndex(dev_id)
    except pynvml.NVMLError:
        raise IndexError("invalid dev_id")


def compute_capability(dev_id=-1):
    """returns compute capability (major, minor)"""
    return tuple(nvmlDeviceGetCudaComputeCapability(get_handle(dev_id)))


def memory(dev_id=-1):
    """returns memory (total, free, used)"""
    mem = pynvml.nvmlDeviceGetMemoryInfo(get_handle(dev_id))
    return (mem.total, mem.free, mem.used)


def name(dev_id=-1):
    """returns device name"""
    res = pynvml.nvmlDeviceGetName(get_handle(dev_id))
    try:
        return res.decode("U8") # pynvml<11.5
    except AttributeError:
        return res


def nvcc_flags(dev_id=-1):
    return "-gencode=arch=compute_{0:d}{1:d},code=compute_{0:d}{1:d}".format(
        *compute_capability(dev_id))


def main(*args, **kwargs):
    args = argopt(__doc__).parse_args(*args, **kwargs)
    noargs = True
    devices = range(num_devices()) if args.dev_id is None else [args.dev_id]

    if args.num_devices:
        print(num_devices())
        noargs = False
    if args.nvcc_flags:
        print(" ".join(sorted(set(map(nvcc_flags, devices)))[::-1]))
        noargs = False
    if args.compute:
        print(" ".join(sorted({"%d%d" % compute_capability(i) for i in devices})[::-1]))
        noargs = False
    if noargs:
        for dev_id in devices:
            print("Device {:2d}:{}:compute capability:{:d}.{:d}".format( # NOQA: P101
                dev_id, name(dev_id), *compute_capability(dev_id)))


if __name__ == "__main__": # pragma: no cover
    main()
