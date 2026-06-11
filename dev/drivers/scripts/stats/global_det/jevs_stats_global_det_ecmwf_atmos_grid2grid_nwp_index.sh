#PBS -N jevs_stats_global_det_ecmwf_atmos_grid2grid_nwp_index
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=shared,select=1:ncpus=1:mem=5GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/feature_global_det_NWP_Index/EVS

export SENDCOM=YES
export KEEPDATA=NO
export job=${PBS_JOBNAME:-jevs_stats_global_det_ecmwf_atmos_grid2grid_nwp_index}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_det/global_det_stats.sh

export evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2
export USE_CFP=NO
export nproc=1


export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2grid
export MODELNAME=ecmwf
export REFERENCENAME=ecmwf_pers

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/${COMPONENT}_nwp_index

export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}.nwp_index

# CALL executable job script here
$HOMEevs/jobs/JEVS_STATS_GLOBAL_DET_NWP_INDEX

######################################################################
# Purpose: This calculates the NWP Index for the global deterministic
#          atmospheric grid-to-grid component for ECMWF
######################################################################
