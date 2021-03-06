# -*- coding: utf-8 -*-
"""
Utilities for generating static image and line plots of near-publishable quality

Created on Thu May 05 13:29:12 2020

@author: Gerd Duscher
"""

from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches
# import matplotlib.animation as animation

from ..hdf.dtype_utils import is_complex_dtype
if sys.version_info.major == 3:
    unicode = str

default_cmap = plt.cm.viridis


class CurveVisualizer(object):
    def __init__(self, dset, spectrum_number=None, figure=None, **kwargs):
        from ..sid.dataset import Dataset
        from ..sid.dimension import DimensionType

        if not isinstance(dset, Dataset):
            raise TypeError('dset should be a sidpy.Dataset object')

        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        if figure is None:
            self.fig = plt.figure(**fig_args)
        else:
            self.fig = figure

        self.dset = dset
        self.selection = []
        self.spectral_dims = []

        for dim, axis in dset._axes.items():
            if axis.dimension_type == DimensionType.SPECTRAL:
                self.selection.append(slice(None))
                self.spectral_dims.append(dim)
            else:
                if spectrum_number <= dset.shape[dim]:
                    self.selection.append(slice(spectrum_number, spectrum_number + 1))
                else:
                    self.spectrum_number = 0
                    self.selection.append(slice(0, 1))

        # Handle the simple cases first:
        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        self.dim = self.dset._axes[self.spectral_dims[0]]

        if is_complex_dtype(dset.dtype):
            # Plot real and image
            fig, axes = plt.subplots(nrows=2, **fig_args)

            axes[0].plot(self.dim.values, self.dset.squeeze().abs(), **kwargs)

            axes[0].set_title(self.dset.title + '\n(Magnitude)', pad=15)
            axes[0].set_xlabel(self.dset.labels[self.dim])
            axes[0].set_ylabel(self.dset.data_descriptor)
            axes[0].ticklabel_format(style='sci', scilimits=(-2, 3))

            axes[1].set_title(self.dset.title + '\n(Phase)', pad=15)
            axes[1].set_ylabel('Phase (rad)')
            axes[1].set_xlabel(self.dset.labels[self.spectral_dims[0]])  # + x_suffix)
            axes[1].ticklabel_format(style='sci', scilimits=(-2, 3))

            fig.tight_layout()

        else:
            self.axis = self.fig.add_subplot(1, 1, 1, **fig_args)
            self.axis.plot(self.dim.values, self.dset, **kwargs)
            self.axis.set_title(self.dset.title, pad=15)
            self.axis.set_xlabel(self.dset.labels[self.spectral_dims[0]])
            self.axis.set_ylabel(self.dset.data_descriptor)
            self.axis.ticklabel_format(style='sci', scilimits=(-2, 3))
            self.fig.canvas.draw_idle()


class ImageVisualizer(object):
    """
    Interactive display of image plot

    The stack can be scrolled through with a mouse wheel or the slider
    The usual zoom effects of matplotlib apply.
    Works on every backend because it only depends on matplotlib.

    Important: keep a reference to this class to maintain interactive properties so usage is:

    >>view = plot_stack(dataset, {'spatial':[0,1], 'stack':[2]})

    Input:
    ------
    - dset: NSIDask _dataset
    - figure: optional
            matplotlib figure
    - image_number optional
            if this is a stack of images we can choose which one we want.
    kwargs optional
            additional arguments for matplotlib and a boolean value with keyword 'scale_bar'

    """

    def __init__(self, dset, figure=None, image_number=0, **kwargs):
        from ..sid.dataset import Dataset
        from ..sid.dimension import DimensionType

        """
        plotting of data according to two axis marked as SPATIAL in the dimensions
        """
        if not isinstance(dset, Dataset):
            raise TypeError('dset should be a sidpy.Dataset object')
        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        if figure is None:
            self.fig = plt.figure(**fig_args)
        else:
            self.fig = figure

        self.dset = dset
        self.image_number = image_number

        self.selection = []
        self.image_dims = []

        for dim, axis in dset._axes.items():
            if axis.dimension_type in [DimensionType.SPATIAL, DimensionType.RECIPROCAL]:
                self.selection.append(slice(None))
                self.image_dims.append(dim)
            else:
                if image_number <= dset.shape[dim]:
                    self.selection.append(slice(image_number, image_number + 1))
                else:
                    self.image_number = 0
                    self.selection.append(slice(0, 1))
        if len(self.image_dims) != 2:
            raise ValueError('We need two dimensions with dimension_type SPATIAL or RECIPROCAL to plot an image')

        if is_complex_dtype(dset.dtype):
            # Plot complex image
            self.axes = []
            self.axes.append(self.fig.add_subplot(121))
            self.img = self.axes[0].imshow(self.dset[tuple(self.selection)].abs().squeeze().T,
                                           extent=self.dset.get_extent(self.image_dims), **kwargs)
            self.axes[0].set_xlabel(self.dset.labels[self.image_dims[0]])
            self.axes[0].set_ylabel(self.dset.labels[self.image_dims[1]])
            self.axes[0].set_title(dset.title + '\n(Magnitude)', pad=15)
            cbar = self.fig.colorbar(self.img)
            cbar.set_label("{} [{}]".format(self.dset.quantity, self.dset.units))
            self.axes[0].ticklabel_format(style='sci', scilimits=(-2, 3))

            self.axes.append(self.fig.add_subplot(122, sharex=self.axes[0], sharey=self.axes[0]))
            self.img_c = self.axes[1].imshow(self.dset[tuple(self.selection)].squeeze().angle().T,
                                             extent=self.dset.get_extent(self.image_dims), **kwargs)
            self.axes[1].set_xlabel(self.dset.labels[self.image_dims[0]])
            self.axes[1].set_ylabel(self.dset.labels[self.image_dims[1]])
            self.axes[1].set_title(dset.title + '\n(Phase)', pad=15)
            cbar_c = self.fig.colorbar(self.img_c)
            cbar_c.set_label(self.dset.data_descriptor)
            self.axes[1].ticklabel_format(style='sci', scilimits=(-2, 3))

            self.fig.tight_layout()

        else:
            self.axis = self.fig.add_subplot(1, 1, 1)
            self.plot_image(**kwargs)

    def plot_image(self, **kwargs):
        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
        scale_bar = kwargs.pop('scale_bar', False)

        if len(self.dset.shape) > 2:
            self.axis.set_title(self.dset.title + '_image {}'.format(self.image_number))
        else:
            self.axis.set_title(self.dset.title)

        self.img = self.axis.imshow(self.dset[tuple(self.selection)].squeeze().T,
                                    extent=self.dset.get_extent(self.image_dims), **kwargs)
        self.axis.set_xlabel(self.dset.labels[self.image_dims[0]])
        self.axis.set_ylabel(self.dset.labels[self.image_dims[1]])
        if scale_bar:

            plt.axis('off')
            extent = self.dset.get_extent(self.image_dims)
            size_of_bar = int((extent[1] - extent[0]) / 10 + .5)
            if size_of_bar < 1:
                size_of_bar = 1
            scalebar = AnchoredSizeBar(plt.gca().transData,
                                       size_of_bar, '{} {}'.format(size_of_bar,
                                                                   self.dset._axes[self.image_dims[0]].units),
                                       'lower left',
                                       pad=1,
                                       color='white',
                                       frameon=False,
                                       size_vertical=.2)

            plt.gca().add_artist(scalebar)

        else:
            cbar = self.fig.colorbar(self.img)
            cbar.set_label(self.dset.data_descriptor)

            self.axis.ticklabel_format(style='sci', scilimits=(-2, 3))
            self.fig.tight_layout()
        self.img.axes.figure.canvas.draw_idle()


class ImageStackVisualizer(object):
    """
    Interactive display of image stack plot

    The stack can be scrolled through with a mouse wheel or the slider
    The usual zoom effects of matplotlib apply.
    Works on every backend because it only depends on matplotlib.

    Important: keep a reference to this class to maintain interactive properties so usage is:

    >>kwargs = {'scale_bar': True, 'cmap': 'hot'}

    >>view = ImageStackVisualizer(dataset, **kwargs )

    Input:
    ------
    - dset: sidpy Dataset
    - figure: optional
            matplotlib figure
    - kwargs: optional
            matplotlib additional arguments like {cmap: 'hot'}
    """

    def __init__(self, dset, figure=None, **kwargs):
        from ..sid.dataset import Dataset
        from ..sid.dimension import DimensionType

        from IPython.display import display

        if not isinstance(dset, Dataset):
            raise TypeError('dset should be a sidpy.Dataset object')
        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        if figure is None:
            self.fig = plt.figure(**fig_args)
        else:
            self.fig = figure

        if dset.ndim < 3:
            raise KeyError('dataset must have at least three dimensions')

        self.stack_dim = -1
        self.image_dims = []
        self.selection = []
        for dim, axis in dset._axes.items():
            if axis.dimension_type in [DimensionType.SPATIAL, DimensionType.RECIPROCAL]:
                self.selection.append(slice(None))
                self.image_dims.append(dim)
            elif axis.dimension_type == DimensionType.TEMPORAL or len(dset) == 3:
                self.selection.append(slice(0, 1))
                self.stack_dim = dim
            else:
                self.selection.append(slice(0, 1))

        if len(self.image_dims) != 2:
            raise ValueError('We need two dimensions with dimension_type spatial to plot an image')

        if self.stack_dim < 0:
            raise KeyError('We need one dimensions with dimension_type stack, time or frame')

        if len(self.image_dims) < 2:
            raise KeyError('Two SPATIAL dimension are necessary for this plot')

        self.dset = dset

        # self.axis = self.fig.add_axes([0.0, 0.2, .9, .7])
        self.ind = 0

        self.number_of_slices = self.dset.shape[self.stack_dim]
        self.axis = None
        self.plot_image(**kwargs)
        self.axis = plt.gca()
        self.axis.set_title('image stack: ' + dset.title + '\n use scroll wheel to navigate images')
        self.img.axes.figure.canvas.mpl_connect('scroll_event', self._onscroll)

        import ipywidgets as iwgt
        self.play = iwgt.Play(
            value=0,
            min=0,
            max=self.number_of_slices,
            step=1,
            interval=500,
            description="Press play",
            disabled=False
        )
        self.slider = iwgt.IntSlider(
            value=0,
            min=0,
            max=self.number_of_slices,
            continuous_update=False,
            description="Frame:")
        # set the slider function
        iwgt.interactive(self._update, frame=self.slider)
        # link slider and play function
        iwgt.jslink((self.play, 'value'), (self.slider, 'value'))

        # We add a button to average the images
        button = iwgt.widgets.ToggleButton(
            value=False,
            description='Average',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Average Images of Stack')

        button.observe(self._average_slices, 'value')

        # set play and slider widgets next to each other
        widg = iwgt.HBox([self.play, self.slider, button])
        display(widg)

        # self.anim = animation.FuncAnimation(self.fig, self._updatefig, interval=200, blit=False, repeat=True)
        self._update()

    def plot_image(self, **kwargs):

        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

        scale_bar = kwargs.pop('scale_bar', False)
        self.axis = plt.gca()
        self.axis.set_title(self.dset.title)

        self.img = self.axis.imshow(self.dset[tuple(self.selection)].squeeze().T,
                                    extent=self.dset.get_extent(self.image_dims), **kwargs)
        self.axis.set_xlabel(self.dset.labels[self.image_dims[0]])
        self.axis.set_ylabel(self.dset.labels[self.image_dims[1]])

        if scale_bar:

            plt.axis('off')
            extent = self.dset.get_extent(self.image_dims)
            size_of_bar = int((extent[1] - extent[0]) / 10 + .5)
            if size_of_bar < 1:
                size_of_bar = 1
            scalebar = AnchoredSizeBar(plt.gca().transData,
                                       size_of_bar, '{} {}'.format(size_of_bar,
                                                                   self.dset._axes[self.image_dims[0]].units),
                                       'lower left',
                                       pad=1,
                                       color='white',
                                       frameon=False,
                                       size_vertical=.2)

            plt.gca().add_artist(scalebar)

        else:
            cbar = self.fig.colorbar(self.img)
            cbar.set_label(self.dset.data_descriptor)

            self.axis.ticklabel_format(style='sci', scilimits=(-2, 3))
            self.fig.tight_layout()

        self.img.axes.figure.canvas.draw_idle()

    def _average_slices(self, event):
        if event.new:
            if len(self.dset.shape) == 3:
                image_stack = self.dset
            else:
                stack_selection = self.selection.copy()
                stack_selection[self.stack_dim] = slice(None)
                image_stack = self.dset[stack_selection].squeeze()

            self.img.set_data(image_stack.mean(axis=self.stack_dim).T)
            self.fig.canvas.draw_idle()
        elif event.old:
            self.ind = self.ind % self.number_of_slices
            self._update(self.ind)

    def _onscroll(self, event):
        if event.button == 'up':
            self.slider.value = (self.slider.value + 1) % self.number_of_slices
        else:
            self.slider.value = (self.slider.value - 1) % self.number_of_slices
        self.ind = int(self.slider.value)

    def _update(self, frame=0):
        self.ind = frame
        self.selection[self.stack_dim] = slice(frame, frame + 1)
        self.img.set_data((self.dset[tuple(self.selection)].squeeze()).T)
        self.img.axes.figure.canvas.draw_idle()


class SpectralImageVisualizer(object):
    """
    ### Interactive spectrum imaging plot

    """

    def __init__(self, dset, figure=None, horizontal=True, **kwargs):
        from ..sid.dataset import Dataset
        from ..sid.dimension import DimensionType

        if not isinstance(dset, Dataset):
            raise TypeError('dset should be a sidpy.Dataset object')

        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        if figure is None:
            self.fig = plt.figure(**fig_args)
        else:
            self.fig = figure

        if len(dset.shape) < 3:
            raise KeyError('dataset must have at least three dimensions')

        # We need one stack dim and two image dimes as lists in dictionary

        selection = []
        image_dims = []
        spectral_dims = []
        for dim, axis in dset._axes.items():
            if axis.dimension_type in [DimensionType.SPATIAL, DimensionType.RECIPROCAL]:
                selection.append(slice(None))
                image_dims.append(dim)
            elif axis.dimension_type == DimensionType.SPECTRAL:
                selection.append(slice(0, 1))
                spectral_dims.append(dim)
            else:
                selection.append(slice(0, 1))
        if len(image_dims) != 2:
            raise ValueError('We need two dimensions with dimension_type SPATIA: to plot an image')

        if len(spectral_dims) != 1:
            raise KeyError('We need one dimension with dimension_type SPECTRAL for a spectral image plot')

        self.horizontal = horizontal
        self.x = 0
        self.y = 0
        self.bin_x = 1
        self.bin_y = 1

        size_x = dset.shape[image_dims[0]]
        size_y = dset.shape[image_dims[1]]

        self.dset = dset
        self.energy_scale = dset._axes[spectral_dims[0]].values

        self.extent = [0, size_x, size_y, 0]
        self.rectangle = [0, size_x, 0, size_y]
        self.scaleX = 1.0
        self.scaleY = 1.0
        self.analysis = []
        self.plot_legend = False

        self.image_dims = image_dims
        self.spec_dim = spectral_dims[0]

        if horizontal:
            self.axes = self.fig.subplots(ncols=2)
        else:
            self.axes = self.fig.subplots(nrows=2, **fig_args)

        self.fig.canvas.manager.set_window_title(self.dset.title)
        self.image = dset.mean(axis=spectral_dims[0])
        if 1 in self.dset.shape:
            self.image = dset.squeeze()
            #self.extent[2]=self.image.shape[1]
            #self.bin_y=self.image.shape[1]
            self.axes[0].set_aspect('auto')
        else:
            self.axes[0].set_aspect('equal')


        self.axes[0].imshow(self.image.T, extent=self.extent, **kwargs)
        if horizontal:
            self.axes[0].set_xlabel('{} [pixels]'.format(self.dset._axes[image_dims[0]].quantity))
        else:
            self.axes[0].set_ylabel('{} [pixels]'.format(self.dset._axes[image_dims[1]].quantity))

        if 1 in self.dset.shape:
            self.axes[0].set_aspect('auto')
            self.axes[0].get_yaxis().set_visible(False)
        else:
            self.axes[0].set_aspect('equal')


        # self.rect = patches.Rectangle((0,0),1,1,linewidth=1,edgecolor='r',facecolor='red', alpha = 0.2)
        self.rect = patches.Rectangle((0, 0), self.bin_x, self.bin_y, linewidth=1, edgecolor='r',
                                      facecolor='red', alpha=0.2)

        self.axes[0].add_patch(self.rect)
        self.intensity_scale = 1.
        self.spectrum = self.get_spectrum()

        self.axes[1].plot(self.energy_scale, self.spectrum)
        self.axes[1].set_title('spectrum {}, {}'.format(self.x, self.y))
        self.xlabel = self.dset.labels[self.spec_dim]
        self.ylabel = self.dset.data_descriptor
        self.axes[1].set_xlabel(self.dset.labels[self.spec_dim])  # + x_suffix)
        self.axes[1].set_ylabel(self.dset.data_descriptor)
        self.axes[1].ticklabel_format(style='sci', scilimits=(-2, 3))
        self.fig.tight_layout()
        self.cid = self.axes[1].figure.canvas.mpl_connect('button_press_event', self._onclick)

        self.fig.canvas.draw_idle()

    def set_bin(self, bin_xy):

        old_bin_x = self.bin_x
        old_bin_y = self.bin_y
        if isinstance(bin_xy, list):

            self.bin_x = int(bin_xy[0])
            self.bin_y = int(bin_xy[1])

        else:
            self.bin_x = int(bin_xy)
            self.bin_y = int(bin_xy)

        if self.bin_x > self.dset.shape[self.image_dims[0]]:
            self.bin_x = self.dset.shape[self.image_dims[0]]
        if self.bin_y > self.dset.shape[self.image_dims[1]]:
            self.bin_y = self.dset.shape[self.image_dims[1]]

        self.rect.set_width(self.rect.get_width() * self.bin_x / old_bin_x)
        self.rect.set_height((self.rect.get_height() * self.bin_y / old_bin_y))
        if self.x + self.bin_x > self.dset.shape[self.image_dims[0]]:
            self.x = self.dset.shape[0] - self.bin_x
        if self.y + self.bin_y > self.dset.shape[self.image_dims[1]]:
            self.y = self.dset.shape[1] - self.bin_y

        self.rect.set_xy([self.x * self.rect.get_width() / self.bin_x + self.rectangle[0],
                          self.y * self.rect.get_height() / self.bin_y + self.rectangle[2]])
        self._update()

    def get_spectrum(self):
        from ..sid.dimension import DimensionType

        if self.x > self.dset.shape[self.image_dims[0]] - self.bin_x:
            self.x = self.dset.shape[self.image_dims[0]] - self.bin_x
        if self.y > self.dset.shape[self.image_dims[1]] - self.bin_y:
            self.y = self.dset.shape[self.image_dims[1]] - self.bin_y
        selection = []

        for dim, axis in self.dset._axes.items():
            # print(dim, axis.dimension_type)
            if axis.dimension_type == DimensionType.SPATIAL:
                if dim == self.image_dims[0]:
                    selection.append(slice(self.x, self.x + self.bin_x))
                else:
                    selection.append(slice(self.y, self.y + self.bin_y))

            elif axis.dimension_type == DimensionType.SPECTRAL:
                selection.append(slice(None))
            else:
                selection.append(slice(0, 1))

        self.spectrum = self.dset[tuple(selection)].mean(axis=tuple(self.image_dims))
        # * self.intensity_scale[self.x,self.y]
        return self.spectrum.squeeze()

    def _onclick(self, event):
        self.event = event
        if event.inaxes in [self.axes[0]]:
            x = int(event.xdata)
            y = int(event.ydata)

            x = int(x - self.rectangle[0])
            y = int(y - self.rectangle[2])

            if x >= 0 and y >= 0:
                if x <= self.rectangle[1] and y <= self.rectangle[3]:
                    self.x = int(x / (self.rect.get_width() / self.bin_x))
                    self.y = int(y / (self.rect.get_height() / self.bin_y))

                    if self.x + self.bin_x > self.dset.shape[self.image_dims[0]]:
                        self.x = self.dset.shape[self.image_dims[0]] - self.bin_x
                    if self.y + self.bin_y > self.dset.shape[self.image_dims[1]]:
                        self.y = self.dset.shape[self.image_dims[1]] - self.bin_y

                    self.rect.set_xy([self.x * self.rect.get_width() / self.bin_x + self.rectangle[0],
                                      self.y * self.rect.get_height() / self.bin_y + self.rectangle[2]])
        self._update()

    def _update(self, ev=None):

        xlim = self.axes[1].get_xlim()
        ylim = self.axes[1].get_ylim()
        self.axes[1].clear()
        self.get_spectrum()

        self.axes[1].plot(self.energy_scale, self.spectrum, label='experiment')

        self.axes[1].set_title('spectrum {}, {}'.format(self.x, self.y))

        self.axes[1].set_xlim(xlim)
        self.axes[1].set_ylim(ylim)
        self.axes[1].set_xlabel(self.xlabel)
        self.axes[1].set_ylabel(self.ylabel)

        self.fig.canvas.draw_idle()

    def set_legend(self, set_legend):
        self.plot_legend = set_legend

    def get_xy(self):
        return [self.x, self.y]


class FourDimImageVisualizer(object):
    """
    ### Interactive 4D imaging plot

    Either you specify only two spatial dimensions or you specify
    scan_x and scan_y
    image_4d_x, image_4d_y

    If none of the key words are specified, it is assumed that the order is slowest to fastest dimension.

    """

    def __init__(self, dset, figure=None, horizontal=True, **kwargs):
        from sidpy import Dataset
        from sidpy import DimensionType

        if not isinstance(dset, Dataset):
            raise TypeError('dset should be a sidpy.Dataset object')

        fig_args = dict()
        temp = kwargs.pop('figsize', None)
        if temp is not None:
            fig_args['figsize'] = temp

        if figure is None:
            self.fig = plt.figure(**fig_args)
        else:
            self.fig = figure

        if len(dset.shape) < 4:
            raise KeyError('dataset must have at least four dimensions')

        # Find scan and 4D_image dimension

        scan_x = kwargs.pop('scan_x', None)
        scan_y = kwargs.pop('scan_y', None)

        image_x = kwargs.pop('image_4d_x', None)
        image_y = kwargs.pop('image_4d_y', None)
        for dim, axis in dset._axes.items():
            if axis.dimension_type in [DimensionType.SPATIAL]:
                if scan_y is None:
                    scan_y = dim
                elif scan_x is None:
                    scan_x = dim

        # We assume slow scan first order
        if scan_y is None or scan_x is None:
            scan_y = 0
            scan_x = 1

        if image_y is None:
            for dim in range(4):
                if dim not in [scan_x, scan_y]:
                    image_y = dim
                    break
        if image_x is None:
            for dim in range(4):
                if dim not in [image_y, scan_x, scan_y]:
                    image_x = dim
                    break

        image_dims = [scan_x, scan_y]
        dims_4d = [image_x, image_y]

        if len(image_dims) != 2:
            raise ValueError('We need two dimensions with dimension_type SPATIAL: to plot an image')

        if len(dims_4d) != 2:
            raise KeyError('We need two dimension with dimension_type other than spatial for a 4D image plot')

        self.horizontal = horizontal
        self.x = 0
        self.y = 0
        self.bin_x = 1
        self.bin_y = 1

        image_dims = [scan_x, scan_y]

        size_x = dset.shape[image_dims[0]]
        size_y = dset.shape[image_dims[1]]

        self.dset = dset

        self.extent = [0, size_x, size_y, 0]
        self.rectangle = [0, size_x, 0, size_y]
        self.scaleX = 1.0
        self.scaleY = 1.0
        self.analysis = []
        self.plot_legend = False

        self.image_dims = image_dims
        self.dims_4d = dims_4d

        if horizontal:
            self.axes = self.fig.subplots(ncols=2)
        else:
            self.axes = self.fig.subplots(nrows=2, **fig_args)

        self.fig.canvas.manager.set_window_title(self.dset.title)
        self.image = np.array(dset).mean(axis=tuple(dims_4d))

        self.axes[0].imshow(self.image.T, extent=self.extent, **kwargs)
        if horizontal:
            self.axes[0].set_xlabel('{} [pixels]'.format(self.dset._axes[image_dims[0]].quantity))
        else:
            self.axes[0].set_ylabel('{} [pixels]'.format(self.dset._axes[image_dims[1]].quantity))
        self.axes[0].set_aspect('equal')

        # self.rect = patches.Rectangle((0,0),1,1,linewidth=1,edgecolor='r',facecolor='red', alpha = 0.2)
        self.rect = patches.Rectangle((0, 0), self.bin_x, self.bin_y, linewidth=1, edgecolor='r',
                                      facecolor='red', alpha=0.2)

        self.axes[0].add_patch(self.rect)
        self.intensity_scale = 1.
        self.image_4d = self.get_image_4d()

        self.axes[1].imshow(self.image_4d)
        self.axes[1].set_title('spectrum {}, {}'.format(self.x, self.y))
        self.xlabel = self.dset.labels[self.dims_4d[0]]
        self.ylabel = self.dset.labels[self.dims_4d[1]]
        self.axes[1].set_xlabel(self.xlabel)  # + x_suffix)
        self.axes[1].set_ylabel(self.ylabel)
        self.axes[1].ticklabel_format(style='sci', scilimits=(-2, 3))
        self.fig.tight_layout()
        self.cid = self.axes[1].figure.canvas.mpl_connect('button_press_event', self._onclick)

        self.fig.canvas.draw_idle()

    def set_bin(self, bin_xy):

        old_bin_x = self.bin_x
        old_bin_y = self.bin_y
        if isinstance(bin_xy, list):

            self.bin_x = int(bin_xy[0])
            self.bin_y = int(bin_xy[1])

        else:
            self.bin_x = int(bin_xy)
            self.bin_y = int(bin_xy)

        if self.bin_x > self.dset.shape[self.image_dims[0]]:
            self.bin_x = self.dset.shape[self.image_dims[0]]
        if self.bin_y > self.dset.shape[self.image_dims[1]]:
            self.bin_y = self.dset.shape[self.image_dims[1]]

        self.rect.set_width(self.rect.get_width() * self.bin_x / old_bin_x)
        self.rect.set_height((self.rect.get_height() * self.bin_y / old_bin_y))
        if self.x + self.bin_x > self.dset.shape[self.image_dims[0]]:
            self.x = self.dset.shape[0] - self.bin_x
        if self.y + self.bin_y > self.dset.shape[self.image_dims[1]]:
            self.y = self.dset.shape[1] - self.bin_y

        self.rect.set_xy([self.x * self.rect.get_width() / self.bin_x + self.rectangle[0],
                          self.y * self.rect.get_height() / self.bin_y + self.rectangle[2]])
        self._update()

    def get_image_4d(self):
        from sidpy import DimensionType

        if self.x > self.dset.shape[self.image_dims[0]] - self.bin_x:
            self.x = self.dset.shape[self.image_dims[0]] - self.bin_x
        if self.y > self.dset.shape[self.image_dims[1]] - self.bin_y:
            self.y = self.dset.shape[self.image_dims[1]] - self.bin_y
        selection = []

        for dim, axis in self.dset._axes.items():
            # print(dim, axis.dimension_type)
            if dim == self.image_dims[0]:
                selection.append(slice(self.x, self.x + self.bin_x))
            elif dim == self.image_dims[1]:
                selection.append(slice(self.y, self.y + self.bin_y))

            elif dim in self.dims_4d:
                selection.append(slice(None))
            else:
                selection.append(slice(0, 1))

        self.image_4d = self.dset[tuple(selection)].mean(axis=tuple(self.image_dims))
        # * self.intensity_scale[self.x,self.y]

        return self.image_4d.squeeze()

    def _onclick(self, event):
        self.event = event
        if event.inaxes in [self.axes[0]]:
            x = int(event.xdata)
            y = int(event.ydata)

            x = int(x - self.rectangle[0])
            y = int(y - self.rectangle[2])

            if x >= 0 and y >= 0:
                if x <= self.rectangle[1] and y <= self.rectangle[3]:
                    self.x = int(x / (self.rect.get_width() / self.bin_x))
                    self.y = int(y / (self.rect.get_height() / self.bin_y))

                    if self.x + self.bin_x > self.dset.shape[self.image_dims[0]]:
                        self.x = self.dset.shape[self.image_dims[0]] - self.bin_x
                    if self.y + self.bin_y > self.dset.shape[self.image_dims[1]]:
                        self.y = self.dset.shape[self.image_dims[1]] - self.bin_y

                    self.rect.set_xy([self.x * self.rect.get_width() / self.bin_x + self.rectangle[0],
                                      self.y * self.rect.get_height() / self.bin_y + self.rectangle[2]])
        self._update()

    def _update(self, ev=None):

        xlim = self.axes[1].get_xlim()
        ylim = self.axes[1].get_ylim()
        self.axes[1].clear()
        self.get_image_4d()

        self.axes[1].imshow(self.image_4d)

        self.axes[1].set_title('set {}, {}'.format(self.x, self.y))

        self.axes[1].set_xlim(xlim)
        self.axes[1].set_ylim(ylim)
        self.axes[1].set_xlabel(self.xlabel)
        self.axes[1].set_ylabel(self.ylabel)

        self.fig.canvas.draw_idle()

    def set_legend(self, set_legend):
        self.plot_legend = set_legend

    def get_xy(self):
        return [self.x, self.y]
