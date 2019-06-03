#! /bin/bash

set -e

export LC_NUMERIC="C"

log="log"

echo "$log:"
printf "\tmkdir -p \$@\n\n"

echo "/media/prudhomme/Elements/data_remi/ds:"
printf "\tmkdir -p \$@\n\n"

echo "/media/prudhomme/Elements/data_remi/ds/nlu:" ../ds/
printf "\tmkdir -p \$@\n\n"

year=$1

for diet_coefficient in AGO 0 1; do #0.2 0.5 0.8
  for climate_scenario in noco2_rcp4p5; do #noco2_rcp2p6 noco2_rcp8p5
    for pchi_scenario in  450ppm; do #Baseline 450ppm 550ppm
      for forest_scenario in Deforest 0 0.2; do #0 0.1 0.2 0.3
          for max_taux_inacc2acc in 0.05; do #0.01 0.1
            for do_increase_NUE in 0 1 1.5; do #0
              for is_bouwman_evolving in 0 1; do #0
                for pop_scenario in SSP1 SSP2 SSP3; do #SSP1 SSP2 SSP3 SSP4
                  for trade_scenario in 1.5 2 2.5; do #0 0.5 1 2 5
                     climate_scenario_name=`echo ${climate_scenario} | sed 's/_//'`
                     string=DietScen-${diet_coefficient}_PchiScenario-${pchi_scenario}_Forest-${forest_scenario}_Climate-${climate_scenario_name}_NUE-${do_increase_NUE}_RumProd-${is_bouwman_evolving}_PopScen-${pop_scenario}_TradeScen-${trade_scenario}
                     output_dir="/media/prudhomme/Elements/data_remi/ds/nlu/${string}"
                     output_dir_relative="/media/prudhomme/Elements/data_remi/ds/nlu/${string}"
                     printf "$output_dir_relative:\n"
                     printf "\tmkdir -p \$@\n\n"
             	     Run_prerequisites=""
               	     for model_type in ab sr cs; do #sr bii
           	       resulting_file_makefile="/media/prudhomme/Elements/data_remi/ds/nlu/${string}/${model_type}_${string}_${year}.nc"
                       result_files="$result_files $resulting_file_makefile"
                       echo "$resulting_file_makefile: ${Run_prerequisites} $output_dir_relative"
                       #printf "\trm -f ${output_dir}/${model_type}_${string}_${year}.png\n"
                       printf "\t(cd .. && python remi-modelr.py ../models/${model_type}-model.rds ${string} ${year} ${output_dir})\n\n"
	             done
                  done
                done
              done
            done
          done
      done
    done
  done
done

echo "simulations_sustainable.stamp: $result_files"
printf "\ttouch \$@\n\n"

