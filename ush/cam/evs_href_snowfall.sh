#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


############################################################


>run_all_href_snowfall_poe.sh

for obsv in 6h 24h  ; do

     >run_href_snow${obsv}.sh

      echo "export regrid=G212" >> run_href_snow${obsv}.sh
      
      echo  "export output_base=$WORK/precip/run_href_snow${obsv}" >> run_href_snow${obsv}.sh
      
      echo  "export obsv=${obsv}" >> run_href_snow${obsv}.sh
      echo  "export obsvpath=$COMSNOW" >> run_href_snow${obsv}.sh
      echo  "export obsvgrid=grid184" >> run_href_snow${obsv}.sh
      echo  "export OBTYPE=NOHRSC" >> run_href_snow${obsv}.sh 

      echo  "export name=WEASD" >> run_href_snow${obsv}.sh
      echo  "export name_obsv=ASNOW" >> run_href_snow${obsv}.sh

      if [ $obsv = 6h ] ; then
        echo  "export level=A06" >> run_href_snow${obsv}.sh
        echo  "export thresh='ge1, ge2, ge4, ge8'" >> run_href_snow${obsv}.sh
        echo  "export vbeg=0" >>run_href_snow${obsv}.sh
        echo  "export vend=18" >>run_href_snow${obsv}.sh
        echo  "export valid_increment=21600" >> run_href_snow${obsv}.sh
        echo  "export lead='6,12,18,24,30,36,42,48'" >> run_href_snow${obsv}.sh
      elif [ $obsv = 24h ] ; then
        echo  "export level=A24" >> run_href_snow${obsv}.sh
        echo  "export thresh='ge1, ge4, ge8, ge12'" >> run_href_snow${obsv}.sh
        echo  "export vbeg=0" >>run_href_snow${obsv}.sh
        echo  "export vend=12" >>run_href_snow${obsv}.sh
        echo  "export valid_increment=43200" >> run_href_snow${obsv}.sh
        echo  "export lead='24,30,36,42,48'" >> run_href_snow${obsv}.sh

      fi

       echo  "export MODEL=HREF" >> run_href_snow${obsv}.sh
       echo  "export regrid=FCST" >> run_href_snow${obsv}.sh
       echo  "export modelpath=$COMHREF" >> run_href_snow${obsv}.sh
       echo  "export modelgrid=conus" >> run_href_snow${obsv}.sh
       echo  "export modeltail=''" >> run_href_snow${obsv}.sh
       echo  "export extradir='verf_g2g/'" >> run_href_snow${obsv}.sh


       echo  "export verif_grid='' " >> run_href_snow${obsv}.sh
       echo  "export verif_poly='${maskpath}/Bukovsky_G212_CONUS.nc, ${maskpath}/Bukovsky_G212_CONUS_East.nc, ${maskpath}/Bukovsky_G212_CONUS_West.nc, ${maskpath}/Bukovsky_G212_CONUS_South.nc, ${maskpath}/Bukovsky_G212_CONUS_Central.nc' " >> run_href_snow${obsv}.sh



       echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/EnsembleStat_fcstHREF_obsNOHRSC.conf " >> run_href_snow${obsv}.sh

      echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstHREFmean_obsNOHRSC.conf " >> run_href_snow${obsv}.sh

        echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_snow${obsv}.sh
       chmod +x run_href_snow${obsv}.sh
       echo "run_href_snow${obsv}.sh" >> run_all_href_snowfall_poe.sh


done  #end of obsv

chmod 775 run_all_href_snowfall_poe.sh


