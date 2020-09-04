#!/usr/bin/env bash

LOG_PATH=/home/ubuntu/elb-logs
CSV_PATH=/home/ubuntu/git/aws-elb-access-log2csv/csv
LOG2CSV_PATH=/home/ubuntu/git/aws-elb-access-log2csv

usage(){
    echo "Usage: $0 [[[-a area] [-p prefix]] | [-h]]]"
    echo
    echo "  -a, --area: {all|elb_pre|elb_service|elb_service2} "
    echo "  -p, --prefix:   yyyyMMdd or yyyyMMddThh format string (ex. 20200901 or 202009T01)"
    echo
    exit 1
}

run_log2csv(){
	local input_log=$1
	local output_csv=$2
	echo -n "creating ${output_csv}..."
    python ${LOG2CSV_PATH}/log2csv.py \
        -i ${input_log} \
        -o ${output_csv}
}

make_csv(){
    local area=$1
    local dateStr=$2
    local year=${dateStr:0:4}
    local month=${dateStr:4:2}
    local day=${dateStr:6:2}
    local hour=${dateStr:9:2}
    local elb_log_path=${LOG_PATH}/${area}/${year}/${month}/${day}
	local csv_log_path=${CSV_PATH}/${area}/${year}/${month}/${day}

	mkdir -p ${csv_log_path}

	if [ -z "${hour}" ]; then
		for i in {0..23}; do
			_hour=$(printf "%.2d" ${i})
			_date=${year}${month}${day}T${_hour}
			zcat ${elb_log_path}/*${_date}*.log.gz > ${elb_log_path}/${area}_access_${_date}.log
			run_log2csv ${elb_log_path}/${area}_access_${_date}.log ${csv_log_path}/${area}_access_${_date}.csv
		done
	else
		zcat ${elb_log_path}/*${dateStr}*.log.gz > ${elb_log_path}/${area}_access_${dateStr}.log
        run_log2csv ${elb_log_path}/${area}_access_${dateStr}.log ${csv_log_path}/${area}_access_${dateStr}.csv
	fi
}


while getopts "p:a:h:" opt; do
    case $opt in
        p | --prefix) DATESTR=$OPTARG
            ;;
        a | --area) AREA=$OPTARG
            ;;
        h | --help) usage
            ;;
        esac
done

if [ -z "${DATESTR}" ]; then
    usage
    exit 1
fi

if [ "${AREA}" == "all" ] || [ -z "${AREA}" ]; then
    make_csv elb_pre ${DATESTR}
    make_csv elb_service ${DATESTR}
    make_csv elb_service2 ${DATESTR}
else
    make_csv ${AREA} ${DATESTR}
fi

