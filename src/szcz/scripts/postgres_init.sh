#!/bin/bash
script_dir="$( cd "$( dirname "$0" )" && pwd )"
dropdb szcz
createdb szcz
psql szcz < $script_dir/mirror.sql
