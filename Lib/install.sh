#!/bin/bash


yum -y install libffi-devel libssl-devel python-devel

tar -zxvf ndg_httpsclient-0.3.2.tar.gz && cd ndg_httpsclient-0.3.2 && python setup.py install 

cd ..

tar -zxvf pyasn1-0.1.7.tar.gz && cd pyasn1-0.1.7 && python setup.py install

cd ..

tar -zxvf pyopenssl_0.14.tar.gz && cd pyopenssl-0.14 && python setup.py install --user




