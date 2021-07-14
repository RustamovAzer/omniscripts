#!/bin/bash -e

# get performance of modin on omnisci
export MODIN_BACKEND=omnisci
export MODIN_EXPERIMENTAL=true
export MODIN_TEST_DATASET_SIZE=big

cd modin/asv_bench
conda activate modin_on_omnisci

OMNISCI_MACHINE_NAME=$HOST_NAME-omnisci
PANDAS_MACHINE_NAME=$HOST_NAME-pandas

# 'number=1' allows for each bench run to get tables with different names (in `trigger_import`),
# which eliminates caching inside OmniSci (`setup` is called before every run)
asv run --launch-method=forkserver --config asv.conf.omnisci.json \
    -b ^omnisci --machine $OMNISCI_MACHINE_NAME -a repeat=3 -a number=1 \
    --show-stderr --python=same --set-commit-hash HEAD
OMNISCI_RESULT_NAME=`ls .asv/results/$OMNISCI_MACHINE_NAME/ | grep existing`

# get performance of pure pandas
export MODIN_ASV_USE_IMPL=pandas

asv run --launch-method=forkserver --config asv.conf.omnisci.json \
    -b ^omnisci --machine $PANDAS_MACHINE_NAME -a repeat=3 \
    --show-stderr --python=same --set-commit-hash HEAD
PANDAS_RESULT_NAME=`ls .asv/results/$PANDAS_MACHINE_NAME/ | grep existing`

# report modin on omnisci results
if [ -z "$DB_COMMON_OPTS" ]; then
    echo env variable DB_COMMON_OPTS is undefined - no results will be report
    exit 0
fi

cd ../../omniscripts
python report_asv_result.py \
    --result-path ../modin/asv_bench/.asv/results/$OMNISCI_MACHINE_NAME/$OMNISCI_RESULT_NAME \
    $DB_COMMON_OPTS

# report pandas results
python report_asv_result.py \
    --result-path ../modin/asv_bench/.asv/results/$PANDAS_MACHINE_NAME/$PANDAS_RESULT_NAME \
    $DB_COMMON_OPTS
