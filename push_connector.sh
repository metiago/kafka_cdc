#!/bin/sh

curl -s -XDELETE "http://localhost:8083/connectors/mysql-connector"

sleep 1

curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors -d @connectors/mysql-source.json

sleep 1

curl -X POST http://localhost:8083/connectors/mysql-connector/restart

sleep 2

clear

curl -X GET http://localhost:8083/connectors/mysql-connector/status
