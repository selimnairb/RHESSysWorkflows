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
PLOT_TYPE_TABLE = 'table'
PLOT_TYPES = [PLOT_TYPE_STD, PLOT_TYPE_LOGY, PLOT_TYPE_CDF, PLOT_TYPE_TABLE]
PLOT_DEFAULT = PLOT_TYPE_STD


def plotTable(args, col_names, obs, data, ax):
    
    #import pdb; pdb.set_trace()
    
    data = np.append( [np.sum(obs['observed'])], np.sum(data['streamflow']) )
    text = [ ["%.2f" % num for num in data] ]
    #nrows, ncols = len(data)+1, len(col_names)
    #hcell, wcell = 0.3, 1.
    #hpad, wpad = 0, 0    
    #fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
    ax.axis('off')
    #do the table
    table = ax.table(cellText=text,
                     colLabels=col_names,
                     rowLabels=['Streamflow (mm)'],
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    

def plotGraph(args, plottype, obs, data, columns, min_x, max_x, ax, secondary=None):
    
    if plottype == PLOT_TYPE_STD or \
       plottype == PLOT_TYPE_LOGY:
        x = obs.index
    elif plottype == PLOT_TYPE_CDF:
        #import pdb; pdb.set_trace()
        x = np.linspace(min_x, max_x, num=1000 )
    
    # Plot observed values
    # Standard or log plot
    obs_y = obs
    if plottype == PLOT_TYPE_CDF:
        #import pdb; pdb.set_trace()
        obs_ecdf = sm.distributions.ECDF(obs['observed'])
        obs_y = obs_ecdf(x)
    obs_plt = None
    if not args.supressObs:
        (obs_plt,) = ax.plot(x, obs_y)
        
    # Plot modeled values
    data_plt = []
    for c in columns:
        # Standard or log plot
        mod_y = data[c]
        if plottype == PLOT_TYPE_CDF:
            mod_ecdf = sm.distributions.ECDF(data[c])
            mod_y = mod_ecdf(x)
        (mod_plt,) = ax.plot(x, mod_y)
        data_plt.append(mod_plt)
    
    # X-axis
    if plottype == PLOT_TYPE_STD or \
       plottype == PLOT_TYPE_LOGY:
        quarterly = matplotlib.dates.MonthLocator(interval=3)
        ax.xaxis.set_major_locator(quarterly)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b-%Y') )
        # Rotate
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=45 )
        plt.setp( ax.xaxis.get_majorticklabels(), fontsize='x-small' )
    
    if plottype == PLOT_TYPE_CDF:
        ax.set_xlim(min_x, max_x)
        ax.set_xscale('log')
        if args.xlabel:
            ax.set_xlabel(args.xlabel)
        else:
            pass
            ax.set_xlabel( 'Streamflow ($mm^{-day}$)' )
    elif args.xlabel:
        ax.set_xlabel(args.xlabel)
    
    # Y-axis
    if plottype == PLOT_TYPE_LOGY:
        ax.set_yscale('log')
    
    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    elif plottype != PLOT_TYPE_CDF and plottype != PLOT_TYPE_LOGY:
        y_label = 'Streamflow ($mm^{-day}$)'
        ax.set_ylabel( y_label )
    
    if args.supressObs:
        legend_items = columns
    else:
        data_plt.insert(0, obs_plt)
        legend_items = ['Observed'] + columns
    
    # Plot secondary data (if specified)
    if secondary and \
        (plottype == PLOT_TYPE_STD or plottype == PLOT_TYPE_LOGY):
        sec_file = open(args.secondaryData, 'r')
        (sec_datetime, sec_data) = RHESSysOutput.readColumnFromFile(sec_file,
                                                                    args.secondaryColumn,
                                                                    startHour=0)
        sec_file.close()
        #sec = pd.Series(sec_data, index=sec_datetime)
#         import pdb; pdb.set_trace()
        sec = pd.DataFrame(sec_data, index=sec_datetime, columns=[args.secondaryColumn])
        # Align timeseries
        (sec_align, obs_align) = sec.align(obs, join='inner')
        (sec_align, data_align) = sec.align(data, axis=0, join='inner')
        # Plot
        ax2 = ax.twinx()
        for s in secondary:
            if args.secondaryPlotType == 'line':
                (sec_plot,) = ax2.plot(x, data[s])
            elif args.secondaryPlotType == 'bar':
                sec_plot = ax2.bar(x, data[s], facecolor='blue', edgecolor='none', width=2.0)
        secondaryLabel = args.secondaryColumn.capitalize()
        if args.secondaryLabel:
            secondaryLabel = args.secondaryLabel
        ax2.invert_yaxis()
        ax2.set_ylabel(args.secondaryLabel)
    
    # Plot legend last
    if plottype == PLOT_TYPE_CDF:
        ax.legend( data_plt, legend_items, 'lower right', fontsize='x-small' )
    elif secondary:
        ax.legend( data_plt, legend_items, 'center right', fontsize='x-small' )
    else:
        ax.legend( data_plt, legend_items, 'best', fontsize='x-small' )

if __name__ == "__main__":
    # Handle command line options
    parser = argparse.ArgumentParser(description='Plot CDF of N datasets vs. observed data')
    parser.add_argument('-n', '--outname', required=True, 
                        help='Base name of file to output figure to.  Only specify base name of file, not extension (PDF and PNG files will be produced)')
    parser.add_argument('-o', '--obs', required=True,
                        help='File containing observed data')
    parser.add_argument('-d', '--data', required=True, #nargs='+',
                        help='One or more data files')
#     parser.add_argument('-c', '--column', required=True,
#                         help='Name of column to use from data files')
    parser.add_argument('-t', '--title', required=False,
                        help='Title of figure')
#     parser.add_argument('-l', '--legend', required=True, nargs='+',
#                         help='Legend item labels')
    parser.add_argument('-x', '--xlabel', required=False,
                        help='X-axis label')
    parser.add_argument('-y', '--ylabel', required=False,
                        help='Y-axis label')
    parser.add_argument('--figureX', required=False, type=int, default=8,
                        help='The width of the plot, in inches')
    parser.add_argument('--figureY', required=False, type=int, default=6,
                        help='The height of the plot, in inches')
    parser.add_argument('--supressObs', required=False, action='store_true',
                        help='Do not plot observed data.  Observed data will still be used for aligning timeseries')
    parser.add_argument('--secondaryData', required=False,
                        help='A data file containing the varaible to plot on a secondary Y-axis')
    parser.add_argument('--secondaryPlotType', required=False, choices=['bar', 'line'], default='bar',
                        help='Type of plot to use for secondary data.')
    parser.add_argument('--secondaryColumn', required=False,
                        help='Name of column to use from secondary data file')
    parser.add_argument('--secondaryLabel', required=False,
                        help='Label to use for seconary Y-axis')
    args = parser.parse_args()
    
    if args.secondaryData and not args.secondaryColumn:
        sys.exit('A secondary data file was specified, but the secondary column to use was not')
    
#     if len(args.data) != len(args.legend):
#         sys.exit('Number of legend items must equal the number of data files')

    # Open observed data
    obs_file = open(args.obs, 'r')
    (obs_datetime, obs_data) = RHESSysOutput.readObservedDataFromFile(obs_file,
                                                                      readHour=False)
    obs_file.close()
    obs = pd.DataFrame(obs_data, index=obs_datetime, columns=['observed'])

    # Open data and align to observed
    cols = ['streamflow', 'evap', 'trans', 'precip']
    obs_align = None
    max_x = min_x = 0
    mod_file = open(args.data, 'r')
    mod_df = RHESSysOutput.readColumnsFromFile(mod_file, cols)
    
    # Align timeseries
    (mod_align, obs_align) = mod_df.align(obs, axis=0, join='inner')
    tmp_max_x = max(mod_align['streamflow'].max(), obs_align['observed'].max())
    if tmp_max_x > max_x:
        max_x = tmp_max_x
    min_x = max(min_x, mod_align['streamflow'].min())

    mod_file.close()
    #data.append( mod_align )

    fig = plt.figure(figsize=(args.figureX, args.figureY), dpi=80, tight_layout=True)
    ax_std = fig.add_subplot(221)
    ax_log = fig.add_subplot(222)
    ax_cdf = fig.add_subplot(223)
    ax_tab = fig.add_subplot(224)

    #import pdb; pdb.set_trace()

    plotGraph(args, PLOT_TYPE_STD, obs_align, mod_align, ['streamflow'], min_x, max_x, ax_std, secondary=['precip'])
    plotGraph(args, PLOT_TYPE_LOGY, obs_align, mod_align, ['streamflow'], min_x, max_x, ax_log)
    plotGraph(args, PLOT_TYPE_CDF, obs_align, mod_align, ['streamflow'], min_x, max_x, ax_cdf)
    
    col_names = ['Observed', 'Modeled']
    plotTable(args, col_names, obs_align, mod_align, ax_tab)

    # Figure annotations
    if args.title:
        fig.suptitle(args.title, y=1.01)

    # Output plot
    plot_filename_png = "%s.png" % (args.outname,)
    plot_filename_pdf = "%s.pdf" % (args.outname,)
    plt.savefig(plot_filename_png, bbox_inches='tight') #, bbox_extra_artists=[table])
    plt.savefig(plot_filename_pdf, bbox_inches='tight') #, bbox_extra_artists=[table])
