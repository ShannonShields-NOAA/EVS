#PBS -N jevs_stats_global_det_fnmoc_atmos_grid2grid_persistence_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter:shared,select=1:ncpus=10:ompthreads=1:mem=15GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export SENDMAIL=YES
export KEEPDATA=NO
export job=${PBS_JOBNAME:-jevs_stats_global_det_fnmoc_atmos_grid2grid_persistence}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_det/global_det_stats.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2
export USE_CFP=YES
export nproc=10

export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2grid
export MODELNAME=fnmoc

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT

export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.persistence.${MODELNAME}

source $HOMEevs/dev/drivers/set_MAILTO.sh

# CALL executable job script here
$HOMEevs/jobs/JEVS_STATS_GLOBAL_DET_PERSISTENCE

######################################################################
# Purpose: This does the persistence statistics work for the global deterministic
#          atmospheric grid-to-grid component for FNMOC
######################################################################
