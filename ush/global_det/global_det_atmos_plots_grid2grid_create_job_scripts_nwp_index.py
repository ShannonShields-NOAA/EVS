#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_grid2grid_create_job_scripts_nwp_index.py
Contact(s): Shannon Shields (shannon.shields@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/plots/global_det/exevs_plots_global_det_atmos_grid2grid_nwp_index.sh
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np
import subprocess
import copy
import global_det_atmos_util as gda_util
import global_det_atmos_nwp_index_util as gda_nwputil

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
NDAYS = str(os.environ['NDAYS'])
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'plot_job_scripts', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Set environment variables to not write to individual job scripts
# as per request from NCO; these get set higher up in the job
dont_write_env_var_list = [
    'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA', 'COMROOT',
    'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'SENDCOM',
    'COMOUT', 'evs_run_mode', 'MET_ROOT', 'met_ver', 'NDAYS'
]

################################################
#### Base/Common Plotting Information
################################################
base_plot_jobs_info_dict = {
    'nwp_index': {
        'NWPIndex': {'vx_masks': ['TROPICS,NHEM,SHEM'],
                     'fcst_var_dict': {'name': 'NWP_INDEX',
                                       'levels': ['NA']},
                     'obs_var_dict': {'name': 'NWP_INDEX',
                                      'levels': ['NA']}},
    }
}

################################################
#### condense_stats jobs
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### nwp_index
for nwp_index_job in list(condense_stats_jobs_dict['nwp_index'].keys()):
    condense_stats_jobs_dict['nwp_index'][nwp_index_job]['line_types'] = ['SSIDX']
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### nwp_index
for nwp_index_job in list(filter_stats_jobs_dict['nwp_index'].keys()):
    filter_stats_jobs_dict['nwp_index'][nwp_index_job]['grid'] = 'G004'
    filter_stats_jobs_dict['nwp_index'][nwp_index_job]['fcst_var_dict']['threshs'] = [
        'NA'
    ]
    filter_stats_jobs_dict['nwp_index'][nwp_index_job]['obs_var_dict']['threshs'] = [
        'NA'
    ]
    filter_stats_jobs_dict['nwp_index'][nwp_index_job]['interps'] = ['NEAREST/1']
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### nwp_index
for nwp_index_job in list(make_plots_jobs_dict['nwp_index'].keys()):
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['grid'] = 'G004'
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['fcst_var_dict']['threshs'] = [
        'NA'
    ]
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['obs_var_dict']['threshs'] = [
        'NA'
    ]
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['interps'] = ['NEAREST/1']
    del make_plots_jobs_dict['nwp_index'][nwp_index_job]['line_types']
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['line_type_stats'] = [
        'SSIDX/SS_INDEX'
    ]
    make_plots_jobs_dict['nwp_index'][nwp_index_job]['plots'] = ['time_series']
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
if SENDCOM == 'YES':
    search_dir = os.path.join(COMOUT, f"{VERIF_CASE}_VERIF_TYPE",
                              f"last{NDAYS}days")
else:
    search_dir = os.path.join(DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                              f"{RUN}.{end_date}", f"{VERIF_CASE}_VERIF_TYPE",
                              f"last{NDAYS}days")
tar_images_jobs_dict = {
    'nwp_index': {'search_base_dir': search_dir},
}
if JOB_GROUP == 'tar_images':
    JOB_GROUP_dict = tar_images_jobs_dict

model_list = os.environ['model_list'].split(' ')
for verif_type in VERIF_CASE_STEP_type_list:
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
          +verif_type+" for job group "+JOB_GROUP)
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    model_plot_name_list = (
        os.environ[VERIF_CASE_STEP_abbrev+'_model_plot_name_list'].split(' ')
    )
    verif_type_plot_jobs_dict = JOB_GROUP_dict[verif_type]
    for verif_type_job in list(verif_type_plot_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_nwputil.initialize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['NDAYS'] = NDAYS
        job_env_dict['date_type'] = 'VALID'
        if JOB_GROUP in ['filter_stats', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_start'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
            if 'Daily' in verif_type_job:
                daily_fhr_list = []
                for fhr in job_env_dict['fhr_list'].split(', '):
                    if int(fhr) >= 24 and int(fhr) % 24 == 0:
                        daily_fhr_list.append(str(fhr))
                    job_env_dict['fhr_list'] = ', '.join(daily_fhr_list)
        if JOB_GROUP in ['condense_stats', 'filter_stats', 'make_plots']:
            if verif_type == 'nwp_index':
                obs_list = (
                    os.environ[VERIF_CASE_STEP_abbrev_type+'_truth_name_list']\
                    .split(' ')
                )
            elif verif_type == 'means':
                obs_list = model_list
            else:
                obs_list = [
                    verif_type_plot_jobs_dict[verif_type_job]['obs_name']
                    for m in model_list
                ]
            for data_name in ['fcst', 'obs']:
                job_env_dict[data_name+'_var_name'] =  (
                    verif_type_plot_jobs_dict[verif_type_job]\
                    [data_name+'_var_dict']['name']
                )
        if JOB_GROUP == 'condense_stats':
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_types'],
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['levels'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                model_list
            ))
        elif JOB_GROUP == 'filter_stats':
            job_env_dict['grid'] = (
                verif_type_plot_jobs_dict[verif_type_job]['grid']
            )
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_types'],
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['levels'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                model_list,
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['threshs'],
                verif_type_plot_jobs_dict[verif_type_job]['interps'],
                valid_hrs
            ))
        elif JOB_GROUP == 'make_plots':
            job_env_dict['grid'] = (
                verif_type_plot_jobs_dict[verif_type_job]['grid']
            )
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_type_stats'],
                verif_type_plot_jobs_dict[verif_type_job]['plots'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                verif_type_plot_jobs_dict[verif_type_job]['interps']
            ))
        elif JOB_GROUP == 'tar_images':
            JOB_GROUP_verif_type_job_product_loops = []
            for root, dirs, files in os.walk(
                verif_type_plot_jobs_dict['search_base_dir'].replace(
                    'VERIF_TYPE', verif_type
                )
            ):
                if not dirs \
                        and root not in JOB_GROUP_verif_type_job_product_loops:
                    JOB_GROUP_verif_type_job_product_loops.append(root)
        for loop_info in JOB_GROUP_verif_type_job_product_loops:
            if JOB_GROUP in ['condense_stats', 'filter_stats']:
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    verif_type_plot_jobs_dict[verif_type_job]\
                    ['obs_var_dict']['levels'][
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['model_list'] = loop_info[3]
                job_env_dict['model_plot_name_list'] = (
                    model_plot_name_list[model_list.index(loop_info[3])]
                )
                job_env_dict['obs_list'] = (
                    obs_list[model_list.index(loop_info[3])]
                )
                job_env_dict['line_type'] = loop_info[0]
                job_env_dict['vx_mask'] = loop_info[2]
                if JOB_GROUP == 'filter_stats':
                    job_env_dict['event_equalization'] = (
                        os.environ[VERIF_CASE_STEP_abbrev
                                   +'_event_equalization']
                    )
                    job_env_dict['fcst_var_thresh'] = loop_info[4]
                    job_env_dict['obs_var_thresh'] = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['obs_var_dict']['threshs'][
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['threshs'].index(loop_info[4])
                        ]
                    )
                    job_env_dict['interp_method'] = loop_info[5].split('/')[0]
                    job_env_dict['interp_points'] = loop_info[5].split('/')[1]
                    job_env_dict['valid_hr_start'] = (
                        str(loop_info[6]).zfill(2)
                    )
                    job_env_dict['valid_hr_end'] = (
                        job_env_dict['valid_hr_start']
                    )
                    job_env_dict['valid_hr_inc'] = '24'
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                    gda_nwputil.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                                  job_env_dict)
                )
                job_env_dict['job_work_dir'] = job_work_dir
                job_env_dict['job_DATA_dir'] = job_DATA_dir
                job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                if SENDCOM == 'YES':
                    gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                else:
                    gda_util.make_dir(job_env_dict['job_DATA_dir'])
                # Check plot files
                plot_files_exist = gda_util.check_plot_files(job_env_dict)
                if plot_files_exist:
                    write_job_cmds = False
                else:
                    write_job_cmds = True
                # Create job file
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Write environment variables
                for name, value in job_env_dict.items():
                    if name not in dont_write_env_var_list:
                        job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                if write_job_cmds:
                    gda_util.make_dir(job_env_dict['job_work_dir'])
                    job.write(
                        gda_util.python_command('global_det_nwp_index_plots.py',[])
                        +'\n'
                    )
                    job.write('export err=$?; err_chk'+'\n')
                job.close()
            elif JOB_GROUP == 'make_plots':
                job_env_dict['event_equalization'] = os.environ[
                    VERIF_CASE_STEP_abbrev+'_event_equalization'
                ]
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['model_plot_name_list'] = (
                    ', '.join(model_plot_name_list)
                )
                job_env_dict['obs_list'] = ', '.join(obs_list)
                job_env_dict['line_type'] = loop_info[0].split('/')[0]
                job_env_dict['stat'] = loop_info[0].split('/')[1]
                job_env_dict['plot'] = loop_info[1]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['interp_method'] = loop_info[3].split('/')[0]
                job_env_dict['interp_points'] = loop_info[3].split('/')[1]
                if job_env_dict['plot'] == 'valid_hour_average':
                    plot_valid_hrs_loop = [valid_hrs]
                else:
                    plot_valid_hrs_loop = valid_hrs
                if job_env_dict['plot'] in ['threshold_average',
                                            'performance_diagram']:
                    plot_fcst_threshs_loop = [
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['threshs']
                    ]
                else:
                    plot_fcst_threshs_loop = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['threshs']
                    )
                if job_env_dict['plot'] in ['stat_by_level', 'lead_by_level']:
                    if verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['name'] == 'O3MR':
                        plot_fcst_levels_loop = ['all', 'strat']
                    else:
                        plot_fcst_levels_loop = ['all', 'trop', 'strat',
                                                 'ltrop', 'utrop']
                else:
                    plot_fcst_levels_loop = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['levels']
                    )
                for plot_loop_info in list(
                    itertools.product(plot_valid_hrs_loop,
                                      plot_fcst_threshs_loop,
                                      plot_fcst_levels_loop)
                ):
                    if job_env_dict['plot'] == 'valid_hour_average':
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0][0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0][-1]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                    else:
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = '24'
                    if job_env_dict['plot'] in ['threshold_average',
                                                'performance_diagram']:
                        job_env_dict['fcst_var_thresh_list'] = ', '.join(
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['threshs']
                        )
                    else:
                        job_env_dict['fcst_var_thresh_list'] = (
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = (
                            plot_loop_info[1]
                        )
                    if job_env_dict['plot'] in ['stat_by_level',
                                                'lead_by_level']:
                        job_env_dict['vert_profile'] = plot_loop_info[2]
                        job_env_dict['fcst_var_level_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['levels']
                        )
                        job_env_dict['obs_var_level_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']
                        )
                    else:
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                             ['fcst_var_dict']['levels']\
                             .index(plot_loop_info[2])]
                        )
                    run_global_det_atmos_plots = ['plots']
                    if evs_run_mode == 'production' and \
                            verif_type in ['pres_levs', 'sfc'] and \
                            job_env_dict['plot'] in \
                            ['lead_average', 'lead_by_level', 'lead_by_date']:
                        run_global_det_atmos_plots.append('plots_tof240')
                    for run_global_det_atmos_plot in run_global_det_atmos_plots:
                        # Set up output directories
                        njobs+=1
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                            gda_nwputil.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                                          job_env_dict)
                        )
                        job_env_dict['job_work_dir'] = job_work_dir
                        job_env_dict['job_DATA_dir'] = job_DATA_dir
                        job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                        if SENDCOM == 'YES':
                            gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                        else:
                            gda_util.make_dir(job_env_dict['job_DATA_dir'])
                        # Check plot files
                        plot_files_exist = gda_util.check_plot_files(
                            job_env_dict
                        )
                        if plot_files_exist:
                             write_job_cmds = False
                        else:
                             write_job_cmds = True
                        # Create job file
                        job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                'job'+str(njobs))
                        print("Creating job script: "+job_file)
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        # Set any environment variables for special cases
                        # Write environment variables
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        for name, value in job_env_dict.items():
                            if name not in dont_write_env_var_list:
                                job.write('export '+name+'="'+value+'"\n')
                        job.write('\n')
                        if run_global_det_atmos_plot == 'plots_tof240':
                            fhrs_tof240 = []
                            for fhr in job_env_dict['fhr_list'].split(', '):
                                if int(fhr) <= 240:
                                    fhrs_tof240.append(str(fhr))
                            job.write(
                                'export fhr_list="'
                                +', '.join(fhrs_tof240)+'"\n'
                            )
                        if write_job_cmds:
                            gda_util.make_dir(job_env_dict['job_work_dir'])
                            job.write(
                                gda_util.python_command('global_det_nwp_index_plots.py',
                                                        [])+'\n'
                            )
                            job.write('export err=$?; err_chk'+'\n')
                        job.close()
            elif JOB_GROUP == 'tar_images':
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                if SENDCOM == 'YES':
                   job_env_dict['job_COMOUT_dir'] = loop_info
                   job_env_dict['job_DATA_dir'] = loop_info.replace(
                       COMOUT,
                       os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                    'plot_output', f"{RUN}.{end_date}")
                   )
                else:
                   job_env_dict['job_DATA_dir'] = loop_info
                   job_env_dict['job_COMOUT_dir'] = loop_info.replace(
                       os.path.join(DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                                    f"{RUN}.{end_date}"),
                       COMOUT
                   )
                job_env_dict['job_work_dir'] = (
                    job_env_dict['job_DATA_dir'].replace(
                        f"{RUN}.{end_date}",
                        f"job_work_dir/{job_env_dict['JOB_GROUP']}/"
                        +f"{job_env_dict['job_id']}/{RUN}.{end_date}"
                    )
                )
                if SENDCOM == 'YES':
                    gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                else:
                    gda_util.make_dir(job_env_dict['job_DATA_dir'])
                # Check plot files
                plot_files_exist = gda_util.check_plot_files(job_env_dict)
                if plot_files_exist:
                    write_job_cmds = False
                else:
                    write_job_cmds = True
                # Create job files
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Write environment variables
                for name, value in job_env_dict.items():
                    if name not in dont_write_env_var_list:
                        job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                if write_job_cmds:
                    gda_util.make_dir(job_env_dict['job_work_dir'])
                    job.write(
                        gda_util.python_command('global_det_nwp_index_plots.py',
                                                [])
                        +'\n'
                    )
                    job.write('export err=$?; err_chk'+'\n')
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "+JOB_GROUP_jobs_dir)
    poe_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(JOB_GROUP_jobs_dir,job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    if machine == 'WCOSS2':
        nselect = subprocess.run(
            f"cat {PBS_NODEFILE} | wc -l",
            shell=True, capture_output=True, encoding="utf8"
        ).stdout.replace('\n', '')
        nnp = int(nselect) * int(nproc)
    else:
        nnp = nproc
    iproc+=1
    while iproc <= int(nnp):
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                f"{str(iproc-1)} /bin/echo {str(iproc)}'\n'"
            )
        else:
            poe_file.write(
                f"/bin/echo {str(iproc)}\n"
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
