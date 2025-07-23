#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_grid2grid_stats_nwp_index.sh
# Developers: Shannon Shields / Shannon.Shields@noaa.gov
# Purpose of Script: This script is run for the global_det atmos stats step
#                    for the grid-to-grid NWP Index. It uses METplus to
#                    generate the index value.
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2gs"
echo "RUN MODE:$evs_run_mode"

# Source config
source $config
export err=$?; err_chk

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Check user's config settings
python $USHevs/global_det/global_det_atmos_check_settings_nwp_index.py
export err=$?; err_chk

# Create output directories
python $USHevs/global_det/global_det_atmos_create_output_dirs_nwp_index.py
export err=$?; err_chk

# Link needed stat files and set up model information
python $USHevs/global_det/global_det_atmos_get_stat_files.py
export err=$?; err_chk

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/grid2grid_stats/data/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/grid2grid_stats/data/mail_*; do
            $FILE
        done
    fi
fi

# Create and run job scripts for calculating NWP Index
for group in calc_nwp_index; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_stats_grid2grid_create_job_scripts_nwp_index.py
    export err=$?; err_chk
    chmod u+x ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/*
    . ${VERIF_CASE}_${STEP}/METplus_job_scripts/$group/*
    export err=$?; err_chk
done

# Copy stat files to desired location
if [ $SENDCOM = YES ]; then
    stat_file=$DATA/${VERIF_CASE}_${STEP}/METplus_output/$MODEL.$VDATE/evs.stats.$MODEL.$RUN.$VERIF_CASE.nwpindex.v$VDATE.stat
    if [ -s $stat_file ]; then
        cp -v $stat_file $COMOUT/$MODEL.$VDATE/.
    fi
fi
