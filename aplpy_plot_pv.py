#####################################################################
#                          APLPY PLOTTING                           #
#####################################################################
# These functions will produce plots of channel maps, moment maps,  #
# pV diagrams, ... in a quality that (hopefully) allows publishing. #
#####################################################################

# I know that I shouldn't use dozens of if-else statements but rather try-except to get correct 
# handling of exceptions. When I started wrinting this code I didn't know what exception could
# do for my case and right now I don't have time to change this script.

###################################################################################################

import aplpy_plotting as ap

import os as __os__
import aplpy as __aplpy__
import numpy as __np__
from astropy import units as __u__
from matplotlib import rc as __rc__
__rc__('text',usetex=True)
from matplotlib.cbook import MatplotlibDeprecationWarning as __MatplotlibDeprecationWarning__
import warnings as __warnings__
__warnings__.simplefilter('ignore', __MatplotlibDeprecationWarning__)

###################################################################################################

def aplpy_plot_pv(fitspv, **kwargs):
    
    """
    aplpy_plot_pv: position-velocity slice plotting
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Mandatory unnamed arguments:
        fitspv      Path and file name of the fits image to be plotted. This must
                    have one velocity axis and one spatial (offset) axis, such as
                    generated by CASA impv().
        

    Optional arguments:
        out         Path and file name of the created plot.
                    If not specified, the plot will be saved where the input image
                    is located. Default format: png
        
        figsize     Fiugre size as tpuel in inches. No default.
        
        xlabel      Label of the xaxis. As the PV slice can be calculated in 
                    arbitrary direction, this can be just an offset or along a
                    coordniate axis (e.g. RA).
        ylabel      Label of the yaxis. Both labels or none must be given.
                    If neither xlabel, nor ylabel is specified, the header 
                    information is used.
        
        cmap        Colormap to plot the image.
                    If not specified, the matplotlib default will be used, usually
                    this is viridis.
                    Every named matplotlib colormap can be used or any matplotlib 
                    colormap object.
                    For grayscale use cmap='grayscale'
                    
        vmin        Minimum value for colormap normalization.
        vmax        Maximum value for colormap normalization.
        
        stretch     Colormap strech, e.g. 'linear', 'log', 'sqrt', 'arcsinh'.
                    Linear and log scaling are fully implemented, other scaling can
                    cause errors when unusual argument combinations are chosen.
        
        recenter    Center the image on this location and set image width and height.
                    Needs to be given with the correct units, i.e. km/s if the 
                    image is defined as km/s. No automatic rescaling.

        contour     List of contour elements.
                    Each contour element must be a list of 'image file', list of 
                    contour levels and list of colors for each contour. If only one
                    color is given, it will be used for all contours.
                    
        colorbar_location   As the name says.
                            Can be, e.g. 'bottom', 'right', ...
        colorbar_label      Can be specified only when colorbar_location is given.
                            String containing the label.

        label_text          List of labels to label to individual panels. Default is
                            to get a label from the file name without extension and
                            path.
        label_kwargs        Keyword arguments to format the label. All plt.text
                            kwargs are allowed, especially bbox=props can be used.
                            See example below.
    
    
    General style settings
        Settings that do not have to be changed for each plot but maybe once per 
        script or once per project. Often used ones are tick_label_xformat, 
        ticks_xspacing and the corresponding settings for y.
            Can be accessed via
        import aplpy_plotting as ap
        ap.setting = ...
        See the aplpy_plotting.py main file for the exact setting names if you need
        to change them.


    example:
    
    aplpy_plot_pv('abc.fits', 
                  figsize  = (8.27, 11.69),
                  vmin     = 0,
                  vmax     = 100,
                  stretch  = 'linear',
                  cmap     = ap.viridis_cropped,
                  recenter = [0, 0, 5, 100],
                  contour  = [['xyz.fits', [1,2,3], 'black']], 
                  colorbar_location = 'right', 
                  colorbar_label = 'intensity [Jy\,beam$^{-1}$]', 
                  xlabel   = 'offset [arcsec]', 
                  ylabel   = 'velocity [km\,s$^{-1}$', 
                  out      = 'abc.png'
                  )
    """
    
    print("--> plotting map "+fitspv)
    
    if 'figsize' in kwargs:
        fig = __aplpy__.FITSFigure(fitspv, figsize=kwargs['figsize'])
    else:
        fig = __aplpy__.FITSFigure(fitspv)
    
    if 'vmin' and 'vmax' in kwargs:
        if 'stretch' in kwargs:
            if 'cmap' in kwargs:
                if kwargs['cmap'] == 'grayscale':
                    fig.show_grayscale(vmin=kwargs['vmin'], vmax=kwargs['vmax'], stretch=kwargs['stretch'], aspect='auto')
                else:
                    fig.show_colorscale(cmap=kwargs['cmap'], vmin=kwargs['vmin'], vmax=kwargs['vmax'], stretch=kwargs['stretch'], aspect='auto')
            else:
                fig.show_colorscale(vmin=kwargs['vmin'], vmax=kwargs['vmax'], stretch=kwargs['stretch'], aspect='auto')
        else:
            fig.show_colorscale(vmin=kwargs['vmax'], vmax=kwargs['vmax'], aspect='auto')
    else:
        fig.show_colorscale(aspect='auto')
        
    # recenter image
    if 'recenter' in kwargs:
        fig.recenter(kwargs['recenter'][0], kwargs['recenter'][1], width=kwargs['recenter'][2], height=kwargs['recenter'][3])
    
    # contours?
    if 'contour' in kwargs:
        for cont_i in __np__.arange(len(kwargs['contour'])):
            if len(kwargs['contour'][cont_i]) == 3:
                fig.show_contour(data=kwargs['contour'][cont_i][0], levels=kwargs['contour'][cont_i][1], colors=kwargs['contour'][cont_i][2])
            else:
                print("--> wrong number or format of contour parameters in image "+str(cont_i)+". not plotting contours")

    # colorbar settings
    if 'colorbar_location' in kwargs:
        fig.add_colorbar()
        fig.colorbar.show()
        fig.colorbar.set_location(kwargs['colorbar_location'])
        if 'colorbar_label' in kwargs:
            fig.colorbar.set_axis_label_text(kwargs['colorbar_label'])
        if 'stretch' in kwargs:
            if (kwargs['stretch'] == 'log'):
                log_ticks = [float('{:.2f}'.format(round(x,int(-1*__np__.log10(kwargs['vmin']))))) for x in __np__.logspace(__np__.log10(kwargs['vmin']),__np__.log10(kwargs['vmax']),num=10, endpoint=True)]
                fig.colorbar.set_ticks(log_ticks)

    # scale bar
    # not possible with CTYPE='OFFSET'

    # ticks + labels
    fig.tick_labels.show()
#   fig.tick_labels.set_xformat(ap.tick_label_xformat_pv)
#   fig.tick_labels.set_yformat(ap.tick_label_yformat_pv)
    fig.ticks.show()
#   fig.ticks.set_xspacing(ap.ticks_xspacing.to(__u__.degree).value)
#   fig.ticks.set_yspacing(ap.ticks_yspacing.to(__u__.degree).value)
    fig.ticks.set_minor_frequency(ap.ticks_minor_frequency)
    fig.ticks.set_color(ap._ticks_color)
    
    # axis labels
    if 'xlabel' and 'ylabel' in kwargs:
        fig.set_axis_labels(kwargs['xlabel'],kwargs['ylabel'])
    else:
        print("--> you need to give both labels")

    # data set overlay
    if 'label_text' in kwargs:
        fig.add_label(0.1, 0.9, kwargs['label_text'].replace('_','$\_$'), color='black', relative=True, size=ap._velo_fontsize)
        if 'label_kwargs' in kwargs:
            fig.add_label(0.5, 0.9, kwargs['label_text'].replace('_','$\_$'), color='black', relative=True, size=ap._velo_fontsize, **kwargs['label_kwargs'])
    
    # write plot to disk
    if 'out' in kwargs:
        fig.save(kwargs['out'], dpi=300, transparent=True)
        print("--> saved file as "+kwargs['out'])
    else:
        fig.save(__os__.path.splitext(fitspv)[0]+'.png', dpi=300, transparent=True)
        print("--> saved plot as "+__os__.path.splitext(fitspv)[0]+'.png')



###################################################################################################
