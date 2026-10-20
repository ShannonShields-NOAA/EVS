#!/usr/bin/env python3
'''
Name: global_det_atmos_get_stat_files.py
Contact(s): Shannon Shields (shannon.shields@noaa.gov)
Abstract: This gets the necessary stat files for Sensible Weather Index.
Run By: scripts/stats/global_det/exevs_stats_global_det_atmos_grid2obs_sensible_weather_index.sh
        scripts/plots/global_det/exevs_plots_global_det_atmos_grid2obs_sensible_weather_index.sh
'''

import os
import datetime
import global_det_atmos_util as gda_util
import global_det_atmos_sensible_weather_index_util as gda_swiutil

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
if STEP == 'stats':
    ref_model = os.environ['REFERENCENAME']
    COMINpara = COMIN.replace(USER, 'emc.vpppg')
    COMINv17 = COMIN.replace(USER, 'qi.shi')

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
        if VERIF_CASE_STEP_type == 'nwp_index':
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
                        if model == 'aifs':
                            COMINaifs = os.environ['COMINaifs']
                            model_evs_data_dir = os.path.join(
                                COMINaifs,
                                STEP, COMPONENT,
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            model_ref_evs_data_dir = os.path.join(
                                COMIN,
                                STEP, COMPONENT,
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            source_model_ref_date_stat_file = os.path.join(
                                model_ref_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'persistence.v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                        elif model == 'gfsv17':
                            model_evs_data_dir = os.path.join(
                                COMINv17,
                                STEP, COMPONENT,
                                'gfs.'+date_dt.strftime('%Y%m%d')
                            )
                            model_ref_evs_data_dir = os.path.join(
                                COMIN,
                                STEP, COMPONENT,
                                'gfs.'+date_dt.strftime('%Y%m%d')
                            )
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir,
                                'evs.stats.gfs.'+RUN+'.'+VERIF_CASE+'.'
                                +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            source_model_ref_date_stat_file = os.path.join(
                                model_ref_evs_data_dir,
                                'evs.stats.gfs.'+RUN+'.'+VERIF_CASE+'.'
                                +'persistence.v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                        else:
                            model_evs_data_dir = os.path.join(
                                COMINpara,
                                STEP, COMPONENT, 
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            model_ref_evs_data_dir = os.path.join(
                                COMIN,
                                STEP, COMPONENT,
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            source_model_ref_date_stat_file = os.path.join(
                                model_ref_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'persistence.v'+date_dt.strftime('%Y%m%d')+'.stat'
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
                    if gda_nwputil.check_stat_file_exists_size(
                            source_model_date_stat_file
                    ):
                        print("Linking "+source_model_date_stat_file+" to "
                              +dest_model_date_stat_file)
                        os.symlink(source_model_date_stat_file,
                                   dest_model_date_stat_file)
                        if model == 'gfsv17':
                            org_file = dest_model_date_stat_file
                            rev_file = os.path.join(
                                VERIF_CASE_STEP_data_dir, model,
                                'revised_'+model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            # Change gfs to gfsv17 in stat file
                            with open(org_file, 'r') as f_in, open(rev_file, 'w') as f_out:
                                for line in f_in:
                                    modified_line = line.replace("gfs", model)
                                    f_out.write(modified_line)
                            print("Done! "+rev_file+" has been created.")
                            os.remove(org_file)
                            print("Removed "+org_file)
                            os.rename(rev_file, dest_model_date_stat_file)
                            print("Renamed "+rev_file+" to "+dest_model_date_stat_file)
                if not os.path.exists(dest_model_ref_date_stat_file):
                    if gda_nwputil.check_stat_file_exists_size(
                            source_model_ref_date_stat_file
                    ):
                        print("Linking "+source_model_ref_date_stat_file+" to "
                              +dest_model_ref_date_stat_file)
                        os.symlink(source_model_ref_date_stat_file,
                                   dest_model_ref_date_stat_file)
                        org_file = dest_model_ref_date_stat_file
                        rev_file = os.path.join(
                            VERIF_CASE_STEP_data_dir, model,
                            'revised_'+ref_model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                        # This replicates sed command to modify stat lines
                        with open(org_file, 'r') as f_in, open(rev_file, 'w') as f_out:
                            for line in f_in:
                                if model == 'gfsv17':
                                    modified_line = line.replace("gfs", ref_model)
                                elif model == 'cfs':
                                    modified_line = line.replace(model, ref_model).replace("gfs", "gfs_pers")
                                elif model == 'aigfs':
                                    modified_line = line.replace("gfs", "gfs_pers")
                                else:
                                    modified_line = line.replace(model, ref_model)
                                f_out.write(modified_line)
                        print("Done! "+rev_file+" has been created.")
                date_dt = date_dt + datetime.timedelta(days=1)
elif VERIF_CASE_STEP == 'grid2obs_stats':
    # Read in VERIF_CASE_STEP related environment variables
    # Get model stat files for each option in VERIF_CASE_STEP_type_list
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        print("----> Getting files for "+VERIF_CASE_STEP+" "
              +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Read in VERIF_CASE_STEP_type related environment variables
        # Set valid hours
        if VERIF_CASE_STEP_type == 'sensible_weather_index':
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
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
                        if model == 'gfsv17':
                            model_evs_data_dir = os.path.join(
                                COMINv17,
                                STEP, COMPONENT,
                                'gfs.'+date_dt.strftime('%Y%m%d')
                            )
                            model_ref_evs_data_dir = os.path.join(
                                COMIN,
                                STEP, COMPONENT,
                                'gfs.'+date_dt.strftime('%Y%m%d')
                            )
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir,
                                'evs.stats.gfs.'+RUN+'.'+VERIF_CASE+'.'
                                +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            source_model_ref_date_stat_file = os.path.join(
                                model_ref_evs_data_dir,
                                'evs.stats.gfs.'+RUN+'.'+VERIF_CASE+'.'
                                +'persistence.v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                        else:
                            model_evs_data_dir = os.path.join(
                                COMINpara,
                                STEP, COMPONENT,
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            model_ref_evs_data_dir = os.path.join(
                                COMIN,
                                STEP, COMPONENT,
                                model+'.'+date_dt.strftime('%Y%m%d')
                            )
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            source_model_ref_date_stat_file = os.path.join(
                                model_ref_evs_data_dir,
                                'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                                +'persistence.v'+date_dt.strftime('%Y%m%d')+'.stat'
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
                    if gda_swiutil.check_stat_file_exists_size(
                            source_model_date_stat_file
                    ):
                        print("Linking "+source_model_date_stat_file+" to "
                              +dest_model_date_stat_file)
                        os.symlink(source_model_date_stat_file,
                                   dest_model_date_stat_file)
                        if model == 'gfsv17':
                            org_file = dest_model_date_stat_file
                            rev_file = os.path.join(
                                VERIF_CASE_STEP_data_dir, model,
                                'revised_'+model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                            # Change gfs to gfsv17 in stat file
                            with open(org_file, 'r') as f_in, open(rev_file, 'w') as f_out:
                                for line in f_in:
                                    modified_line = line.replace("gfs", model)
                                    f_out.write(modified_line)
                            print("Done! "+rev_file+" has been created.")
                            os.remove(org_file)
                            print("Removed "+org_file)
                            os.rename(rev_file, dest_model_date_stat_file)
                            print("Renamed "+rev_file+" to "+dest_model_date_stat_file)
                if not os.path.exists(dest_model_ref_date_stat_file):
                    if gda_swiutil.check_stat_file_exists_size(
                            source_model_ref_date_stat_file
                    ):
                        print("Linking "+source_model_ref_date_stat_file+" to "
                              +dest_model_ref_date_stat_file)
                        os.symlink(source_model_ref_date_stat_file,
                                   dest_model_ref_date_stat_file)
                        org_file = dest_model_ref_date_stat_file
                        rev_file = os.path.join(
                            VERIF_CASE_STEP_data_dir, model,
                            'revised_'+ref_model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                        # This replicates sed command to modify stat lines
                        with open(org_file, 'r') as f_in, open(rev_file, 'w') as f_out:
                            for line in f_in:
                                if model == 'gfsv17':
                                    modified_line = line.replace("gfs", ref_model).replace("ADPSFC", "ADPSFC_pers")
                                else:
                                    modified_line = line.replace(model, ref_model).replace("ADPSFC", "ADPSFC_pers")
                                f_out.write(modified_line)
                        print("Done! "+rev_file+" has been created.")
                date_dt = date_dt + datetime.timedelta(days=1)
elif STEP == 'plots':
    # Read in VERIF_CASE_STEP related environment variables
    # Get nwp index stat files
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
    date_type = 'VALID'
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_type_valid_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
        ].split(' ')
        for VERIF_CASE_STEP_type_valid_hr in VERIF_CASE_STEP_type_valid_hr_list:
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
                                +'nwpindex.v'+date_dt.strftime('%Y%m%d')+VERIF_CASE_STEP_type_valid_hr+'.stat'
                            )
                        else:
                            source_model_date_stat_file = os.path.join(
                                model_evs_data_dir, 'evs_data',
                                COMPONENT, RUN, VERIF_CASE, model,
                                model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                            )
                        dest_model_date_stat_file = os.path.join(
                            VERIF_CASE_STEP_data_dir, model,
                            model+'_nwpindex_v'+date_dt.strftime('%Y%m%d')+VERIF_CASE_STEP_type_valid_hr+'.stat'
                        )
                    if not os.path.exists(dest_model_date_stat_file):
                        if gda_nwputil.check_nwp_index_file_exists_size(
                                source_model_date_stat_file
                        ):
                            print("Linking "+source_model_date_stat_file+" to "
                                  +dest_model_date_stat_file)
                            os.symlink(source_model_date_stat_file,
                                       dest_model_date_stat_file)
                    date_dt = date_dt + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
