#!/bin/bash

if [[ $# -lt 1 ]] ; then
	echo "USAGE: ./curate.sh <subses.csv>"
	echo "	this script clears any existing bids and curates a session of HCPMultiCenter using the hcp_heuristic.py"
	exit 1
fi

module load python/3.9

sublist=$1

subs=`cat $sublist | cut -d ',' -f1 | awk 'BEGIN { ORS = " " } { print }'`
sess=`cat $sublist | cut -d ',' -f2 | awk 'BEGIN { ORS = " " } { print }'`


cmd="fw-heudiconv-clear --project HCPMultiCenter --subject $subs --session $sess"
echo $cmd
$cmd

cmd="fw-heudiconv-curate --project HCPMultiCenter --subject $subs --session $sess --heuristic /project/ftdc_hcp/fmriBids/scripts/heuristic_hcp.py"
echo $cmd
$cmd
