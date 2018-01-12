#!/bin/bash 

set -e
year=$1
scenario='historical'
DATA_ROOT=${DATA_ROOT:=/Users/ricardog/src/eec/data}
OUTDIR=${OUTDIR:=/Users/ricardog/src/eec/predicts/playground/ds}

## Generate the four base layers.
for what in sr cs-sr ab cs-ab; do
    printf "  %-6s :: %s\n" ${what} ${year}
    ./ipbes-project.py -m ~/src/eec/predicts/models/sam/2018-01-05/ \
		       ${what} ${scenario} ${year} > /dev/null
done

## Combine base layers into BII layer.
for what in sr ab; do
    if [ "${what}" == "ab" ]; then
	v1="Abundance"
	v2="Ab"
    else
	v1="Richness"
	v2="SR"
    fi
    rio clip ${OUTDIR}/luh2/${scenario}-CompSim${v2}-${year}.tif \
	--like ${OUTDIR}/luh2/${scenario}-${v1}-${year}.tif \
	--output ${OUTDIR}/luh2/${scenario}-CompSim${v2}-${year}.tif
	
    rio calc --co "COMPRESS=lzw" --co "PREDICTOR=2" --masked \
	-t float32 "(* (read 1 1) (read 2 1))" \
	-o ${OUTDIR}/luh2/${scenario}-BII${v2}-${year}.tif ${OUTDIR}/luh2/${scenario}-${v1}-${year}.tif ${OUTDIR}/luh2/${scenario}-CompSim${v2}-${year}.tif
done
