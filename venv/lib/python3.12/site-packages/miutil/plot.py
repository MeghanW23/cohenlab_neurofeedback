from os import path
from textwrap import dedent

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from .imio import imread

show = plt.show    # convenience: for use after `imscroll`


def apply_cmap(**kwargs):
    """Apply different cmaps to inputs an average the results.

    Args:
      **kwargs: map named cmap to ndarray

    >>> vol1 = np.random.random((10, 10, 10))
    >>> vol2 = np.random.random((10, 10, 10))
    >>> res = apply_cmap(magma=vol1, bone=vol2)
    >>> assert res.shape == (10, 10, 10, 4)  # RGBA
    >>> imscroll(res[None])  # (1, 10, 10, 10, 4) for (N, Z, Y, X, RGBA)
    """
    res = None
    for v in kwargs.values():
        if res is None:
            res = np.zeros(v.shape + (4,), dtype=np.float32)
        else:
            assert v.shape == res.shape[:-1], "all inputs must have same shape"
    for k, v in kwargs.items():
        cmap = getattr(cm, k)
        res += cmap(v)
    res /= len(kwargs)
    return res


class imscroll:
    """
    Slice through volumes by scrolling.
    Hold SHIFT to scroll faster.
    CTRL+click to select points to plot profiles between.
    """

    _instances = []
    _SUPPORTED_KEYS = ['control', 'shift']

    def __init__(self, vol, view='t', fig=None, titles=None, order=0, sharexy=None, show=False,
                 **kwargs):
        """
        Scroll through 2D slices of 3D volume(s) using the mouse.
        Args:
            vol (str or numpy.ndarray or list or dict): path to file or
                a (list/dict of) array(s).
            view (str): z, t, transverse/y, c, coronal/x, s, sagittal.
            fig (matplotlib.pyplot.Figure): will be created if unspecified.
            titles (list): list of strings (overrides `vol.keys()`).
            order (int): spline interpolation order for line profiles.
                0: nearest, 1: bilinear, >2: probably avoid.
            sharexy (bool): whether to link zoom across all axes.
            show (bool): whether to run `matplotlib.pyplot.show()`.
            **kwargs: passed to `matplotlib.pyplot.imshow()`.
        """
        if isinstance(vol, str) and path.exists(vol):
            vol = imread(vol)
        if hasattr(vol, "keys"):
            keys = list(vol.keys())
            vol = [vol[i] for i in keys]
            if titles is None:
                titles = keys
        ndim = vol[0].ndim + 1
        if ndim == 3:
            vol = [vol]
        elif ndim not in [4, 5]:
            raise IndexError(
                dedent("""\
                Expected vol.ndim in
                    3: single volume
                    4: multiple volumes
                    5: multiple RGB volumes
                but got {0}
                """.format(ndim)))

        view = view.lower()
        if view in ['c', 'coronal', 'y']:
            vol = [i.transpose(1, 0, 2) for i in vol]
        elif view in ['s', 'saggital', 'x']:
            vol = [i.transpose(2, 0, 1) for i in vol]

        # volumes
        self.titles = titles or [None] * len(vol)
        self.index_max = min(map(len, vol))
        self.index = self.index_max // 2
        if sharexy is None:
            sharexy = len({i.shape for i in vol}) == 1
        if fig is not None:
            self.fig, axs = fig, fig.subplots(1, len(vol), sharex=sharexy, sharey=sharexy)
        else:
            self.fig, axs = plt.subplots(1, len(vol), sharex=sharexy, sharey=sharexy)
        self.axs = [axs] if len(vol) == 1 else list(axs.flat)
        for ax, i, t in zip(self.axs, vol, self.titles):
            ax.imshow(i[self.index], **kwargs)
            ax.set_title(t or f"slice #{self.index}")
        self.vols = vol
        # line profiles
        self.order = order
        self.picked = []
        self._annotes = []
        # event callbacks
        self.key = {i: False for i in self._SUPPORTED_KEYS}
        self.fig.canvas.mpl_connect('scroll_event', self._scroll)
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)
        self.fig.canvas.mpl_connect('key_release_event', self._off_key)
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        imscroll._instances.append(self) # prevents gc
        if show:
            plt.show()

    @classmethod
    def clear(cls, self):
        cls._instances.clear()

    def _on_key(self, event):
        key = {'ctrl': 'control'}.get(event.key, event.key)
        if key in self._SUPPORTED_KEYS:
            self.key[key] = True

    def _off_key(self, event):
        key = {'ctrl': 'control'}.get(event.key, event.key)
        if key in self._SUPPORTED_KEYS:
            self.key[key] = False

    def _scroll(self, event):
        self.set_index(self.index + event.step * (10 if self.key['shift'] else 1))

    def set_index(self, index):
        self.index = int(index) % self.index_max
        for ax, vol, t in zip(self.axs, self.vols, self.titles):
            ax.images[0].set_array(vol[self.index])
            ax.set_title(t or f"slice #{self.index}")
        for ann in self._annotes:
            ann.remove()
        self._annotes = []
        self.fig.canvas.draw()

    def _on_click(self, event):
        if not self.key['control'] or None in (event.xdata, event.ydata):
            return
        self.picked.append((event.xdata, event.ydata))
        if len(self.picked) < 2:
            return

        import numpy as np
        import scipy.ndimage as ndi

        (x0, y0), (x1, y1) = self.picked[:2]
        num = int(np.round(np.hypot(y1 - y0, x1 - x0) * 4)) + 1
        x, y = np.linspace(x0, x1, num), np.linspace(y0, y1, num)
        arr = event.inaxes.images[0].get_array()
        if arr.ndim == 3:
            z = [
                ndi.map_coordinates(
                    arr,
                    np.vstack((x, y, np.ones_like(x) * i)),
                    order=self.order,
                    mode='nearest',
                ) for i in range(event.inaxes.images[0].get_array().shape[-1])]
        else:
            z = ndi.map_coordinates(arr, np.vstack((x, y)), order=self.order, mode='nearest')
        self.picked = []
        self.key['control'] = False

        self._annotes.append(event.inaxes.plot([x0, x1], [y0, y1], 'r-')[0])
        plt.figure()
        if arr.ndim == 3:
            for channel, colour in zip(z, 'rgbcmyk'):
                plt.plot(x, channel, colour + '-')
        else:
            plt.plot(x, z, 'r-')
        plt.xlabel("x")
        plt.ylabel("Intensity")
        plt.show()
