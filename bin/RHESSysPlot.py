#!/usr/bin/env python
# TODO: Add ability to plot all three plot types in one figure
# TODO: Add table plot type that print summary statistics for column
import sys
import argparse
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib

from rhessysworkflows.rhessys import RHESSysOutput

PLOT_TYPE_STD = 'standard'
PLOT_TYPE_LOGY = 'logy'
PLOT_TYPE_CDF = 'cdf'
PLOT_TYPE_SCATTER = 'scatter'
PLOT_TYPE_SCATTER_LOG = 'scatter-log'
PLOT_TYPES = [PLOT_TYPE_STD, PLOT_TYPE_LOGY, PLOT_TYPE_CDF, PLOT_TYPE_SCATTER, PLOT_TYPE_SCATTER_LOG]
PLOT_DEFAULT = PLOT_TYPE_STD

LINE_TYPE_LINE = 'line'
LINE_TYPE_DASH = 'dash'
LINE_TYPE_DASH_DOT = 'dashdot'
LINE_TYPE_COLON = 'colon'
LINE_TYPE_DOT = 'dot'
LINE_TYPE_DICT = { LINE_TYPE_LINE: '-',
                   LINE_TYPE_DASH: '--',
                   LINE_TYPE_DASH_DOT: '-.',
                   LINE_TYPE_COLON: ':',
                   LINE_TYPE_DOT: '.' }
LINE_TYPES = [LINE_TYPE_LINE, LINE_TYPE_DASH, LINE_TYPE_DASH_DOT, LINE_TYPE_COLON, LINE_TYPE_DOT]
NUM_LINE_TYPES = len(LINE_TYPES)


def plotGraphScatter(args, obs, data, log=False, sizeX=1, sizeY=1, dpi=80):
    
    assert( len(data) == len(args.legend) == 2 )
    
    fig = plt.figure(figsize=(sizeX, sizeY), dpi=dpi, tight_layout=True)
    ax = fig.add_subplot(111)

    x = data[0]
    y = data[1]
    one_to_one = np.linspace(math.floor(min(x)), math.ceil(max(x)), 1000)
    
    ax.plot(data[0], data[1], '.')
    ax.plot(one_to_one, one_to_one, 'k-')
    
    if log:
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    # Plot annotations
    if args.title:
        title = args.title
    else:
        title = "%s vs. %s" % (args.legend[0], args.legend[1])
    fig.suptitle(title, y=0.99)
    
    # X-axis
    ax.set_xlabel(args.legend[0])
    
    # Y-axis
    ax.set_ylabel(args.legend[1])


def plotGraph(args, obs, data, sizeX=1, sizeY=1, dpi=80):
    
    fig = plt.figure(figsize=(sizeX, sizeY), dpi=dpi, tight_layout=True)
    ax = fig.add_subplot(111)
    
    if args.plottype == PLOT_TYPE_STD or \
       args.plottype == PLOT_TYPE_LOGY:
        x = obs.index
    elif args.plottype == PLOT_TYPE_CDF:
        x = np.linspace(min_x, max_x, num=len(obs) )
    
    # Plot observed values
    # Standard or log plot
    obs_y = obs
    if args.plottype == PLOT_TYPE_CDF:
        obs_ecdf = sm.distributions.ECDF(obs)
        obs_y = obs_ecdf(x)
    obs_plt = None
    if not args.supressObs:
        (obs_plt,) = ax.plot(x, obs_y, linewidth=2.0, color='black')
        
    # Plot modeled values 
    data_plt = []
    for (i, d) in enumerate(data):
        # Standard or log plot
        mod_y = d
        if args.plottype == PLOT_TYPE_CDF:
            mod_ecdf = sm.distributions.ECDF(d)
            mod_y = mod_ecdf(x)
        
        # Plot (we could move this outside of the for loop)
        if args.linewidth:
            linewidth = args.linewidth[i]
        else:
            linewidth = 1.0
            
        if args.linestyle:
            linestyle = LINE_TYPE_DICT[ args.linestyle[i] ]
        else:
            # Rotate styles
            styleIdx = ( (i + 1) % NUM_LINE_TYPES ) - 1
            linestyle = LINE_TYPE_DICT[ LINE_TYPES[styleIdx] ]
            
        if args.color:
            (mod_plt,) = ax.plot(x, mod_y, linewidth=linewidth, linestyle=linestyle,
                                 color=args.color[i])
        else:
            (mod_plt,) = ax.plot(x, mod_y, linewidth=linewidth, linestyle=linestyle)
        
        data_plt.append(mod_plt)
    
    # Plot annotations
    if args.title:
        title = args.title
    else:
        columnName = args.column.capitalize()
        if args.plottype == PLOT_TYPE_STD:
            title = columnName
        elif args.plottype == PLOT_TYPE_LOGY:
            title = "log(%s)" % (columnName,)
        elif args.plottype == PLOT_TYPE_CDF:
            title = "Cummulative distribution - %s" % (columnName,) 
    fig.suptitle(title, y=0.99)

    # X-axis
    if args.plottype == PLOT_TYPE_STD or \
       args.plottype == PLOT_TYPE_LOGY:
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator() )
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b-%Y') )
        # Rotate
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=45 )
        plt.setp( ax.xaxis.get_majorticklabels(), fontsize='x-small' )
    
    if args.plottype == PLOT_TYPE_CDF:
        ax.set_xlim(min_x, max_x)
        ax.set_xscale('log')
        if args.xlabel:
            ax.set_xlabel(args.xlabel)
        else:
            ax.set_xlabel( columnName )
    elif args.xlabel:
        ax.set_xlabel(args.xlabel)
    
    # Y-axis
    if args.plottype == PLOT_TYPE_LOGY:
        ax.set_yscale('log')
    
    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    elif args.plottype != PLOT_TYPE_CDF:
        y_label = columnName
        if args.plottype == PLOT_TYPE_LOGY:
            y_label = "log( %s )" % (columnName,)
        ax.set_ylabel( y_label )
    
    if args.supressObs:
        legend_items = args.legend
    else:
        data_plt.insert(0, obs_plt)
        legend_items = ['Observed'] + args.legend
    
    # Plot secondary data (if specified)
    if args.secondaryData and \
       (args.plottype == PLOT_TYPE_STD or args.plottype == PLOT_TYPE_LOGY):
        sec_file = open(args.secondaryData, 'r')
        (sec_datetime, sec_data) = RHESSysOutput.readColumnFromFile(sec_file,
                                                                                   args.secondaryColumn,
                                                                                   startHour=0)
        sec_file.close()
        sec = pd.Series(sec_data, index=sec_datetime)
        # Align timeseries
        (sec_align, obs_align) = sec.align(obs, join='inner')
        # Plot
        ax2 = ax.twinx()
        (sec_plot,) = ax2.plot(x, sec_align)
        secondaryLabel = args.secondaryColumn.capitalize()
        if args.secondaryLabel:
            secondaryLabel = args.secondaryLabel
        ax2.invert_yaxis()
        ax2.set_ylabel(args.secondaryLabel)
    #ax.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2
    #ax.patch.set_visible(False) # hide the 'canvas' 
    
    # Plot legend last
    num_cols = len(data)
    if not args.supressObs:
        num_cols += 1
    
    if args.plottype == PLOT_TYPE_CDF:
        fig.legend( data_plt, legend_items, 'lower center', fontsize='x-small', 
                    bbox_to_anchor=(0.5, -0.015), ncol=num_cols, frameon=False )
    else:
        fig.legend( data_plt, legend_items, 'lower center', fontsize='x-small', 
                    bbox_to_anchor=(0.5, -0.03), ncol=num_cols, frameon=False )

if __name__ == "__main__":
    # Handle command line options
    parser = argparse.ArgumentParser(description='Plot CDF of N datasets vs. observed data')
    parser.add_argument('-p', '--plottype', required=False, 
                        default=PLOT_DEFAULT, choices=PLOT_TYPES,
                        help='Type of plot')
    parser.add_argument('-f', '--outfileSuffix', required=False,
                        help='Suffix to append on to name part of file name (i.e. before extension)')
    parser.add_argument('-o', '--obs', required=True,
                        help='File containing observed data')
    parser.add_argument('-d', '--data', required=True, nargs='+',
                        help='One or more data files')
    parser.add_argument('--color', required=False, nargs='+',
                        help='Color of symbol to be applied to plots of data. Color must be expressed in form recognized by matplotlib.')
    parser.add_argument('--linewidth', required=False, nargs='+', type=float,
                        help='Width of lines to be applied to plots of data. Value must be float in units of points.')
    parser.add_argument('--linestyle', required=False, nargs='+', choices=LINE_TYPES,
                        help='Style of symbol to be applied to plots of data. Styles correspond to those of matplotlib.')
    parser.add_argument('-c', '--column', required=True,
                        help='Name of column to use from data files')
    parser.add_argument('-t', '--title', required=False,
                        help='Title of figure')
    parser.add_argument('-l', '--legend', required=True, nargs='+',
                        help='Legend item labels')
    parser.add_argument('-x', '--xlabel', required=False,
                        help='X-axis label')
    parser.add_argument('-y', '--ylabel', required=False,
                        help='Y-axis label')
    parser.add_argument('--figureX', required=False, type=int, default=4,
                        help='The width of the plot, in inches')
    parser.add_argument('--figureY', required=False, type=int, default=3,
                        help='The height of the plot, in inches')
    parser.add_argument('--supressObs', required=False, action='store_true',
                        help='Do not plot observed data.  Observed data will still be used for aligning timeseries')
    parser.add_argument('--secondaryData', required=False,
                        help='A data file containing the varaible to plot on a secondary Y-axis')
    parser.add_argument('--secondaryColumn', required=False,
                        help='Name of column to use from secondary data file')
    parser.add_argument('--secondaryLabel', required=False,
                        help='Label to use for seconary Y-axis')
    args = parser.parse_args()
    
    if args.color:
        if len(args.color) != len(args.data):
            sys.exit('Number of colors must match number of data files')
    
    if args.linewidth:
        if min(args.linewidth) <= 0.0:
            sys.exit('All line widths must be > 0.0')
        if len(args.linewidth) != len(args.data):
            sys.exit('Number of line widths must match number of data files')
            
    if args.linestyle:
        if len(args.linestyle) != len(args.data):
            sys.exit('Number of line styles must match number of data files')
    
    if args.secondaryData and not args.secondaryColumn:
        sys.exit('A secondary data file was specified, but the secondary column to use was not')
    
    if len(args.data) != len(args.legend):
        sys.exit('Number of legend items must equal the number of data files')

    # Open observed data
    obs_file = open(args.obs, 'r')
    (obs_datetime, obs_data) = RHESSysOutput.readObservedDataFromFile(obs_file,
                                                                                     readHour=False)
    obs_file.close()
    obs = pd.Series(obs_data, index=obs_datetime)

    # Open data and align to observed
    obs_align = None
    data = []
    max_x = min_x = 0
    for d in args.data:
        mod_file = open(d, 'r')
        (tmp_datetime, tmp_data) = RHESSysOutput.readColumnFromFile(mod_file, args.column, startHour=0)
        tmp_mod = pd.Series(tmp_data, index=tmp_datetime)
        # Align timeseries
        (mod_align, obs_align) = tmp_mod.align(obs, join='inner')
        tmp_max_x = max(mod_align.max(), obs_align.max())
        if tmp_max_x > max_x:
            max_x = tmp_max_x
        min_x = max(min_x, mod_align.min())
    
        mod_file.close()
        data.append( mod_align )

    if args.plottype == PLOT_TYPE_SCATTER:
        plotGraphScatter(args, obs_align, data, log=False, 
                         sizeX=args.figureX, sizeY=args.figureY)
    elif args.plottype == PLOT_TYPE_SCATTER_LOG:
        plotGraphScatter(args, obs_align, data, log=True, 
                         sizeX=args.figureX, sizeY=args.figureY)
    else:
        plotGraph(args, obs_align, data, 
                  sizeX=args.figureX, sizeY=args.figureY)

    # Output plot
    filename = args.plottype
    if args.outfileSuffix:
        filename += '_' + args.outfileSuffix
    plot_filename_png = "%s.png" % (filename,)
    plot_filename_pdf = "%s.pdf" % (filename,)
    plt.savefig(plot_filename_png)
    plt.savefig(plot_filename_pdf)
