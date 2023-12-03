#!/bin/bash
HOME=`dirname $0`
cd $HOME
mkdir -p ssl/certs
mkdir -p ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./ssl/private/apache-selfsigned.key -out ./ssl/certs/apache-selfsigned.crt


