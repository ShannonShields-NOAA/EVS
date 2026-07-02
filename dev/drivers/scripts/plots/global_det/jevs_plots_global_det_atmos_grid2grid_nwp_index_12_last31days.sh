#PBS -N jevs_plots_global_det_atmos_grid2grid_nwp_index_12_last31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=5:ompthreads=1:mem=150GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/feature_global_det_NWP_Index/EVS

export SENDCOM=YES
export KEEPDATA=NO
export SENDDBN=NO
export job=${PBS_JOBNAME:-jevs_plots_global_det_atmos_grid2grid_nwp_index_12_last31days}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=12

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_det/global_det_plots.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2
export USE_CFP=YES
export nproc=5

export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2grid
export VERIF_TYPE=nwp_index
export NDAYS=31

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
today=$(cut -c7-14 ${COMROOT}/date/t${vhr}z)
export VDATE_END=${VDATE_END:-$(finddate.sh $today d-2)}
export COMOUT=/lfs/h2/emc/ptmp/${USER}/EVS_nwp_index/$NET/$evs_ver_2d/$STEP/$COMPONENT/$RUN.$VDATE_END

# Set config file
export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${VERIF_TYPE}

# CALL executable job script here
$HOMEevs/jobs/JEVS_PLOTS_GLOBAL_DET_NWP_INDEX

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-grid NWP Index for last 31 days 12Z
######################################################################
