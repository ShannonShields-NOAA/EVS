#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_job_scripts_nwp_index.py
Contact(s): Shannon Shields (shannon.shields@noaa.gov)
Abstract: This creates one main job script. This
          job script contains all the necessary environment variables
          and commands needed to run it.
Run By: scripts/stats/global_det/exevs_global_det_atmos_grid2grid_stats_nwp_inde        x.sh
'''

import sys
import os
import glob
import datetime
import numpy as np
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'METplus_job_scripts', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Set environment variables to not write to individual job scripts
# as per request from NCO; these get set higher up in the job
dont_write_env_var_list = [
    'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA', 'COMROOT',
    'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'SENDCOM',
    'COMOUT', 'evs_run_mode', 'MET_ROOT', 'METPLUS_PATH'
]

################################################
#### calc_nwp_index jobs
################################################
calc_nwp_index_jobs_dict = {'env': {},
                            'commands': [gda_util.metplus_command(
                                             'StatAnalysis_NWP_Index.conf'
                                         )]}

# Create job scripts
if JOB_GROUP in ['generate_stats', 'calc_nwp_index']:
    if JOB_GROUP == 'calc_nwp_index':
        JOB_GROUP_jobs_dict = calc_nwp_index_jobs_dict
    elif JOB_GROUP == 'generate_stats':
        JOB_GROUP_jobs_dict = generate_stats_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print(f"----> Making job scripts for {VERIF_CASE_STEP} {verif_type} "
              +f"for job group {JOB_GROUP}")
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        # Read in environment variables for verif_type
        if JOB_GROUP == 'assemble_data' and verif_type in ['precip_accum24hr',
                                                           'precip_accum3hr']:
            precip_file_accum_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_'+verif_type+'_file_accum_list'] \
                .split(' '))
            precip_var_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_'+verif_type+'_var_list'] \
                .split(' '))
        for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type].keys()):
            # Initialize job environment dictionary
            job_env_dict = gda_util.initalize_job_env_dict(
                verif_type, JOB_GROUP, VERIF_CASE_STEP_abbrev_type,
                verif_type_job
            )
            # Add job specific environment variables
            full_job_levels_dict = {}
            for verif_type_job_env_var in \
                    list(JOB_GROUP_jobs_dict[verif_type]\
                         [verif_type_job]['env'].keys()):
                job_env_dict[verif_type_job_env_var] = (
                    JOB_GROUP_jobs_dict[verif_type]\
                    [verif_type_job]['env'][verif_type_job_env_var]
                )
                if verif_type_job_env_var in ['var1_levels',
                                              'var2_levels']:
                    full_job_levels_dict[verif_type_job_env_var] = (
                        job_env_dict[verif_type_job_env_var]
                    )
            full_job_fhr_list = job_env_dict['fhr_list']
            verif_type_job_commands_list = (
                JOB_GROUP_jobs_dict[verif_type]\
                [verif_type_job]['commands']
            )
            # Loop through and write job script for dates and models
            if JOB_GROUP == 'reformat_data':
                if verif_type in ['sst', 'sea_ice']:
                    job_env_dict['valid_hr_start'] = '00'
                    job_env_dict['valid_hr_end'] = '12'
                    job_env_dict['valid_hr_inc'] = '12'
                if verif_type == 'pres_levs' \
                        and verif_type_job == 'GeoHeightAnom':
                    if int(job_env_dict['valid_hr_start']) - 12 > 0:
                        job_env_dict['valid_hr_start'] = str(
                            int(job_env_dict['valid_hr_start']) - 12
                        )
                        job_env_dict['valid_hr_inc'] = '12'
            valid_start_date_dt = datetime.datetime.strptime(
                start_date+job_env_dict['valid_hr_start'],
                '%Y%m%d%H'
            )
            valid_end_date_dt = datetime.datetime.strptime(
                end_date+job_env_dict['valid_hr_end'],
                '%Y%m%d%H'
            )
            valid_date_inc = int(job_env_dict['valid_hr_inc'])
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                for model_idx in range(len(model_list)):
                    job_env_dict['fhr_list'] = full_job_fhr_list
                    for full_level_key in list(full_job_levels_dict.keys()):
                        job_env_dict[full_level_key] = (
                            full_job_levels_dict[full_level_key]
                        )
                    job_env_dict['MODEL'] = model_list[model_idx]
                    njobs+=1
                    job_env_dict['job_num'] = str(njobs)
                    # Create job file
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                    print(f"Creating job script: {job_file}")
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Create job working directory
                    job_env_dict['job_num_work_dir'] = os.path.join(
                        DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                        'job_work_dir', JOB_GROUP,
                        f"job{job_env_dict['job_num']}"
                    )
                    job_env_dict['MET_TMP_DIR'] = os.path.join(
                        job_env_dict['job_num_work_dir'], 'tmp'
                    )
                    # Set any environment variables for special cases
                    if JOB_GROUP == 'reformat_data':
                        if verif_type == 'pres_levs':
                            job_env_dict['TRUTH'] = os.environ[
                                VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
                            ].split(' ')[model_idx]
                    elif JOB_GROUP == 'assemble_data':
                        if verif_type in ['precip_accum24hr',
                                          'precip_accum3hr']:
                            job_env_dict['MODEL_var'] = (
                                precip_var_list[model_idx]
                            )
                            if precip_file_accum_list[model_idx] \
                                    == 'continuous':
                                job_env_dict['pcp_combine_method'] = 'SUBTRACT'
                                job_env_dict['MODEL_accum'] = '{lead?fmt=%HH}'
                                job_env_dict['MODEL_levels'] = 'A{lead?fmt=%HH}'
                            else:
                                job_env_dict['pcp_combine_method'] = 'SUM'
                                job_env_dict['MODEL_accum'] = (
                                    precip_file_accum_list[model_idx]
                                )
                                job_env_dict['MODEL_levels'] = (
                                    'A'+job_env_dict['MODEL_accum']
                                )
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'DailyAvg_GeoHeightAnom':
                            job_fhr_list = []
                            for fhr in full_job_fhr_list.split(', '):
                                if int(fhr) % 24 == 0 and int(fhr) >= 24:
                                    job_fhr_list.append(fhr)
                                job_env_dict['fhr_list'] = (
                                    ', '.join(job_fhr_list)
                                )
                    elif JOB_GROUP == 'generate_stats':
                        if verif_type == 'pres_levs':
                            job_env_dict['TRUTH'] = os.environ[
                                VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
                            ].split(' ')[model_idx]
                            if verif_type_job == 'DailyAvg_GeoHeightAnom':
                                job_fhr_list = []
                                for fhr in full_job_fhr_list.split(', '):
                                    if int(fhr) % 24 == 0 and int(fhr) >= 24:
                                        job_fhr_list.append(fhr)
                                    job_env_dict['fhr_list'] = ', '.join(
                                        job_fhr_list
                                    )
                    # Do file checks
                    all_truth_file_exist = False
                    model_files_exist = False
                    write_job_cmds = False
                    check_model_files = True
                    if check_model_files:
                        (model_files_exist, valid_date_fhr_list,
                         copy_output_list) = (
                            gda_util.check_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            ', '.join(valid_date_fhr_list)
                        )
                    if JOB_GROUP == 'reformat_data':
                        if verif_type == 'pres_levs' \
                                and verif_type_job in ['GeoHeightAnom',
                                                       'WindShear']:
                            check_truth_files = True
                        else:
                            check_truth_files = False
                    elif JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    elif JOB_GROUP == 'generate_stats':
                        if verif_type == 'pres_levs' \
                                and verif_type_job in [
                                    'DailyAvg_GeoHeightAnom',
                                    'WindShear'
                                ]:
                            check_truth_files = False
                        elif verif_type == 'means':
                            check_truth_files = False
                        else:
                            check_truth_files = True
                    if check_truth_files:
                        all_truth_file_exist = (
                             gda_util.check_truth_files(job_env_dict)
                        )
                        if model_files_exist and all_truth_file_exist:
                            write_job_cmds = True
                        else:
                            write_job_cmds = False
                    else:
                        if model_files_exist:
                            write_job_cmds = True
                        else:
                            write_job_cmds = False
                    # Check job and model being run
                    if JOB_GROUP == 'reformat_data':
                        # UKMET does not have winds at P200 past fhr120
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'WindShear' \
                                and job_env_dict['MODEL'] == 'ukmet' \
                                and job_env_dict['fhr_list'] != "''":
                            ukmet_fhr_list = []
                            ukmet_fhr_rm_list = []
                            for fhr_chk in (job_env_dict['fhr_list']\
                                            .split(', ')):
                                if int(fhr_chk) <= 120:
                                    ukmet_fhr_list.append(fhr_chk)
                                else:
                                    ukmet_fhr_rm_list.append(fhr_chk)
                            job_env_dict['fhr_list'] = (
                                ', '.join(ukmet_fhr_list)
                            )
                    elif JOB_GROUP == 'assemble_data':
                        # JMA does not have the forecast hour frequency
                        # to do daily average Geopotential Height anomalies
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'DailyAvg_GeoHeightAnom' \
                                and job_env_dict['MODEL'] == 'jma':
                            write_job_cmds = False
                    elif JOB_GROUP == 'generate_stats':
                        # Models below do not have Ozone Mixing Ratio
                        if verif_type == 'pres_levs' \
                                and job_env_dict['MODEL'] \
                                in ['cmc', 'cmc_regional', 'dwd', 'ecmwf',
                                    'fnmoc', 'jma', 'metfra', 'ukmet'] \
                                and verif_type_job == 'Ozone':
                            write_job_cmds = False
                        # IMD does not have Ozone Mixing Ratio at 925mb
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'Ozone' \
                                and job_env_dict['MODEL'] == 'imd':
                            imd_ozone_level_list = (
                                job_env_dict['var1_levels'].split(', ')
                            )
                            imd_ozone_level_list.remove('P925')
                            job_env_dict['var1_levels'] = ', '.join(
                                imd_ozone_level_list
                            )
                        # UKMET does not have winds at P200 past fhr120
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'WindShear' \
                                and job_env_dict['MODEL'] == 'ukmet' \
                                and job_env_dict['fhr_list'] != "''":
                            ukmet_fhr_list = []
                            ukmet_fhr_rm_list = []
                            for fhr_chk in (job_env_dict['fhr_list']\
                                            .split(', ')):
                                if int(fhr_chk) <= 120:
                                    ukmet_fhr_list.append(fhr_chk)
                                else:
                                    ukmet_fhr_rm_list.append(fhr_chk)
                            job_env_dict['fhr_list'] = ', '.join(
                                ukmet_fhr_list
                            )
                        # JMA does not have the forecast hour frequency
                        # to do daily average Geopotential Height anomalies
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'DailyAvg_GeoHeightAnom' \
                                and job_env_dict['MODEL'] == 'jma':
                            write_job_cmds = False
                        # UKMET and JMA does not variables at
                        # different levels depending on if past
                        # a certain forecast hour
                        if job_env_dict['VERIF_TYPE'] == 'pres_levs' \
                                and verif_type_job in ['GeoHeight',
                                                       'Temp', 'UWind',
                                                       'VWind', 'VectorWind'] \
                                and job_env_dict['MODEL'] in ['jma',
                                                              'ukmet']:
                            model_fhr_lev_dict = {
                                'run1': {},
                                'run2': {}
                            }
                            if job_env_dict['MODEL'] == 'jma':
                                mod_fhr_thresh = 120
                                mod_rm_lefhr_level_list = []
                                mod_rm_gtfhr_level_list = ['P250']
                            elif job_env_dict['MODEL'] == 'ukmet':
                                mod_fhr_thresh = 120
                                mod_rm_lefhr_level_list = []
                                if verif_type_job == 'GeoHeight':
                                    mod_rm_gtfhr_level_list = [
                                        'P700', 'P250'
                                    ]
                                else:
                                    mod_rm_gtfhr_level_list = [
                                        'P500', 'P250'
                                    ]
                            mod_lefhr_list = []
                            mod_gtfhr_list = []
                            if job_env_dict['fhr_list'] != '':
                                mod_full_fhr_list = (
                                    job_env_dict['fhr_list'].split(', ')
                                )
                                for fhr_chk in mod_full_fhr_list:
                                    if int(fhr_chk) <= mod_fhr_thresh:
                                        mod_lefhr_list.append(fhr_chk)
                                    else:
                                        mod_gtfhr_list.append(fhr_chk)
                            for runN in ['run1', 'run2']:
                                if runN == 'run1':
                                    mod_runN_fhr_list =  mod_lefhr_list
                                    mod_runN_rm_level_list = (
                                        mod_rm_lefhr_level_list
                                    )
                                elif runN == 'run2':
                                    mod_runN_fhr_list =  mod_gtfhr_list
                                    mod_runN_rm_level_list = (
                                        mod_rm_gtfhr_level_list
                                    )
                                model_fhr_lev_dict[runN]['fhr_list'] = (
                                    ', '.join(mod_runN_fhr_list)
                                )
                                level_list = (
                                    job_env_dict[f"var1_levels"].split(', ')
                                )
                                mod_runN_level_list = []
                                for level_chk in level_list:
                                    if level_chk not \
                                            in mod_runN_rm_level_list:
                                        mod_runN_level_list.append(
                                            level_chk
                                        )
                                (model_fhr_lev_dict[runN]\
                                 [f"var1_levels"]) = (
                                     ', '.join(mod_runN_level_list)
                                )
                                if verif_type_job == 'VectorWind':
                                    (model_fhr_lev_dict[runN]\
                                     [f"var2_levels"]) = (
                                         ', '.join(mod_runN_level_list)
                                    )
                            for run1_key \
                                    in list(model_fhr_lev_dict['run1'].keys()):
                                job_env_dict[run1_key] = (
                                    model_fhr_lev_dict['run1'][run1_key]
                                )
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        if name not in dont_write_env_var_list:
                            if '"' in value:
                                job.write(f"export {name}='{value}'\n")
                            else:
                                job.write(f'export {name}="{value}"\n')
                    job.write('\n')
                    # Write job commands
                    if write_job_cmds:
                        gda_util.make_dir(job_env_dict['job_num_work_dir'])
                        for cmd in verif_type_job_commands_list:
                            job.write(cmd+'\n')
                            job.write('export err=$?; err_chk'+'\n')
                        if JOB_GROUP == 'generate_stats':
                            # JMA and UKMET: run again for fhr > 120
                            if verif_type == 'pres_levs' \
                                    and verif_type_job in ['GeoHeight',
                                                           'Temp', 'UWind',
                                                           'VWind', 'VectorWind'] \
                                    and job_env_dict['MODEL'] in ['jma',
                                                                  'ukmet']:
                                rerun_key_list = list(
                                    model_fhr_lev_dict.keys()
                                )[1:]
                                for runN in rerun_key_list:
                                    if (model_fhr_lev_dict[runN]['fhr_list']) \
                                            != '':
                                        export_key_list = list(
                                            model_fhr_lev_dict[runN].keys()
                                        )
                                        for export_key in export_key_list:
                                            job.write('export '
                                                      +export_key+'="'
                                                      +model_fhr_lev_dict[runN]\
                                                       [export_key]+'"\n')
                                        for cmd in verif_type_job_commands_list:
                                            job.write(cmd+'\n')
                                            job.write('export err=$?; err_chk'
                                                      +'\n')
                        for output_file_tuple in copy_output_list:
                            job.write(f'if [ -f "{output_file_tuple[0]}" ]; then '
                                      +f"cp -v {output_file_tuple[0]} "
                                      +f"{output_file_tuple[1]}; fi\n")
                    else:
                        if JOB_GROUP == 'reformat_data':
                            if (verif_type_job == 'GeoHeightAnom' \
                                     and int(job_env_dict['valid_hr_start']) \
                                     % 12 == 0) \
                                    or verif_type_job == 'WindShear':
                                if job_env_dict['fhr_list'] != '':
                                    job.write(verif_type_job_commands_list[1]+'\n')
                                    job.write('export err=$?; err_chk\n')
                    job.close()
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
elif JOB_GROUP == 'gather_stats':
    print(f"----> Making job scripts for {VERIF_CASE_STEP} "
          +"for job group {JOB_GROUP}")
    # Initialize job environment dictionary
    job_env_dict = gda_util.initalize_job_env_dict(
        JOB_GROUP, JOB_GROUP,
        VERIF_CASE_STEP_abbrev, JOB_GROUP
    )
    # Loop through and write job script for dates and models
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
        for model_idx in range(len(model_list)):
            job_env_dict['MODEL'] = model_list[model_idx]
            job_env_dict['MODEL_EVS_DATA_DIR'] = (
                model_evs_data_dir_list[model_idx]
            )
            njobs+=1
            job_env_dict['job_num'] = str(njobs)
            # Create job file
            job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
            print(f"Creating job script: {job_file}")
            job = open(job_file, 'w')
            job.write('#!/bin/bash\n')
            job.write('set -x\n')
            job.write('\n')
            # Create job working directory
            job_env_dict['job_num_work_dir'] = os.path.join(
                DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                'job_work_dir', JOB_GROUP,
                f"job{job_env_dict['job_num']}"
            )
            job_env_dict['MET_TMP_DIR'] = os.path.join(
                job_env_dict['job_num_work_dir'], 'tmp'
            )
            # Set any environment variables for special cases
            # Write environment variables
            for name, value in job_env_dict.items():
                if name not in dont_write_env_var_list:
                    if '"' in value:
                        job.write(f"export {name}='{value}'\n")
                    else:
                        job.write(f'export {name}="{value}"\n')
            job.write('\n')
            # Do file checks
            stat_files_exist, copy_output_list = gda_util.check_stat_files(
                job_env_dict
            )
            if stat_files_exist:
                write_job_cmds = True
            else:
                write_job_cmds = False
            # Write job commands
            if write_job_cmds:
                gda_util.make_dir(job_env_dict['job_num_work_dir'])
                for cmd in gather_stats_jobs_dict['commands']:
                    job.write(cmd+'\n')
                    job.write('export err=$?; err_chk'+'\n')
                for output_file_tuple in copy_output_list:
                    job.write(f'if [ -f "{output_file_tuple[0]}" ]; then '
                              +f"cp -v {output_file_tuple[0]} "
                              +f"{output_file_tuple[1]}"
                              +f"; fi\n")
            job.close()
        date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "
              +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                            JOB_GROUP))
    poe_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'poe*'))
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
        poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                    'METplus_job_scripts',
                                    JOB_GROUP, 'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               str(iproc-1)+' '
               +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                'METplus_job_scripts',
                                JOB_GROUP, 'poe_jobs'+str(node))
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= int(nproc):
       if machine in ['HERA', 'ORION', 'S4', 'JET']:
           poe_file.write(
               str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
           )
       else:
           poe_file.write(
               '/bin/echo '+str(iproc)+'\n'
           )
       iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
