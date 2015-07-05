#!/usr/bin/python

import time

class output():
    def __init__(self, log_file = None):
        if log_file == None:
            self.log_file_name = 'log_'+'_'.join(time.ctime().split()).replace(':','_')+'.txt'
        else:
            self.log_file_name = log_file

    def show(self, content):
        '''Print the content with time.'''
        final_content = '['+time.ctime()+'] '+content
        print final_content 

    def warn(self, content, log = False):
        '''Warn the message'''
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++'
        self.show(content)
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++'
        if log == True:
            self.record('+++++++++++++++++++++++++++++++++++++++++++++++++++', no_time = True)
            self.record(content)
            self.record('+++++++++++++++++++++++++++++++++++++++++++++++++++', no_time = True)

    def dump(self, content):
        '''Print the content on the screen and write the content to the log file.'''
        self.show(content)
        self.record(content)

    def record(self, content, no_time = False):
        '''Write logs to log file.'''
        if no_time == True:
            final_content = content
        else:
            final_content = '['+time.ctime()+'] '+content
        file_object = open(self.log_file_name, 'a')
        file_object.write(final_content+'\n')
        file_object.close()


class ip_net():
    '''Handle IP address and subnet'''
    def __init__(self):
        '''Init the parameters'''


    def if_ip(self, ip_address, format='ipv4'):
        '''If the ip_string is legal IP format'''
        import socket
        if format == 'ipv4':
            try:
                addr= socket.inet_pton(socket.AF_INET, ip_address)
            except AttributeError: # no inet_pton here, sorry
                try:
                    addr= socket.inet_aton(ip_address)
                except socket.error:
                    return False
                return ip_address.count('.') == 3
            except socket.error: # not a valid address
                return False
            return True
        elif format == 'ipv6':
            try:
                addr= socket.inet_pton(socket.AF_INET6, ip_address)
            except socket.error: # not a valid address
                return False
            return True

    def ipv6_full_format(self, ip6_address):
        '''Add zero to ipv6 address to fulfill IPv6 full format'''
        if ip6_address.find('::') != -1:
            # contains '::'
            if ip6_address.find('::') == 0:
                # ::x
                zero_count = 8-len(ip6_address.split('::')[1].split(':'))
                ip6_address = '0:'*zero_count+ip6_address.split('::')[1]
            elif ip6_address.find('::') == len(ip6_address)-2:
                # x::
                zero_count = 8-len(ip6_address.split('::')[0].split(':'))
                ip6_address = ip6_address.split('::')[0]+':0'*5
            else:
                # x::x
                zero_count = 9-len(ip6_address.split(':'))
                ip6_address = ip6_address.split('::')[0]+':'+'0:'*zero_count+ip6_address.split('::')[1]
        return ip6_address

    def ip_to_int(self, ip_address):
        '''Convert ip_address to int number'''
        if ip_address.find(':') == -1:
            #IPv4
            ip_address_list = ip_address.split('.') #['192', '168', '10', '1']
            for seq in xrange(0,4):
                ip_address_list[seq] = bin(int(ip_address_list[seq])).replace('0b','')
                zero_count = 8-len(ip_address_list[seq])
                ip_address_list[seq] = '0'*zero_count+ip_address_list[seq]
            #ip_address_list --> ['11000000', '10101000', '00001010', '00000001']
            return int(''.join(ip_address_list),2)
        else:
            #IPv6
            ip_address_list = self.ipv6_full_format(ip_address).split(':')
            # ip_address_list --> ['2001', '0', '0', '0', '10', '76', '10', '1']
            for seq in xrange(0,8):
                ip_address_list[seq] = bin(int(ip_address_list[seq],16)).replace('0b','')
                zero_count = 16-len(ip_address_list[seq])
                ip_address_list[seq] = '0'*zero_count+ip_address_list[seq]
            # ip_address_list --> ['0010000000000001', '0000000000000000', '0000000000000000', '0000000000000000', '0000000000010000', '0000000001110110', '0000000000010000', '0000000000000001']
            return int(''.join(ip_address_list),2)

    def int_to_ip(self, number, format='ipv4'):
        '''Convert int number to IP address'''
        # number is int
        if format == 'ipv4':
            ip_address = bin(number).replace('0b','')
            zero_count = 32-len(ip_address)
            ip_address = '0'*zero_count+ip_address
            return str(int(ip_address[0:8],2))+'.'+str(int(ip_address[8:16],2))+'.'+str(int(ip_address[16:24],2))+'.'+str(int(ip_address[24:32],2))
        elif format == 'ipv6':
            ip_address = bin(number).replace('0b','')
            zero_count = 128-len(ip_address)
            ip_address = '0'*zero_count+ip_address
            return (hex(int(ip_address[0:16],2)).replace('0x','')
                    +':'+hex(int(ip_address[16:32],2)).replace('0x','')
                    +':'+hex(int(ip_address[32:48],2)).replace('0x','')
                    +':'+hex(int(ip_address[48:64],2)).replace('0x','')
                    +':'+hex(int(ip_address[64:80],2)).replace('0x','')
                    +':'+hex(int(ip_address[80:96],2)).replace('0x','')
                    +':'+hex(int(ip_address[96:112],2)).replace('0x','')
                    +':'+hex(int(ip_address[112:128],2)) .replace('0x','')
                    )

    def ip_plus(self, ip_address, number=1):
        '''Return ip_address+number'''
        if ip_address.find(':') == -1:
            # IPv4
            return self.int_to_ip(self.ip_to_int(ip_address)+number, format='ipv4')

        else:
            # IPv6
            return self.int_to_ip(self.ip_to_int(ip_address)+number, format='ipv6')

    def ip_minus(self, ip_address, number=1):
        '''Return ip_address-number'''
        if ip_address.find(':') == -1:
            # IPv4
            return self.int_to_ip(self.ip_to_int(ip_address)-number, format='ipv4')
        else:
            # IPv6
            return self.int_to_ip(self.ip_to_int(ip_address)-number, format='ipv6')

    def min_ip(self, ip_address1, ip_address2):
        '''Return min one of ip_address1 and ip_address2'''
        if ip_address1.find(':') == -1 and ip_address1.find(':') == -1:
            # ip1 and ip2 are IPv4
            return self.int_to_ip(min(self.ip_to_int(ip_address1), self.ip_to_int(ip_address2)), format='ipv4')
        elif ip_address1.find(':') != -1 and ip_address1.find(':') != -1:
            # ip1 and ip2 are IPv6
            return self.int_to_ip(min(self.ip_to_int(ip_address1), self.ip_to_int(ip_address2)), format='ipv6')
        else:
            return None

    def max_ip(self, ip_address1, ip_address2):
        '''Return max one of ip_address1 and ip_address2'''
        if ip_address1.find(':') == -1 and ip_address1.find(':') == -1:
            # ip1 and ip2 are IPv4
            return self.int_to_ip(max(self.ip_to_int(ip_address1), self.ip_to_int(ip_address2)), format='ipv4')
        elif ip_address1.find(':') != -1 and ip_address1.find(':') != -1:
            # ip1 and ip2 are IPv6
            return self.int_to_ip(max(self.ip_to_int(ip_address1), self.ip_to_int(ip_address2)), format='ipv6')
        else:
            return None

    def ip_range(self, ip_range):
        '''Return a range of IP address list'''
        # ip_range format: 10.76.1.1,10.78.1.10-10.78.1.20,110.1.1.1
        ip_range_result = []
        ip_range_list = ip_range.split(',')
        for infor in ip_range_list:
            if infor.find('-') == -1:
                ip_range_result.append(infor)
            else:
                start_ip = self.min_ip(infor.split('-')[0],infor.split('-')[1])
                end_ip =  self.max_ip(infor.split('-')[0],infor.split('-')[1])
                if start_ip == None or end_ip == None:
                    pass
                else:
                    while 1:
                        ip_range_result.append(start_ip)
                        if start_ip == end_ip:
                            break
                        start_ip = self.ip_plus(start_ip)
        return ip_range_result

    def ip_random(self, ip_prefix, count):
        '''Return a count of random IP address list'''
        import random
        random_ip_list = []
        if ip_prefix.find(':') == -1:
            # IPv4
            for infor in xrange(count):
                random_ip_list.append(self.int_to_ip(random.randint(self.ip_to_int(self.ip_subnet(ip_prefix)[0]),self.ip_to_int(self.ip_subnet(ip_prefix)[1]))))
        else:
            # IPv6
            for infor in xrange(count):
                random_ip_list.append(self.int_to_ip(random.randint(self.ip_to_int(self.ip_subnet(ip_prefix)[0]),self.ip_to_int(self.ip_subnet(ip_prefix)[1])), format='ipv6'))
        return random_ip_list
   
    def if_ip_in_iprange(self, ip_address, ip_range):
        '''If the ip_address is in ip_range'''
        # ip_range format: 10.76.1.1,10.78.1.10-10.78.1.20,110.1.1.1
        if_in_range = False
        ip_range_list = ip_range.split(',')
        for infor in ip_range_list:
            if infor.find('-') == -1:
                if infor == ip_address :
                    if_in_range = True
                    break
            else:
                first_ip_int = self.ip_to_int(infor.split('-')[0])
                second_ip_int = self.ip_to_int(infor.split('-')[1])
                ip_address_int = self.ip_to_int(ip_address)
                if ip_address_int <= max(first_ip_int,second_ip_int) and ip_address_int >= min(first_ip_int,second_ip_int):
                    if_in_range = True
                    break
        return if_in_range

    def if_ip_in_subnet(self, ip_address, ip_prefix):
        '''If the ip_address is in ip_prefix'''
        ip_address_int = self.ip_to_int(ip_address)
        subnet_tuple = self.ip_subnet(ip_prefix)
        if ip_address_int <= self.ip_to_int(subnet_tuple[1]) and ip_address_int >= self.ip_to_int(subnet_tuple[0]):
            return True
        else:
            return False

    def prefix_to_mask(self, prefix_number):
        '''Convert prefix_number to subnet mask'''
        # prefix_number is int, only for IPv4
        zero_count = 32-prefix_number
        return self.int_to_ip(int('1'*prefix_number+'0'*zero_count,2), format='ipv4')

    def mask_to_prefix(self, subnet_mask):
        '''Convert subnet mask to prefix number'''
        mask_bin = bin(self.ip_to_int(subnet_mask)).replace('0b','')
        zero_count = 32-len(mask_bin)
        mask_bin = '0'*zero_count+mask_bin
        mask_bin_list = list(mask_bin)
        for infor in xrange(32):
            if mask_bin_list[infor] == '0':
                return infor

    def ip_subnet(self, ip_prefix):
        '''Return the subnet IP and broadcast IP of ip_prefix'''
        ip_string = ip_prefix.split('/')[0]
        prefix_num = int(ip_prefix.split('/')[1])
        if ip_string.find(':') == -1:
            # IPv4
            ip_address_list = ip_string.split('.') #['192', '168', '10', '1']
            for seq in xrange(0,4):
                ip_address_list[seq] = bin(int(ip_address_list[seq])).replace('0b','')
                zero_count = 8-len(ip_address_list[seq])
                ip_address_list[seq] = '0'*zero_count+ip_address_list[seq]
            zero_count = 32-prefix_num
            return self.int_to_ip(int(''.join(ip_address_list)[0:prefix_num]+'0'*zero_count,2)), self.int_to_ip(int(''.join(ip_address_list)[0:prefix_num]+'1'*zero_count,2))
        else:
            # IPv6
            ip_address_list = self.ipv6_full_format(ip_string).split(':')
            # ip_address_list --> ['2001', '0', '0', '0', '10', '76', '10', '1']
            for seq in xrange(0,8):
                ip_address_list[seq] = bin(int(ip_address_list[seq],16)).replace('0b','')
                zero_count = 16-len(ip_address_list[seq])
                ip_address_list[seq] = '0'*zero_count+ip_address_list[seq]
            zero_count = 128-prefix_num
            return self.int_to_ip(int(''.join(ip_address_list)[0:prefix_num]+'0'*zero_count,2), format='ipv6'), self.int_to_ip(int(''.join(ip_address_list)[0:prefix_num]+'1'*zero_count,2),format='ipv6')






