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
    
    startDate = data['streamflow'].index[0]
    endDate = data['streamflow'].index[-1]
    
    obsRunoffRat = np.sum( obs['observed'] ) / np.sum( data['precip'] )
    modRunoffRat = np.sum( data['streamflow']) / np.sum( data['precip'] )
    obsET = np.sum( data['precip'] ) - np.sum( obs['observed'] )
    summary = [ [ np.sum( data['precip'] ), np.sum( data['precip'] ) ],
                [ np.sum(obs['observed']), np.sum(data['streamflow']) ],
                [ obsET, np.sum( data['evap'] ) + np.sum( data['trans'] ) ],
                [ obsRunoffRat, modRunoffRat ]
              ]
    text = [ [ "%.2f" % num for num in summary[0] ],
             [ "%.2f" % num for num in summary[1] ],
             [ "%.2f" % num for num in summary[2] ],
             [ "%.2f" % num for num in summary[3] ]
           ]

    ax.axis('off')
    # Draw the table
    table = ax.table(cellText=text,
                     colWidths=[0.33, 0.33],
                     colLabels=col_names,
                     rowLabels=['Precip ($mm$)', 'Streamflow ($mm$)', 'ET ($mm$)', 'Runoff ratio'],
                     loc='center right')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    ax.text(0, 0.75, "Mass balance: %s - %s" % \
                 (startDate.strftime('%Y/%m/%d'), endDate.strftime('%Y/%m/%d') ),
            horizontalalignment='left',
            #verticalalignment='center',
            fontsize=10)
    

def plotGraph(args, plottype, obs, data, columns, min_x, max_x, ax, secondary=None,
              plotColor=True):
    
    if plotColor:
        obs_color = 'black'
        mod_color = 'green'
        second_color = 'blue'
    else:
        obs_color = 'black'
        mod_color = 'grey'
        second_color = 'black'
    
    if plottype == PLOT_TYPE_STD or \
       plottype == PLOT_TYPE_LOGY:
        x = obs.index
    elif plottype == PLOT_TYPE_CDF:
        x = np.linspace(min_x, max_x, num=1000 )
    
    # Plot observed values
    # Standard or log plot
    obs_y = obs
    if plottype == PLOT_TYPE_CDF:
        obs_ecdf = sm.distributions.ECDF(obs['observed'])
        obs_y = obs_ecdf(x)
    obs_plt = None
    if not args.supressObs:
        (obs_plt,) = ax.plot(x, obs_y, obs_color, linewidth=2)
        
    # Plot modeled values
    data_plt = []
    for c in columns:
        # Standard or log plot
        mod_y = data[c]
        if plottype == PLOT_TYPE_CDF:
            mod_ecdf = sm.distributions.ECDF(data[c])
            mod_y = mod_ecdf(x)
        (mod_plt,) = ax.plot(x, mod_y, color=mod_color, linewidth=1)
        data_plt.append(mod_plt)
    
    # X-axis
    if plottype == PLOT_TYPE_STD or \
       plottype == PLOT_TYPE_LOGY:
        num_years = len(x) / 365
        if num_years > 2:
            if num_years > 5:
                ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
            else:
                ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
        else:
            ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b-%Y'))
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
            ax.set_xlabel( 'Streamflow ($mm\ day^{-1}$)' )
    elif args.xlabel:
        ax.set_xlabel(args.xlabel)
    
    # Y-axis
    if plottype == PLOT_TYPE_LOGY:
        ax.set_yscale('log')
    
    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    elif plottype != PLOT_TYPE_CDF and plottype != PLOT_TYPE_LOGY:
        y_label = 'Streamflow ($mm\ day^{-1}$)'
        ax.set_ylabel( y_label )
    
    data_plt.insert(0, obs_plt)
    
    # Plot secondary data (if specified)
    if secondary and \
        (plottype == PLOT_TYPE_STD or plottype == PLOT_TYPE_LOGY):
        # Plot
        ax2 = ax.twinx()
        if args.secondaryPlotType == 'line':
            (sec_plot,) = ax2.plot(x, data[secondary])
        elif args.secondaryPlotType == 'bar':
            sec_plot = ax2.bar(x, data[secondary], facecolor=second_color, edgecolor='none', width=2.0)
        ax2.invert_yaxis()
        ax2.set_ylabel('Precipication ($mm\ day^{-1}$)')
    
    return data_plt

if __name__ == "__main__":
    # Handle command line options
    parser = argparse.ArgumentParser(description='Plot CDF of N datasets vs. observed data')
    parser.add_argument('-n', '--outname', required=True, 
                        help='Base name of file to output figure to.  Only specify base name of file, not extension (PDF and PNG files will be produced)')
    parser.add_argument('-o', '--obs', required=True,
                        help='File containing observed data')
    parser.add_argument('-d', '--data', required=True, #nargs='+',
                        help='One or more data files')
    parser.add_argument('-t', '--title', required=False,
                        help='Title of figure')
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
    parser.add_argument("--color", action="store_true", required=False, default=False,
                        help="Plot in color")
    parser.add_argument('--secondaryPlotType', required=False, choices=['bar', 'line'], default='bar',
                        help='Type of plot to use for secondary data.')
    parser.add_argument('--secondaryLabel', required=False,
                        help='Label to use for seconary Y-axis')
    args = parser.parse_args()

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
    mod_df = RHESSysOutput.readColumnsFromFile(mod_file, cols,
                                               readHour=False)
    
    # Align timeseries
    (mod_align, obs_align) = mod_df.align(obs, axis=0, join='inner')
    tmp_max_x = max(mod_align['streamflow'].max(), obs_align['observed'].max())
    if tmp_max_x > max_x:
        max_x = tmp_max_x
    min_x = max(min_x, mod_align['streamflow'].min())

    mod_file.close()

    fig = plt.figure(figsize=(args.figureX, args.figureY), dpi=80, tight_layout=True)
    ax_std = fig.add_subplot(221)
    ax_log = fig.add_subplot(222)
    ax_cdf = fig.add_subplot(223)
    ax_tab = fig.add_subplot(224)

    data_plt = plotGraph(args, PLOT_TYPE_STD, obs_align, mod_align, ['streamflow'], 
                         min_x, max_x, ax_std, secondary='precip', plotColor=args.color)
    fig.text(0.0, 1.0, '(a)')
    plotGraph(args, PLOT_TYPE_LOGY, obs_align, mod_align, ['streamflow'], 
              min_x, max_x, ax_log, plotColor=args.color)
    fig.text(1.0, 1.0, '(b)')
    plotGraph(args, PLOT_TYPE_CDF, obs_align, mod_align, ['streamflow'], 
              min_x, max_x, ax_cdf, plotColor=args.color)
    fig.text(0.0, 0.5, '(c)')
    
    col_names = ['Observed', 'Modeled']
    plotTable(args, col_names, obs_align, mod_align, ax_tab)
    fig.text(1.0, 0.5, '(d)')

    # Figure annotations
    if args.title:
        fig.suptitle(args.title, y=1.01)

    legend_items = ['Observed', 'Modeled']
    fig.legend( data_plt, legend_items, 'lower right', fontsize=10, ncol=2 )

    # Output plot
    if args.color:
        outname = "%s_color" % (args.outname,)
    else:
        outname=args.outname
    plot_filename_png = "%s.png" % (outname,)
    plot_filename_pdf = "%s.pdf" % (outname,)
    plt.savefig(plot_filename_png, bbox_inches='tight') #, bbox_extra_artists=[table])
    plt.savefig(plot_filename_pdf, bbox_inches='tight') #, bbox_extra_artists=[table])
