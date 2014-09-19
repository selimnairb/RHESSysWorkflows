#!/usr/bin/env python
"""@package RHESSysPlot

@brief Tool for visualizing basin-scale RHESSys output.

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2014, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>

"""
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
    
    if args.scatterwidth:
        linewidth = args.scatterwidth
    else:
        linewidth = 1
    
    fig = plt.figure(figsize=(sizeX, sizeY), dpi=dpi, tight_layout=False)
    ax = fig.add_subplot(111)

    x = data[0]
    y = data[1]
    min_val = min( min(x), min(y) )
    max_val = max( max(x), max(y) )
    floor = math.floor(min_val)
    ceil = math.ceil(max_val)
    range = np.linspace(floor, ceil, 1000)
    
    if not log:
        ax.plot(data[0], data[1], '.', markersize=linewidth*6)
        ax.plot(range, range, 'k-', linewidth=linewidth)
    else:
        ax.loglog(data[0], data[1], '.', markersize=linewidth*6)
        ax.loglog(range, range, 'k-', linewidth=linewidth)
    
    # Fit line
    (m, b) = np.polyfit(x, y, 1)
    fit_y = m*range
    if not log:
        ax.plot(range, fit_y, '--', color='grey', linewidth=linewidth)
    else:
        ax.loglog(range, fit_y, '--', color='grey', linewidth=linewidth)
    
    ax.set_xlim(floor, ceil)
    ax.set_ylim(floor, ceil)
    
    # Plot annotations
    
    # Annotate fit line, making sure the annotation does not overlap 1:1 line
    if m <= 1:
        if not log:
            ax.text(0.85*ceil, 0.8*max(fit_y), "$y = %.2f x$" % (m,), 
                    fontsize=args.ticklabelfontsize)
        else:
            ax.text(0.3*ceil, 0.2*max(fit_y), "$y = %.2f x$" % (m,), 
                    fontsize=args.ticklabelfontsize)
    else:
        if not log:
            ax.text(0.65*ceil, 0.8*max(fit_y), "$y = %.2f x$" % (m,),
                    fontsize=args.ticklabelfontsize)
        else:
            ax.text(0.3*ceil, 0.2*max(fit_y), "$y = %.2f x$" % (m,), 
                    fontsize=args.ticklabelfontsize)
    
    if args.title:
        title = args.title
    else:
        title = "%s vs. %s" % (args.legend[0], args.legend[1])
    fig.suptitle(title, y=0.98, fontsize=args.titlefontsize, fontweight=args.fontweight)
    
    # X-axis
    ax.set_xlabel(args.legend[0], fontsize=args.axesfontsize, fontweight=args.fontweight)
    plt.setp(ax.get_xticklabels(), fontsize=args.ticklabelfontsize)
    
    # Y-axis
    ax.set_ylabel(args.legend[1], fontsize=args.axesfontsize, fontweight=args.fontweight)
    plt.setp(ax.get_yticklabels(), fontsize=args.ticklabelfontsize)


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
    columnName = args.column.capitalize()
    if args.title:
        title = args.title
    else:
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
        num_years = len(x) / 365
        if num_years > 4:
            if num_years > 10:
                ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
            else:
                ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
        else:
            ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b-%Y'))
        # Rotate
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=45)
        plt.setp( ax.xaxis.get_majorticklabels(), fontsize='x-small')
    
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
        if args.secondaryPlotType == 'line':
            (sec_plot,) = ax2.plot(x, sec_align)
        elif args.secondaryPlotType == 'bar':
            sec_plot = ax2.bar(x, sec_align, facecolor='blue', edgecolor='none', width=2.0)
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
                    bbox_to_anchor=(0.5, -0.01), ncol=num_cols, frameon=False )

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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--data', nargs='+',
                       help='One or more RHESSys output data files')
    group.add_argument('-b', '--behavioralData', nargs='+',
                       help='One or more ensemble output files from RHESSys behavioral runs')
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
    parser.add_argument('--titlefontsize', required=False, type=float,
                        default=12)
    parser.add_argument('--scatterwidth', required=False, type=float,
                        default=1, help='Width to use for lines and markers in scatter plots.  Markers size will be determine by multiplying scatterwidth by 6.')
    parser.add_argument('--fontweight', required=False, 
                        choices=['ultralight','light','normal','regular','book','medium','roman','semibold','demibold','demi','bold','heavy','extra bold','black'],
                        default='regular')
    parser.add_argument('--legendfontsize', required=False, type=float,
                        default=6)
    parser.add_argument('--axesfontsize', required=False, type=float,
                        default=12)
    parser.add_argument('--ticklabelfontsize', required=False, type=float,
                        default=12)
    parser.add_argument('--figureX', required=False, type=int, default=4,
                        help='The width of the plot, in inches')
    parser.add_argument('--figureY', required=False, type=int, default=3,
                        help='The height of the plot, in inches')
    parser.add_argument('--supressObs', required=False, action='store_true',
                        help='Do not plot observed data.  Observed data will still be used for aligning timeseries. Not applicable to scatter plot output.')
    parser.add_argument('--secondaryData', required=False,
                        help='A data file containing the varaible to plot on a secondary Y-axis')
    parser.add_argument('--secondaryPlotType', required=False, choices=['bar', 'line'], default='bar',
                        help='Type of plot to use for secondary data.')
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
    
    if args.data and ( len(args.data) != len(args.legend) ):
        sys.exit('Number of legend items must equal the number of data files')
    elif args.behavioralData and ( len(args.behavioralData) != len(args.legend) ):
        sys.exit('Number of legend items must equal the number of data files')

    # Open data and align to observed
    obs_align = None
    data = []
    max_x = min_x = 0
    
    if args.data:
        # Open observed data
        obs_file = open(args.obs, 'r')
        (obs_datetime, obs_data) = RHESSysOutput.readObservedDataFromFile(obs_file,
                                                                          readHour=False)
        obs_file.close()
        obs = pd.Series(obs_data, index=obs_datetime)
        
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
    elif args.behavioralData:
        
        # Open observed data (behavioral data has hour in it, so we need to read obs. data differently)
        obs_file = open(args.obs, 'r')
        (obs_datetime, obs_data) = RHESSysOutput.readObservedDataFromFile(obs_file,
                                                                          readHour=True)
        obs_file.close()
        obs = pd.Series(obs_data, index=obs_datetime)
        
        for b in args.behavioralData:
            tmp_mod = pd.read_csv(b, index_col=0, parse_dates=True)
            # Convert df to series
            tmp_mod = pd.Series(tmp_mod[args.column], index=tmp_mod.index)
            # Align timeseries
            (mod_align, obs_align) = tmp_mod.align(obs, join='inner')
            tmp_max_x = max(mod_align.max(), obs_align.max())
            if tmp_max_x > max_x:
                max_x = tmp_max_x
            min_x = max(min_x, mod_align.min())
        
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
