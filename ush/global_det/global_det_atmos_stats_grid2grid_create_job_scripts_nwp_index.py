#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_job_scripts_nwp_index.py
Contact(s): Shannon Shields (shannon.shields@noaa.gov)
Abstract: This creates one main job script. This
          job script contains all the necessary environment variables
          and commands needed to run it.
Run By:   scripts/stats/global_det/exevs_stats_global_det_atmos_grid2grid_nwp_
          index.py
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
ref_model = os.environ['REFERENCENAME']
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
                                             'StatAnalysis_NWP_Index_00z.conf'
                                         ),
                                         gda_util.metplus_command(
                                             'StatAnalysis_NWP_Index_12z.conf'
                                         )]}

# Create job scripts
if JOB_GROUP == 'calc_nwp_index':
    print(f"----> Making job scripts for {VERIF_CASE_STEP} "
          +f"for job group {JOB_GROUP}")
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
            model = model_list[model_idx]
            job_env_dict['MODEL_ANL'] = model+'_anl'
            job_env_dict['REFERENCE_ANL'] = ref_model+'_anl'
            if model in ['cfs', 'aigfs']:
                job_env_dict['MODEL_ANL'] = 'gfs_anl'
                job_env_dict['REFERENCE_ANL'] = 'gfs_pers_anl'
            job_env_dict['MODEL'] = model_list[model_idx]
            job_env_dict['REFERENCE'] = ref_model
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
            # Create tmp working directory
            job_env_dict['MET_TMP_DIR'] = os.path.join(
                DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                'tmp'
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
            # Do stat file checks
            VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
            model_stat_file = os.path.join(
                VERIF_CASE_STEP_data_dir, model,
                model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
            )
            ref_stat_file = os.path.join(
                VERIF_CASE_STEP_data_dir, model,
                'revised_'+ref_model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
            )
            if gda_util.check_file_exists_size(model_stat_file) \
                    and gda_util.check_file_exists_size(ref_stat_file):
                write_job_cmds = True
            else:
                write_job_cmds = False
            # Write job commands
            if write_job_cmds:
                for cmd in calc_nwp_index_jobs_dict['commands']:
                    job.write(cmd+'\n')
                    job.write('export err=$?; err_chk'+'\n')
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
