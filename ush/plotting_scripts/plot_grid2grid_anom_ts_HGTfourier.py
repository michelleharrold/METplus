#!/usr/bin/env python
'''
Program Name: plot_grid2grid_anom_ts_HGTfourier.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make time series plots
History Log:  Second version
Usage: 
Parameters: None
Input Files: ASCII files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''
############################################################################
##### Import python modules
from __future__ import (print_function, division)
import os
import numpy as np
import datetime as datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.gridspec as gridspec
import plot_defs as pd
import warnings
import logging
import pandas as pandas
#############################################################################
##### Settings
np.set_printoptions(suppress=True)
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
warnings.filterwarnings('ignore')
colors = ['black', 'darkgreen', 'darkred', 'indigo', 'blue', 'crimson', 'goldenrod', 'sandybrown', 'thistle']
##############################################################################
##### Read in data and set variables
#forecast dates
month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
sdate = os.environ['START_T']
syear = int(sdate[:4])
smon = int(sdate[4:6])
smonth = month_name[smon-1]
sday = int(sdate[6:8])
edate = os.environ['END_T']
eyear = int(edate[:4])
emon = int(edate[4:6])
emonth = month_name[emon-1]
eday = int(edate[6:8])
cycle_int = int(os.environ['CYCLE'])
lead_int = int(os.environ['LEAD'])
sd = datetime.datetime(syear, smon, sday, cycle_int)
ed = datetime.datetime(eyear, emon, eday, cycle_int)+datetime.timedelta(days=1)
tdelta = datetime.timedelta(days=1)
dates = md.drange(sd, ed, tdelta)
total_days = len(dates)
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
stat_files_input_dir_base = os.environ['STAT_FILES_INPUT_DIR']
stat_files_input_dir = os.path.join(stat_files_input_dir_base, "anom")
model_names = os.environ['MODEL_NAMES'].replace(" ", ",").split(",")
nmodels = len(model_names)
cycle = os.environ['CYCLE']
lead = os.environ['LEAD']
region = os.environ['REGION']
grid = "G2"
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_level = os.environ['FCST_VAR_LEVEL']
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_level = os.environ['OBS_VAR_LEVEL']
wave_num_beg_list = os.environ['WAVE_NUM_BEG_LIST'].replace(", ", ",").split(",")
wave_num_end_list = os.environ['WAVE_NUM_END_LIST'].replace(", ", ",").split(",")
nwave_num = len(wave_num_beg_list)
event_equalization = True
ci_method = "EMC"
#ouput info
logging_filename = os.environ['LOGGING_FILENAME']
logger = logging.getLogger(logging_filename)
logging_level = os.environ['LOGGING_LEVEL']
logger.setLevel(logging_level)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) ""%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(logging_filename, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
plotting_out_dir_base = os.environ['PLOTTING_OUT_DIR']
plotting_out_dir = os.path.join(plotting_out_dir_base, "anom")
####################################################################
logger.info(" ")
logger.info("Running "+os.path.realpath(__file__))
logger.info("with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z lead:"+lead+" region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
#############################################################################
##### Create image directory if does not exist
if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
    os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
##### Read data in data, compute statistics, and plot
#read in data
logger.info("Gathering data")
create_data_arrays = True
m=1
while m <= nmodels: #loop over models
    model_now = model_names[m-1]
    wn = 1
    while wn <= nwave_num:
        wb = wave_num_beg_list[wn-1]
        we = wave_num_end_list[wn-1]
        wave_num_pairing = "WV1_"+wb+"-"+we 
        model_now_stat_file = stat_files_input_dir+"/"+cycle+"Z/"+model_now+"/"+region+"/"+model_now+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+wave_num_pairing+".stat"
        if os.path.exists(model_now_stat_file):
            nrow = sum(1 for line in open(model_now_stat_file))
            if nrow == 0: #file blank if stat analysis filters were not all met
                logger.warning("Model "+str(m)+" "+model_now+": "+model_now_stat_file+" empty")
            else:
                logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_stat_file)
                met_cols = [ "VERSION", "MODEL", "DESC", "FCST_LEAD", "FCST_VALID_BEG", "FCST_VALID_END", "OBS_LEAD", "OBS_VALID_BEG", "OBS_VALID_END", "FCST_VAR", "FCST_LEV", "OBS_VAR", "OBS_LEV", "OBTYPE", "VX_MASK", "INTERP_MTHD", "INTERP_PNTS", "FCST_THRESH", "OBS_THRESH", "COV_THRESH", "ALPHA", "LINE_TYPE", "TOTAL", "A", "B", "C", "D", "E", "F", "G" ]
                model_now_data = pandas.read_csv(model_now_stat_file, sep=" ", skiprows=1, skipinitialspace=True, header=None, names=met_cols)
                #format dates in stat file
                model_now_dates = model_now_data.loc[:]['FCST_VALID_BEG']
                dateformat = "%Y%m%d_%H%M%S"
                model_now_dates_formatted = np.zeros_like(model_now_dates)
                for d in range(len(model_now_dates)):
                    if date_filter_method == 'Valid':
                        date_now = datetime.datetime.strptime(model_now_dates[d], dateformat)
                    elif date_filter_method == 'Initialization':
                        date_now = datetime.datetime.strptime(model_now_dates[d], dateformat) - datetime.timedelta(hours=lead_int)
                    model_now_dates_formatted[d] = md.date2num(date_now)
                #parse between sl1l2 and vl1l2 data
                data_line_type = model_now_data.loc[0]['LINE_TYPE']
                if data_line_type == 'SAL1L2':
                    #if create partial sum data arrays for all models and all dates, if not created yet
                    if create_data_arrays:
                        fabar_models_dates = np.full([nmodels,total_days, nwave_num], np.nan)
                        oabar_models_dates = np.full([nmodels,total_days, nwave_num], np.nan)
                        foabar_models_dates = np.full([nmodels,total_days, nwave_num], np.nan)
                        ffabar_models_dates = np.full([nmodels,total_days, nwave_num], np.nan)
                        ooabar_models_dates = np.full([nmodels,total_days, nwave_num], np.nan)
                        create_data_arrays = False
                    #read data for current model
                    #check for any missing data in current model from requested date span,
                    #arrange data in chronological order, and put in array
                    for d in range(total_days):
                        dd = np.where(model_now_dates_formatted == dates[d])[0]
                        if len(dd) == 1:
                            fabar_models_dates[m-1, d, wn-1] = model_now_data.loc[dd[0]]['A']
                            oabar_models_dates[m-1, d, wn-1] = model_now_data.loc[dd[0]]['B']
                            foabar_models_dates[m-1, d, wn-1] = model_now_data.loc[dd[0]]['C']
                            ffabar_models_dates[m-1, d, wn-1] = model_now_data.loc[dd[0]]['D']
                            ooabar_models_dates[m-1, d, wn-1] = model_now_data.loc[dd[0]]['E']
        else:
            logger.warning("Model "+str(m)+" "+model_now+": "+model_now_stat_file+" missing")    
        wn+=1
    m+=1
#compute statistics
logger.info("Calculating and plotting statistics")
s=1
while s <= nstats: #loop over statistics
    stat_now = plot_stats_list[s-1]
    stat_formal_name_now = pd.get_stat_formal_name(stat_now)
    logger.debug(stat_now)
    if data_line_type == 'SAL1L2':
        if stat_now == 'acc':
            stat_now_vals = np.ma.masked_invalid((foabar_models_dates - (fabar_models_dates*oabar_models_dates))/np.sqrt((ffabar_models_dates - (fabar_models_dates)**2)*(ooabar_models_dates - (oabar_models_dates)**2)))
        else:
            logger.error(stat_now+" cannot be computed")
            exit(1)    
    #do event equalization, if requested
    if event_equalization:
        logger.debug("Doing event equalization")
        wn = 1
        while wn <= nwave_num:
            stat_now_vals[:,:,wn-1] = np.ma.mask_cols(stat_now_vals[:,:,wn-1])
            wn+=1
    #set up plot
    if nwave_num == 1:
        fig = plt.figure(figsize=(10,6))
        gs = gridspec.GridSpec(1,1)
    elif nwave_num == 2:
        fig = plt.figure(figsize=(12,14))
        gs = gridspec.GridSpec(2,1)
        gs.update(hspace=0.4)
    elif nwave_num == 3:
        fig = plt.figure(figsize=(12,18))
        gs = gridspec.GridSpec(3,1)
        gs.update(hspace=0.4)
    elif nwave_num == 4:
        fig = plt.figure(figsize=(12,20))
        gs = gridspec.GridSpec(4,1)
        gs.update(hspace=0.4)
    else:
        logger.error("Too many wave number pairs selected, max. is 4")
        exit(1)
    #plot
    wn = 1
    while wn <= nwave_num:
        wb = wave_num_beg_list[wn-1]
        we = wave_num_end_list[wn-1]
        wave_num_pairing = "WV1_"+wb+"-"+we
        logger.debug(wave_num_pairing)
        ax = plt.subplot(gs[(wn-1)])
        m=1
        while m <= nmodels: #loop over models
            model_now = model_names[m-1]
            logger.debug(str(m)+" "+model_now)
            model_now_stat_now_vals = stat_now_vals[m-1,:,wn-1]
            #write forecast hour mean to file
            if not os.path.exists(os.path.join(plotting_out_dir, "data", cycle+"Z", model_now)):
                os.makedirs(os.path.join(plotting_out_dir, "data", cycle+"Z", model_now))
            save_mean_filename = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+wave_num_pairing+".txt"
            if os.path.exists(save_mean_filename):
                append_write = 'a' # append if already exists
            else:
                append_write = 'w' # make a new file if not
            with open(save_mean_filename, append_write) as save_mean_file:
                save_mean_file.write(lead+' '+str(model_now_stat_now_vals.mean())+ '\n')
            #calculate 95% confidence intervals for difference between model m>1 and model 1
            if ci_method == "NONE":
                logger.debug("Not calculating confidence intervals")
            else:
                if m == 1:
                    model1_stat_now_vals = model_now_stat_now_vals
                else:
                    if ci_method == "EMC":
                        logger.debug("Calculating confidence intervals using EMC method")
                        model_now_model1_intvl = pd.cintvl_emc(model1_stat_now_vals, model_now_stat_now_vals, total_days)
                    elif ci_method == "NCAR":
                        logger.warning("NCAR method not set up yet, setting as NaN")
                        model_now_model1_intvl = np.nan
                    else:
                        logger.warning("Method for calculating confidence intervals not supported, setting as NaN")
                        model_now_model1_intvl = np.nan
                    #write confidence interval to file
                    save_ci_filename = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_CI_"+region+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+wave_num_pairing+".txt"
                    if os.path.exists(save_ci_filename):
                        append_write = 'a' # append if already exists
                    else:
                        append_write = 'w' # make a new file if not
                    with open(save_ci_filename, append_write) as save_ci_file:
                        save_ci_file.write(lead+' '+str(model_now_model1_intvl)+ '\n')
            #plot individual statistic time series
            logger.debug("Plotting "+stat_now+" time series for "+model_now)
            if m == 1:
                #set up plot
                ax.grid(True)
                ax.tick_params(axis='x', pad=10)
                ax.set_xlabel(date_filter_method+" Date")
                ax.set_xlim([dates[0],dates[-1]])
                if len(dates) <= 31:
                    ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                    ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
                    ax.xaxis.set_minor_locator(md.DayLocator())
                else:
                    ax.xaxis.set_major_locator(md.MonthLocator())
                    ax.xaxis.set_major_formatter(md.DateFormatter('%b%Y'))
                    ax.xaxis.set_minor_locator(md.DayLocator())
                ax.tick_params(axis='y', pad=15)
                ax.set_ylabel(stat_formal_name_now)
                #ax.set_ylim()
                ax.set_title(wave_num_pairing+"\n", loc='right')
            masked_count = np.ma.count_masked(model_now_stat_now_vals)
            vals_count = len(model_now_stat_now_vals) - masked_count
            ax.plot_date(dates,model_now_stat_now_vals, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_now+' '+str(round(model_now_stat_now_vals.mean(),2))+' '+str(vals_count))
            m+=1
            ax.legend(bbox_to_anchor=(1.025, 1.0, 0.375, 0.0), loc='upper right', ncol=1, fontsize='13', mode="expand", borderaxespad=0.)
        wn+=1
    fig.suptitle("Fcst: "+fcst_var_name+"_"+fcst_var_level+" Obs: "+obs_var_name+"_"+obs_var_level+" Fourier Decomposition "+str(stat_formal_name_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" forecast hour "+lead+"\n", fontsize=14, fontweight='bold')
    logger.info("Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhr"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_fourierdecomp_"+grid+region+".png")
    plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhr"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_fourierdecomp_"+grid+region+".png", bbox_inches='tight')
    s+=1