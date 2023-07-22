#!/bin/bash
#后台运行Flask应用执行脚本

cd `dirname $0`/..
export BASE_DIR=`pwd`
echo $BASE_DIR

# check the nohup.out log output file
if [ ! -f "${BASE_DIR}/nohup.out" ]; then
  touch "${BASE_DIR}/nohup.out"
  echo "create file  ${BASE_DIR}/nohup.out"
fi

nohup python3 "${BASE_DIR}/app.py" > "${BASE_DIR}/nohup.out" 2>&1 &

echo "Flask application is starting，you can check the ${BASE_DIR}/nohup.out"
