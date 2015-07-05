#!/usr/bin/python


import socket
import re
import argparse
from argparse import RawTextHelpFormatter
import time
import threading
import os
import requests
import random
import atexit
from signal import signal, SIGTERM
from sys import exit
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
from urlparse import urlparse # For Python 3.0, this is urllib.urlparse

# Rewrite the HTTPAdapter to input source_address
class SourceAddressAdapter(HTTPAdapter):
    def __init__(self, source_address, **kwargs):
        self.source_address = source_address
        super(SourceAddressAdapter, self).__init__(**kwargs)
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       socket_options=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)],
                                       source_address=self.source_address,
                                       )



class Ssl3HttpAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_SSLv3)


# Rewrite the HTTPAdapter to custom the adapter
class MagicAdapter(HTTPAdapter):
    def __init__(self, source_address = ('0.0.0.0',0), ssl_version = None ,**kwargs):
        self.source_address = source_address

        #ssl_version:    
        #PROTOCOL_SSLv2
        #PROTOCOL_SSLv3
        #PROTOCOL_SSLv23
        #PROTOCOL_TLSv1
        #PROTOCOL_TLSv1_1
        #PROTOCOL_TLSv1_2
        if ssl_version == 'sslv2':
            self.ssl_version = ssl.PROTOCOL_SSLv2
        elif ssl_version == 'sslv3':
            self.ssl_version = ssl.PROTOCOL_SSLv3
        elif ssl_version == 'sslv23':
            self.ssl_version = ssl.PROTOCOL_SSLv23
        elif ssl_version == 'tlsv1':
            self.ssl_version = ssl.PROTOCOL_TLSv1
        elif ssl_version == 'tlsv1_1':
            self.ssl_version = ssl.PROTOCOL_TLSv1_1
        elif ssl_version == 'tlsv1_2':
            self.ssl_version = ssl.PROTOCOL_TLSv1_2
        else:
            self.ssl_version = None

        super(MagicAdapter, self).__init__(**kwargs)
        

    def init_poolmanager(self, connections, maxsize, block=False):
        if self.ssl_version == None:
            self.poolmanager = PoolManager(num_pools=connections,
                                           maxsize=maxsize,
                                           block=block,
                                           socket_options=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)],
                                           source_address=self.source_address,
                                           )
        else:
            self.poolmanager = PoolManager(num_pools=connections,
                                           maxsize=maxsize,
                                           block=block,
                                           socket_options=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)],
                                           source_address=self.source_address, ssl_version = self.ssl_version
                                           )




class http_request_assist():
    def __init__(self, dst_ip):
        self.dst_ip = dst_ip
        self.out_interface = os.popen('ip route get '+self.dst_ip).readlines()[0].split('dev')[1].split()[0]
        self.clean_up_cmd_list = []
        self.ip_format = re.compile('((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))')
        self.ip6_format = re.compile('\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*')

    def bind_ip(self, bind_ip ):
        # bind the IP address to out interface.
        indef_ifexist_ip = False
        indef_ip_route_get_str = os.popen('ip route get '+bind_ip).readlines()[0]
        if indef_ip_route_get_str.split()[0] == 'local':
            indef_ip_to_bind = indef_ip_route_get_str.split('local')[1].split()[0]
            if os.popen('ip add show '+self.out_interface+'|grep " '+indef_ip_to_bind+'/">/dev/null;echo $?').readlines()[0].split('\n')[0] == '0':
                indef_ifexist_ip == True
        if indef_ifexist_ip == False:
            if self.ip_format.findall(bind_ip) != []:
                # ipv4 address
                indef_run_bind = os.popen('ip address add '+bind_ip+'/32 dev '+self.out_interface).readlines()
                self.clean_up_cmd_list.append('ip address del '+bind_ip+'/32 dev '+self.out_interface)
            else:
                # ipv6 address
                indef_run_bind = os.popen('ip address add '+bind_ip+'/128 dev '+self.out_interface).readlines()
                self.clean_up_cmd_list.append('ip address del '+bind_ip+'/128 dev '+self.out_interface)

        # waiting for ipv6 tentative status over

        if_src_ipv6 = False
        if bind_ip.find(':') != -1:
            if_src_ipv6 = True


        # Wait for the tentative status of IPv6
        if if_src_ipv6 == True:
            print 'Waiting for the tentative status of new added IPv6 address over.'
            for wait in xrange(40):
                if not os.popen('ip address show '+self.out_interface+' | grep inet6 | grep tentative').readlines():
                    #break
                    return
                time.sleep(0.1)

    def clean_up(self):
        for cmd in self.clean_up_cmd_list:
            os.popen(cmd)



def http_request(dst_ip, dst_port, requests_amount = 1, interval=0, type = 'http', src_ip = None, src_port = None, url='/'):
    assistant = http_request_assist(dst_ip)
    http_session = requests.Session()
    http_session.headers.update({'User-Agent':'QA of FortiADC'})
    if src_ip != None:
        assistant.bind_ip(src_ip)
        if src_port != None:
            http_session.mount('http://', SourceAddressAdapter((src_ip, src_port)))
            http_session.mount('https://', SourceAddressAdapter((src_ip, src_port)))
        else:
            http_session.mount('http://', SourceAddressAdapter((src_ip, 0)))
            http_session.mount('https://',SourceAddressAdapter((src_ip, 0)) )
    else:
        if src_port != None:
            http_session.mount('https://',SourceAddressAdapter(('0.0.0.0', src_port)) )
            http_session.mount('http://',SourceAddressAdapter(('0.0.0.0', src_port)) )
    for i in xrange(requests_amount):
        if type == 'http':
            try:
                print '======================================'
                print 'Try to send HTTP request, the full URL is:'
                print 'http://'+dst_ip+':'+str(dst_port)+url
                print '======================================'
                http_session_get = http_session.get('http://'+dst_ip+':'+str(dst_port)+url)
            except Exception as e:
                print e
                if e[0][0] == 'Connection aborted.' and e[0][1][1] == 'Connection refused':
                    return 'Connection refused'
        elif type == 'https':
            try:
                http_session_get = http_session.get('https://'+dst_ip+':'+str(dst_port)+url) 
            except Exception as e:
                if e[0][0] == 'Connection aborted.' and e[0][1][1] == 'Connection refused':
                    return 'Connection refused'
    assistant.clean_up()
    return http_session_get



