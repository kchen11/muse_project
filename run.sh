#!/bin/bash
#!/bin/bash 

# Rules for a good bash script
# Must be run in bash or zsh shell (not sh, not dash)
# Must define the various directories.
# Must generate logs.
# Can print error when there is a programming error.
# Must have a mechanism to exit the program safely.

# 1) Set up Default Variables

current_timestamp=`date '+%Y%m%d%H%M%S'`

# 2) Set up Paths - need input, output, script, log file path 

export whoaminame=$(whoami)
export BASE_FOLDER="/home/"$whoaminame
export OUTPUT_FOLDER=$BASE_FOLDER"/project/output"
export SCRIPT_FOLDER=$BASE_FOLDER"/project/"
export LOG_FOLDER=$BASE_FOLDER"/project/log"

if [ ! -d "$LOG_FOLDER" ]; then
    mkdir -p "$LOG_FOLDER"
    echo "Directory $LOG_FOLDER created."
fi 

export SHELL_NAME=$(basename "$0" | cut -d. -f1) # cuts off extenstion of filename
export LOG_FILE=${LOG_FOLDER}/${SHELL_NAME}_${current_timestamp}.log
export OUTPUT_FOLDER=$BASE_FOLDER"/project/output"

# 3) set up log file rules

# https://stackoverflow.com/questions/49509264/explain-the-bash-command-exec-tee-log-file-21

exec > >(tee ${LOG_FILE}) 2>&1 

# 4) CD to scripts folder run py script and run script 

# cd $SCRIPT_FOLDER
source sandbox/bin/activate
echo "Start to run Python Script"
python3 $(cat config.toml | grep 'import_json' | awk -F"=" '{print $2}' | tr -d '"')

RC1=$?

if [ ${RC1} != 0 ]; then 
	echo "SCRIPT FAILED"
	echo "RETURN CODE: ${RC1}" 
    exit 1 

fi


# 7) exit sh

echo "successful"
deactivate
exit 0