#!/bin/bash

#后台停止Flask应用执行脚本

cd `dirname $0`/..
export BASE_DIR=`pwd`
pid=`ps ax | grep -i 'app.py' | grep python3 | grep ${BASE_DIR} | grep -v grep | awk '{print $1}'`
if [ -z "$pid" ]; then
    echo "No Flask application is currently running."
    exit -1
fi

echo "The Flask application ($pid) is currently running..."

kill ${pid}

echo "Sent shutdown request to Flask application ($pid)."
