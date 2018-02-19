#! /bin/bash

set -e

export LC_NUMERIC="C"

log="log"

#echo "$log:"
#printf "\tmkdir -p \$@\n\n"

#echo "../ds:"
#printf "\tmkdir -p \$@\n\n"

#echo "../ds/nlu:" ../ds/
#printf "\tmkdir -p \$@\n\n"

year=$1

    echo -e "SSP|SSP1|SSP2|SSP5\n" > ssp_scenarios.txt
    ssp_policy_value_list=`awk -F "|" '$1 == "'SSP'" {$1=""; print $0}' ssp_scenarios.txt | sed '1s/^.//'`
    for SSP in $ssp_policy_value_list; do
            string="SSP-${SSP}_Trade-2.001"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            printf "$output_dir_relative:\n"
            printf "\tmkdir -p \$@\n\n"
	 #for year in 2001 2098; do
          string="SSP-${SSP}_Trade-2.001"
    	  Run_prerequisites="../../../data/nlu/${string}/PREDICT_map_${string}_${year}_ann_light.nc"
      	  for model_type in ab sr; do #sr bii
  	    resulting_file_makefile="../ds/nlu/${string}/${model_type}_${string}_${year}.nc"
            output_dir="ds/nlu/${string}"
            output_dir_relative="../ds/nlu/${string}"
            result_files="$result_files $resulting_file_makefile"
            echo "$resulting_file_makefile: ${Run_prerequisites} $output_dir_relative"
            printf "\trm -f ${output_dir}/${model_type}_${string}_${year}.png\n"
            printf "\t(cd .. && python nlu-modelr.py -m ../models/ ${model_type} ${string} ${year} ${output_dir})\n\n"
	    #printf "\tgdal_translate -a_srs \"+proj=latlong +datum=WGS84\" -a_ullr -180 90 180 -90 -outsize 720 360  -of Gtiff ../ds/nlu/${string}/${model_type}_${string}_${year}.png \$@\n\n"
          #done
	  done
  done

echo "simulations_ssp.stamp: $result_files"
printf "\ttouch \$@\n\n"

