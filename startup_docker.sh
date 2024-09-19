#!/bin/bash

# ALIASES
echo "alias rifg='python /workdir/tasks_run/scripts/rifg_task.py'" >> ~/.bashrc

echo "alias data='cd /workdir/tasks_run/data/'" >> ~/.bashrc

echo "alias logs='cd /workdir/tasks_run/data/logs'" >> ~/.bashrc

echo "alias scripts='cd /workdir/tasks_run/scripts'" >> ~/.bashrc

echo "alias samba='cd /workdir/tasks_run/data/sambashare'" >> ~/.bashrc

echo "alias mock='python /workdir/tasks_run/scripts/other/mock_mri_file_production.py'" >> ~/.bashrc

echo "alias nfb='python /workdir/tasks_run/scripts/nf_calc_MW.py'" >> ~/.bashrc

echo "alias msit='python /workdir/tasks_run/scripts/MSIT_NF_latest.py'" >> ~/.bashrc

echo "alias testdir='cd /workdir/tasks_run/data/sambashare/test_dir'" >> ~/.bashrc

echo "alias clear_testdir='rm -rf /workdir/tasks_run/data/sambashare/test_dir/*'" >> ~/.bashrc

echo "e3() {
cd /workdir/
./ssh_e3.sh
}" >> ~/.bashrc

source ~/.bashrc

echo "Hello, $USERNAME. Docker container setup is all set. Type 'alias' to available commands."
exec "$@"
