#!/usr/bin/env python3
'''
Name: global_det_atmos_get_stat_files.py
Contact(s): Shannon Shields (shannon.shields@noaa.gov)
Abstract: This gets the necessary stat files for NWP Index.
Run By: scripts/stats/global_det/exevs_global_det_atmos_grid2grid_stats_nwp_index.sh
'''

import os
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
COMIN = os.environ['COMIN']
model_list = os.environ['model_list'].split(' ')
ref_model = os.environ['REFERENCENAME']
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
USER = os.environ['USER']
evs_run_mode = os.environ['evs_run_mode']
if evs_run_mode != 'production':
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    machine = os.environ['machine']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

# Set archive paths
if evs_run_mode != 'production':
    archive_obs_data_dir = os.environ['archive_obs_data_dir']
else:
    archive_obs_data_dir = '/dev/null'

# Make sure in right working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

if VERIF_CASE_STEP == 'grid2grid_stats':
    # Get model stat files for
    # each option in VERIF_CASE_STEP_type_list
    # Read in VERIF_CASE_STEP related environment variables
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        print("----> Getting files for "+VERIF_CASE_STEP+" "
              +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Read in VERIF_CASE_STEP_type related environment variables
        # Set valid hours
        if VERIF_CASE_STEP_type == 'nwp':
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        else:
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        # Set forecast hours
        if VERIF_CASE_STEP_abbrev_type+'_fhr_list' in list(os.environ.keys()):
            VERIF_CASE_STEP_type_fhr_list = [
                int(i) for i in
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_list'].split(' ')
            ]
        else:
            VERIF_CASE_STEP_type_fhr_min = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_min']
            )
            VERIF_CASE_STEP_type_fhr_max = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_max']
            )
            VERIF_CASE_STEP_type_fhr_inc = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_inc']
            )
            VERIF_CASE_STEP_type_fhr_list = list(
                range(int(VERIF_CASE_STEP_type_fhr_min),
                      int(VERIF_CASE_STEP_type_fhr_max)
                      +int(VERIF_CASE_STEP_type_fhr_inc),
                      int(VERIF_CASE_STEP_type_fhr_inc))
            )
        # Get model stat files
        start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
        VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
        date_type = 'VALID'
        for model_idx in range(len(model_list)):
            model = model_list[model_idx]
            date_dt = start_date_dt
            while date_dt <= end_date_dt:
                if date_type == 'VALID':
                    if evs_run_mode == 'production':
                        model_evs_data_dir = os.path.join(
                            COMIN, STEP, COMPONENT, 
                            model+'.'+date_dt.strftime('%Y%m%d')
                        )
                        model_ref_evs_data_dir = os.path.join(
                            COMIN, STEP, COMPONENT,
                            ref_model+'.'+date_dt.strftime('%Y%m%d')
                        )
                        source_model_date_stat_file = os.path.join(
                            model_evs_data_dir,
                            'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                        source_model_ref_date_stat_file = os.path.join(
                            model_ref_evs_data_dir,
                            'evs.stats.'+ref_model+'.'+RUN+'.'+VERIF_CASE+'.'
                            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                    else:
                        source_model_date_stat_file = os.path.join(
                            model_evs_data_dir, 'evs_data',
                            COMPONENT, RUN, VERIF_CASE, model,
                            model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                    dest_model_date_stat_file = os.path.join(
                        VERIF_CASE_STEP_data_dir, model,
                        model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                    dest_model_ref_date_stat_file = os.path.join(
                        VERIF_CASE_STEP_data_dir, model,
                        ref_model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                if not os.path.exists(dest_model_date_stat_file):
                    if gda_util.check_file_exists_size(
                            source_model_date_stat_file
                    ):
                        print("Linking "+source_model_date_stat_file+" to "
                              +dest_model_date_stat_file)
                        os.symlink(source_model_date_stat_file,
                                   dest_model_date_stat_file)
                if not os.path.exists(dest_model_ref_date_stat_file):
                    if gda_util.check_file_exists_size(
                            source_model_ref_date_stat_file
                    ):
                        print("Linking "+source_model_ref_date_stat_file+" to "
                              +dest_model_ref_date_stat_file)
                        os.symlink(source_model_ref_date_stat_file,
                                   dest_model_ref_date_stat_file)
                date_dt = date_dt + datetime.timedelta(days=1)
elif VERIF_CASE_STEP == 'grid2obs_stats':
    # Read in VERIF_CASE_STEP related environment variables
    # Get model forecast and truth files for each option in VERIF_CASE_STEP_type_list
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        print("----> Getting files for "+VERIF_CASE_STEP+" "
              +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Read in VERIF_CASE_STEP_type related environment variables
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres_levs', 'sfc', 'ptype']:
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_init_hr_list'
        ].split(' ')
        # Set forecast hours
        if VERIF_CASE_STEP_abbrev_type+'_fhr_list' in list(os.environ.keys()):
            VERIF_CASE_STEP_type_fhr_list = [
                int(i) for i in
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_list'].split(' ')
            ]
        else:
            VERIF_CASE_STEP_type_fhr_min = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_min']
            )
            VERIF_CASE_STEP_type_fhr_max = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_max']
            )
            VERIF_CASE_STEP_type_fhr_inc = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_inc']
            )
            VERIF_CASE_STEP_type_fhr_list = list(
                range(int(VERIF_CASE_STEP_type_fhr_min),
                      int(VERIF_CASE_STEP_type_fhr_max)
                      +int(VERIF_CASE_STEP_type_fhr_inc),
                      int(VERIF_CASE_STEP_type_fhr_inc))
           )
        # Get time information
        VERIF_CASE_STEP_type_time_info_dict = gda_util.get_time_info(
            start_date, end_date, 'VALID', VERIF_CASE_STEP_type_init_hr_list,
            VERIF_CASE_STEP_type_valid_hr_list, VERIF_CASE_STEP_type_fhr_list
        )
        # Get forecast files for each model
        VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
        VERIF_CASE_STEP_type_valid_time_list = []
        for time in VERIF_CASE_STEP_type_time_info_dict:
            if time['valid_time'] not in VERIF_CASE_STEP_type_valid_time_list:
                VERIF_CASE_STEP_type_valid_time_list.append(time['valid_time'])
            for model_idx in range(len(model_list)):
                model = model_list[model_idx]
                model_file_format = model_file_format_list[model_idx]
                VERIF_CASE_STEP_model_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, model
                )
                model_fcst_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_model_dir,
                    model+'.'+'{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                )
                gda_util.make_dir(VERIF_CASE_STEP_model_dir)
                gda_util.get_model_file(
                    time['valid_time'], time['init_time'],
                    time['forecast_hour'], model_file_format,
                    model_fcst_dest_file_format,
                )
                if VERIF_CASE_STEP_type == 'sfc':
                    # Get files for anomaly daily averages, same init
                    if int(time['forecast_hour']) % 24 == 0:
                        nf = 1
                        while nf <= 3:
                            minus_hr = nf * 6
                            fhr = int(time['forecast_hour'])-minus_hr
                            if fhr >= 0:
                                gda_util.get_model_file(
                                    time['valid_time'] \
                                    - datetime.timedelta(hours=minus_hr),
                                    time['init_time'],
                                    str(fhr),
                                    model_file_format,
                                    model_fcst_dest_file_format,
                                )
                                gda_util.get_model_file(
                                    time['valid_time'],
                                    time['init_time'] \
                                    - datetime.timedelta(hours=minus_hr),
                                    str(fhr),
                                    model_file_format,
                                    model_fcst_dest_file_format,
                                )
                            nf+=1
        # Get truth files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type in ['pres_levs', 'sfc']:
                # GDAS prepbufr
                if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['00', '06', '12', '18']:
                    gdas_prod_file_format = os.path.join(
                        COMIN, 'prep', COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
                        'prepbufr_gdas', 'pb2nc_gdas_'+VERIF_CASE_STEP_type
                        +'_valid{valid?fmt=%Y%m%d%H}.nc'
                    )
                    gdas_arch_file_format = os.path.join(
                        archive_obs_data_dir, 'pb2nc_gdas',
                        'pb2nc_gdas_'+VERIF_CASE_STEP_type
                        +'_valid{valid?fmt=%Y%m%d%H}.nc'
                    )
                    VERIF_CASE_STEP_gdas_dir = os.path.join(
                        VERIF_CASE_STEP_data_dir, 'prepbufr_gdas'
                    )
                    gda_util.make_dir(VERIF_CASE_STEP_gdas_dir)
                    gdas_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_gdas_dir,
                        'prepbufr.gdas.'+VERIF_CASE_STEP_type
                        +'.{valid?fmt=%Y%m%d%H}'
                    )
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time, 'Prepbufr GDAS',
                        gdas_prod_file_format, gdas_arch_file_format,
                        evs_run_mode, gdas_dest_file_format
                    )
            if VERIF_CASE_STEP_type in ['sfc', 'ptype']:
                # NAM prepbufr
                nam_prod_file_format = os.path.join(
                    COMIN, 'prep', COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
                    'prepbufr_nam', 'pb2nc_nam_'+VERIF_CASE_STEP_type
                    +'_valid{valid?fmt=%Y%m%d%H}.nc'
                )
                nam_arch_file_format = os.path.join(
                     archive_obs_data_dir, 'prepbufr_gdas',
                     'pb2nc_nam_'+VERIF_CASE_STEP_type
                     +'_valid{valid?fmt=%Y%m%d%H}.nc'
                )
                VERIF_CASE_STEP_nam_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'prepbufr_nam'
                )
                gda_util.make_dir(VERIF_CASE_STEP_nam_dir)
                nam_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nam_dir,
                    'prepbufr.nam.'+VERIF_CASE_STEP_type+'.'
                    +'{valid?fmt=%Y%m%d%H}'
                )
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'Prepbufr NAM',
                    nam_prod_file_format, nam_arch_file_format, evs_run_mode,
                    nam_dest_file_format
                )
elif STEP == 'plots' :
    # Read in VERIF_CASE_STEP related environment variables
    # Get model stat files
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
    date_type = 'VALID'
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        model_evs_data_dir = model_evs_data_dir_list[model_idx]
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            if date_type == 'VALID':
                if evs_run_mode == 'production':
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir+'.'+date_dt.strftime('%Y%m%d'),
                        'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                        +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                else:
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir, 'evs_data',
                        COMPONENT, RUN, VERIF_CASE, model,
                        model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                dest_model_date_stat_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                )
            if not os.path.exists(dest_model_date_stat_file):
                if gda_util.check_file_exists_size(
                        source_model_date_stat_file
                ):
                    print("Linking "+source_model_date_stat_file+" to "
                          +dest_model_date_stat_file)
                    os.symlink(source_model_date_stat_file,
                               dest_model_date_stat_file)
            date_dt = date_dt + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
