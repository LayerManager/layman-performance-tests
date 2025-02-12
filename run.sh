#!/bin/bash

set -exu

# SETUP
## prepare virtual environment
./prepare-venv.sh

## setup and start layman dev
cp ../layman/.env .layman_env_backup
./start_layman.sh
cp ../layman/.env .env
cp ../layman/src/layman/error_list.py src/error_list.py

# INSPECT PERFORMANCE
source .venv/bin/activate
set -o allexport && source .env && set +o allexport
mkdir -p tmp

## run performance script
PYTHONPATH=".:src" python run_inspect.py

## CLEANUP
deactivate

cp .layman_env_backup ../layman/.env
