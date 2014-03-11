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

from rhessyscalibrator.postprocess import RHESSysCalibratorPostprocess

PLOT_TYPE_STD = 'standard'
PLOT_TYPE_LOGY = 'logy'
PLOT_TYPE_CDF = 'cdf'
PLOT_TYPES = [PLOT_TYPE_STD, PLOT_TYPE_LOGY, PLOT_TYPE_CDF]
PLOT_DEFAULT = PLOT_TYPE_STD


def plotGraph(args, obs, data):
    
    if args.plottype == PLOT_TYPE_STD or \
       args.plottype == PLOT_TYPE_LOGY:
        x = obs.index
    elif args.plottype == PLOT_TYPE_CDF:
        x = np.linspace(min_x, max_x, num=1000 )
    
    # Plot observed values
    # Standard or log plot
    obs_y = obs
    if args.plottype == PLOT_TYPE_CDF:
        obs_ecdf = sm.distributions.ECDF(obs)
        obs_y = obs_ecdf(x)
    obs_plt = None
    if not args.supressObs:
        (obs_plt,) = plt.plot(x, obs_y)
    ax = plt.gca()
        
    # Plot modeled values
    data_plt = []
    for d in data:
        # Standard or log plot
        mod_y = d
        if args.plottype == PLOT_TYPE_CDF:
            mod_ecdf = sm.distributions.ECDF(d)
            mod_y = mod_ecdf(x)
        (mod_plt,) = plt.plot(x, mod_y)
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
    plt.title(title)
    
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
        plt.xscale('log')
        if args.xlabel:
            plt.xlabel(args.xlabel)
        else:
            plt.xlabel( columnName )
    elif args.xlabel:
        plt.xlabel(args.xlabel)
    
    # Y-axis
    if args.plottype == PLOT_TYPE_LOGY:
        plt.yscale('log')
    
    if args.ylabel:
        plt.ylabel(args.ylabel)
    elif args.plottype != PLOT_TYPE_CDF:
        y_label = columnName
        if args.plottype == PLOT_TYPE_LOGY:
            y_label = "log( %s )" % (columnName,)
        plt.ylabel( y_label )
    
    if args.supressObs:
        legend_items = args.legend
    else:
        data_plt.insert(0, obs_plt)
        legend_items = ['Observed'] + args.legend
    
    # Plot secondary data (if specified)
    if args.secondaryData and \
       (args.plottype == PLOT_TYPE_STD or args.plottype == PLOT_TYPE_LOGY):
        sec_file = open(args.secondaryData, 'r')
        (sec_datetime, sec_data) = RHESSysCalibratorPostprocess.readColumnFromFile(sec_file,
                                                                                   args.secondaryColumn)
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
    
    # Plot legend last
    if args.plottype == PLOT_TYPE_CDF:
        plt.legend( data_plt, legend_items, 'lower right', fontsize='x-small' )
    elif args.secondaryData:
        plt.legend( data_plt, legend_items, 'center right', fontsize='x-small' )
    else:
        plt.legend( data_plt, legend_items, 'best', fontsize='x-small' )

if __name__ == "__main__":
    # Handle command line options
    parser = argparse.ArgumentParser(description='Plot CDF of N datasets vs. observed data')
    parser.add_argument('-p', '--plottype', required=False, 
                        default=PLOT_DEFAULT, choices=PLOT_TYPES,
                        help='Type of plot')
    parser.add_argument('-o', '--obs', required=True,
                        help='File containing observed data')
    parser.add_argument('-d', '--data', required=True, nargs='+',
                        help='One or more data files')
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
    parser.add_argument('--supressObs', required=False, action='store_true',
                        help='Do not plot observed data.  Observed data will still be used for aligning timeseries')
    parser.add_argument('--secondaryData', required=False,
                        help='A data file containing the varaible to plot on a secondary Y-axis')
    parser.add_argument('--secondaryColumn', required=False,
                        help='Name of column to use from secondary data file')
    parser.add_argument('--secondaryLabel', required=False,
                        help='Label to use for seconary Y-axis')
    args = parser.parse_args()
    
    if args.secondaryData and not args.secondaryColumn:
        sys.exit('A secondary data file was specified, but the secondary column to use was not')
    
    if len(args.data) != len(args.legend):
        sys.exit('Number of legend items must equal the number of data files')

    # Open observed data
    obs_file = open(args.obs, 'r')
    (obs_datetime, obs_data) = RHESSysCalibratorPostprocess.readObservedDataFromFile(obs_file)
    obs_file.close()
    obs = pd.Series(obs_data, index=obs_datetime)

    # Open data and align to observed
    obs_align = None
    data = []
    max_x = min_x = 0
    for d in args.data:
        mod_file = open(d, 'r')
        (tmp_datetime, tmp_data) = RHESSysCalibratorPostprocess.readColumnFromFile(mod_file,
        args.column)
        tmp_mod = pd.Series(tmp_data, index=tmp_datetime)
        # Align timeseries
        (mod_align, obs_align) = tmp_mod.align(obs, join='inner')
        tmp_max_x = max(mod_align.max(), obs_align.max())
        if tmp_max_x > max_x:
            max_x = tmp_max_x
        min_x = max(min_x, mod_align.min())
    
        mod_file.close()
        data.append( mod_align )

    plotGraph(args, obs_align, data)

    # Output plot
    plot_filename_png = "%s.png" % (args.plottype,)
    plot_filename_pdf = "%s.pdf" % (args.plottype,)
    plt.savefig(plot_filename_png)
    plt.savefig(plot_filename_pdf)
