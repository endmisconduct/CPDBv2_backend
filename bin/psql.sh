#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Connect to app database on production or staging using psql."
    echo ""
    echo "Usage: `basename $0` {--production|--staging}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    exit 0
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
else
    echo "Must specify either --production or --staging."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source $ENV_FILE

PGPASSWORD=$POSTGRES_APP_PASSWORD psql \
    --username $POSTGRES_APP_USER --host="$POSTGRES_HOST" --port=5432 "sslmode=require dbname=$POSTGRES_APP_DB"
