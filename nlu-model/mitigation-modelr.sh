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

  for mitigation_policy in "reg_taxeC" "bioelec_scenario" "forest_scenario" "food_scenario" ; do
    reg_taxeC="NoScenario" #LinearIncrease
    taxeC_value=0
    bioelec_scenario="NoScenario" #"LinearIncrease"
    in_bioelecprod=0 #150 300
    forest_scenario="Historical" #NoScenario RCP85
    food_scenario="DietAgTUrbanization"
    echo -e "reg_taxeC|0|85|200\nbioelec_scenario|150|300\nforest_scenario|RCP45\nfood_scenario|DietAgTHealthy" > mitigation_scenarios.txt
    mitigation_policy_value_list=`awk -F "|" '$1 == "'${mitigation_policy}'" {$1=""; print $0}' mitigation_scenarios.txt | sed '1s/^.//'`
    for mitigation_policy_value in $mitigation_policy_value_list ; do
      if [[ $mitigation_policy = "reg_taxeC" ]]; then
        reg_taxeC="LinearIncrease"
	if [[ ${mitigation_policy_value} = 200 ]]; then
	    taxeC_value=30
            food_scenario="DietAgTHealthy"
            bioelec_scenario="LinearIncrease"
            in_bioelecprod=150
            forest_scenario="RCP45"
        else
            taxeC_value=${mitigation_policy_value}
        fi
        reg_taxeC_begin=0
        Begin_taxeC_year=2020
        increase_taux_taxeC=`bc <<< "scale=10; (${mitigation_policy_value}-${reg_taxeC_begin})/(2098-${Begin_taxeC_year})"`
      elif [[ $mitigation_policy = "bioelec_scenario" ]]; then
        bioelec_scenario="LinearIncrease"
        in_bioelecprod=${mitigation_policy_value}
      elif [[ $mitigation_policy = "forest_scenario" ]]; then
        forest_scenario=${mitigation_policy_value}
      elif [[ $mitigation_policy = "food_scenario" ]]; then
        food_scenario=${mitigation_policy_value}
      fi
      for max_taux_inacc2acc in 0.01 0.05 0.1; do #0.01 0.1
        for do_increase_NUE in 0 1 ; do
            string="TaxeC-${taxeC_value}_Bioelec-${in_bioelecprod}_Forest-${forest_scenario}_Food-${food_scenario}_Inacc2acc-${max_taux_inacc2acc}_NUE-${do_increase_NUE}"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            printf "$output_dir_relative:\n"
            printf "\tmkdir -p \$@\n\n"
         done
      done
      for max_taux_inacc2acc in 0.05; do #0.01 0.1
        for do_increase_NUE in 0; do #1
	 #for year in 2001 2098; do
          string="TaxeC-${taxeC_value}_Bioelec-${in_bioelecprod}_Forest-${forest_scenario}_Food-${food_scenario}_Inacc2acc-${max_taux_inacc2acc}_NUE-${do_increase_NUE}"
    	  Run_prerequisites="../../../data/nlu/${string}/PREDICT_map_${string}_${year}_ann_light.nc"
      	  for model_type in ab sr; do #sr bii
  	    resulting_file_makefile="../ds/nlu/${string}/${model_type}_${string}_${year}.nc"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            result_files="$result_files $resulting_file_makefile"
            echo "$resulting_file_makefile: ${Run_prerequisites} $output_dir_relative"
            printf "\trm -f ${output_dir}/${model_type}_${string}_${year}.png\n"
            printf "\t(cd .. && python nlu-modelr.py -m ../models/ ${model_type} ${string} ${year} ${output_dir})\n\n "
	    #printf "\tgdal_translate -a_srs \"+proj=latlong +datum=WGS84\" -a_ullr -180 90 180 -90 -outsize 720 360  -of Gtiff ../ds/nlu/${string}/${model_type}_${string}_${year}.png \$@\n\n"
          #done
	done
      done
    done
  done
done

echo "simulations_mitigation.stamp: $result_files"
printf "\ttouch \$@\n\n"

