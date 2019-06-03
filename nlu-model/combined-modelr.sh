#! /bin/bash

set -e

export LC_NUMERIC="C"

log="log"

echo "$log:"
printf "\tmkdir -p \$@\n\n"

echo "../ds:"
printf "\tmkdir -p \$@\n\n"

echo "../ds/nlu:" ../ds/
printf "\tmkdir -p \$@\n\n"

year=$1
scp prudhomme@poseidon.centre-cired.fr:/diskdata/cired/prudhomme/land-use2/output_yad/MitigationScenarios/selected_mitigation_policy_combined_bis.csv selected_mitigation_policy.csv
scenario_list=`sed '1p' selected_mitigation_policy.csv`
for year in 2098; do
for scenario in  $scenario_list; do
  taxeC_value=0
  in_bioelecprod=`echo $scenario | awk 'BEGIN{FS="&"} {print $2}'`
  forest_scenario=`echo $scenario | awk 'BEGIN{FS="&"} {print $3}'`
  food_scenario=`echo $scenario | awk 'BEGIN{FS="&"} {print $4}'`
      for max_taux_inacc2acc in 0.05; do #0.01 0.1
        for do_increase_NUE in 0; do
            string="TaxeC-${taxeC_value}_Bioelec-${in_bioelecprod}_Forest-${forest_scenario}_Food-${food_scenario}_Inacc2acc-${max_taux_inacc2acc}_NUE-${do_increase_NUE}"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            printf "$output_dir_relative:\n"
            printf "\tmkdir -p \$@\n\n"
         done
      done
      for max_taux_inacc2acc in 0.05 ; do #0.01 0.1
        for do_increase_NUE in 0; do #1
          string="TaxeC-${taxeC_value}_Bioelec-${in_bioelecprod}_Forest-${forest_scenario}_Food-${food_scenario}_Inacc2acc-${max_taux_inacc2acc}_NUE-${do_increase_NUE}"
    	  Run_prerequisites="../../../data/nlu/${string}/PREDICT_map_${string}_${year}_ann_light.nc"
      	  for model_type in ab sr cs; do #sr bii
  	    resulting_file_makefile="../ds/nlu/${string}/${model_type}_${string}_${year}.nc"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            result_files="$result_files $resulting_file_makefile"
            echo "$resulting_file_makefile: ${Run_prerequisites} $output_dir_relative"
            printf "\trm -f ${output_dir}/${model_type}_${string}_${year}.png\n"
            printf "\t(cd .. && python remi-modelr.py ../models/${model_type}-model.rds ${string} ${year} ${output_dir})\n\n"
	    #printf "\tgdal_translate -a_srs \"+proj=latlong +datum=WGS84\" -a_ullr -180 90 180 -90 -outsize 720 360  -of Gtiff ../ds/nlu/${string}/${model_type}_${string}_${year}.png \$@\n\n"
          done
	done
      done
  done
done

echo "simulations_combined.stamp: $result_files"
printf "\ttouch \$@\n\n"

