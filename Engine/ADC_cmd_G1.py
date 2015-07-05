#!/usr/bin/python

import re
import telnetlib
import os



class telnet_ADC():
    '''Handle telnet'''
    def __init__(self):
        '''Init parameters'''
        pass

    def login(self, host, username = 'admin', password = '', 
              telnet_port=23, login_msg='login: ', password_msg='Password: ', finish_msg='#', 
              **kwargs):
        '''Login the device'''
        self.login_host = host
        self.login_username = username
        self.login_password = password
        self.login_telnet_port = telnet_port
        self.login_login_msg = login_msg
        self.login_password_msg = password_msg
        self.login_finish_msg = finish_msg
        print 'Try to login the device "'+host+'" .'
        try:
            self.telnet_obj = telnetlib.Telnet(host, telnet_port)
            self.telnet_obj.read_until(login_msg)
            self.telnet_obj.write(username + '\n')
            self.telnet_obj.read_until(password_msg)
            self.telnet_obj.write(password + '\n')
            self.telnet_obj.read_until(finish_msg)
            self.telnet_obj.write('\n')
            self.telnet_obj.read_until(finish_msg)
            print 'Login device "'+host+'" OK!'
            return True
        except:
            # If login failed, return False
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'Login device "'+host+'" failed.'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            return False

    def run_cmd(self, cmd, show_info = True, line_break = True, until_msg='#', relogin = False):
        '''Run cmd in line'''
        for in_times in xrange(3):
            try:
                if line_break == True:
                    self.telnet_obj.write(cmd + '\n')
                else:
                    self.telnet_obj.write(cmd)
                result_msg = self.telnet_obj.read_until(until_msg, 20)
                break
            except:
                if relogin == True:
                    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    print 'Running the command ['+cmd+'] failed.'
                    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    print 'Try to relogin the device "'+self.login_host+'" .'
                    try:
                        self.login(self.login_host, username = self.login_username, 
                                   password = self.login_password, telnet_port = self.login_telnet_port, 
                                   login_msg = self.login_login_msg, password_msg = self.login_password_msg, 
                                   finish_msg = self.login_finish_msg)
                        print 'Relogin OK!'
                    except:
                        pass
                    continue
                else:
                    break
        if show_info == True:
            print result_msg
        return result_msg

    def run_file(self, cmd_file, until_msg='#' ):
        '''Run the command file.
           The content after "#" will be marked as comment in every line.
        '''
        if os.path.isfile(cmd_file) == False:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'The file "'+cmd_file+'" does not exist. '
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            return False
        print 'Try to open the config file "'+cmd_file+'" .'
        my_file = open(cmd_file)
        file_content = my_file.read()
        my_file.close()
        print 'Read config file "'+cmd_file+'" OK.'
        

        comment_re = re.compile('#.*$')
        cmd_line_list = file_content.split('\n')
        for cmd_line in cmd_line_list:
            to_run = cmd_line
            comment_find_list = comment_re.findall(cmd_line)
            if comment_find_list != []:
                to_run = cmd_line.replace(comment_find_list[0], '')
                if to_run == '':
                    continue
            self.run_cmd(to_run)
        print 'The config of "'+cmd_file+" has been uploaded to device "+self.login_host+'".'

    def back_to_start_cmd(self):
        '''Enter the start mode of CLI.'''
        self.cmd_mode_checker = re.compile('\(.*\) #')
        run_result = self.run_cmd('', show_info = False)
        last_line = run_result.split('\r\n')[1]
        check_result = self.cmd_mode_checker.findall(last_line) 
        if check_result != []:
            for i in xrange(10):
                end_result = self.run_cmd('end', show_info = False)
                end_result_list = end_result.split('\r\n')
                n_last_line = end_result_list[len(end_result_list)-1]
                n_check_result = self.cmd_mode_checker.findall(n_last_line)
                if n_check_result == []:
                    break

    def enter_vdom(self, vdom_name, show_info = False):
        '''Enter the related vdom'''
        self.back_to_start_cmd()
        self.run_cmd('config vdom', show_info = show_info)
        self.run_cmd('edit '+vdom_name, show_info = show_info)


    def config(self, module_name, entry_name, option, value):
        '''Set option with value in the entry like VS, profile, persistence.
           module_name should be like : load-balance virtual-server
                                        load_balance profile
                                        load_balance persistence

           entry_name should be like: SLB1_VS_app2_L7
        '''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.run_cmd('config vdom')
            self.run_cmd('edit '+self.vdom)

        self.run_cmd('config '+module_name)
        self.run_cmd('edit '+entry_name)
        self.run_cmd('set '+option+' '+value)
        self.run_cmd('end')

        self.back_to_start_cmd()

    def set_entry_value_list(self, module_name, entry_name, value_list):
        '''Set option with value list
           value_list like: [('type','l7-load-balance'),('load-balance-profile', 'http')]
        '''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.run_cmd('config vdom')
            self.run_cmd('edit '+self.vdom)
        
        self.run_cmd('config '+module_name)
        self.run_cmd('edit '+entry_name)
        for option_value in value_list:
            self.run_cmd('set '+option_value[0]+' '+option_value[1])
        self.run_cmd('end')
            

        self.back_to_start_cmd()


    def get_entry_list(self, module_name):
        '''Get all the available entry list.
           module_name should be like : load-balance virtual-server
                                        load_balance profile
                                        load_balance persistence
        '''
        self.back_to_start_cmd()

        if self.vdom == None:
            pass
        else:
            self.run_cmd('config vdom', show_info = False)
            self.run_cmd('edit '+self.vdom, show_info = False)

        get_vs_list_result = self.run_cmd('get '+module_name, show_info = False)
        vs_list = get_vs_list_result.split('\r\n')
        del vs_list[0]
        del vs_list[len(vs_list)-1]
        del vs_list[len(vs_list)-1]
        vs_name_list = []
        for in_vs in vs_list:
            vs_name_list.append(in_vs.replace('== [ ', '').replace(' ]', ''))
        if self.vdom != None:
            self.back_to_start_cmd()

        return vs_name_list

    def get_entry_option_available_value(self, module_name, entry_name):
        '''Return the entry option available value in dic type'''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        self.run_cmd('config '+module_name, show_info = False)
        self.run_cmd('edit '+entry_name, show_info = False)
        option_result = self.run_cmd('set ?', show_info = False, line_break = False)
        option_list_1 = option_result.split('\r\n')
        self.run_cmd('', show_info = False)
        del option_list_1[0]
        del option_list_1[len(option_list_1)-1]
        del option_list_1[len(option_list_1)-1]
        option_list = []
        for in_option in option_list_1:
            option_list.append(in_option.split()[0].replace('*',''))

        option_value_dic = {}
        cmd_1_line_checker = re.compile('^ <.*> ') # Match ' <datasource>  '
        for in_option in option_list:
            value_result = self.run_cmd('set '+in_option+' ?', show_info = False, line_break = False)
            self.run_cmd('', show_info = False)
            value_list_1 = value_result.split('\r\n')
            del value_list_1[0]
            del value_list_1[len(value_list_1)-1]
            del value_list_1[len(value_list_1)-1]
            if cmd_1_line_checker.findall(value_list_1[0]) != []:
                del value_list_1[0]
            if value_list_1 == []:
                option_value_dic[in_option] = None
            else:
                available_value_list = []
                for i in value_list_1:
                    available_value_list.append(i.split()[0])
                option_value_dic[in_option] = available_value_list
        self.back_to_start_cmd()
        return option_value_dic

    def get_entry_value(self, module_name, entry_name):
        '''Return all the value of VS in dictionary type.
           Run command "get load-balance virtual-server vs1" to get the value.
           Notice: Predefined entry can't be shown. 
        '''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        run_result = self.run_cmd('get '+module_name+' '+entry_name, show_info = False)
        result_list_1 = run_result.split('\r\n')
        del result_list_1[0]
        del result_list_1[len(result_list_1)-1]
        del result_list_1[len(result_list_1)-1]
        vs_value_dic = {}
        for in_option in result_list_1:
            value_list = in_option.split()
            real_option = value_list[0]
            real_value = value_list[len(value_list)-1]
            if real_option == '==' and real_value == ']':
                continue
            if real_value == ':':
                vs_value_dic[real_option] = None
            else:
                vs_value_dic[real_option] = real_value
        self.back_to_start_cmd()
        return vs_value_dic


    def close(self):
        '''Close the telnet TCP connection'''
        self.telnet_obj.close()



class load_balance_vs(telnet_ADC):
    def __init__(self, host,
                 username = 'admin', password = '', telnet_port=23,
                 vdom = None,
                 login_msg='login: ', password_msg='Password: ', finish_msg='#',
                 **kwargs):
        self.vdom = vdom
        self.login(host, username = 'admin', password = '',
                   telnet_port=23, login_msg='login: ', password_msg='Password: ', finish_msg='#')

    def set_value(self, vs_name, option, value):
        '''Set the option with value in the vs.'''

        self.config('load-balance virtual-server', vs_name, option, value)

    def set_value_list(self, vs_name, value_list):
        '''Set the option with value list as sequence.
           value_list like [('type','l7-load-balance'),('load-balance-profile', 'http')]
        '''
        self.set_entry_value_list('load-balance virtual-server', vs_name, value_list)
        

    def get_vs_list(self):
        '''Return the vs item list.'''
        return self.get_entry_list('load-balance virtual-server')


    def get_vs_option_available_value(self, vs_name):
        '''Return the vs option available value in dic type'''
        return self.get_entry_option_available_value('load-balance virtual-server', vs_name)

    def get_vs_value(self, vs_name):
        '''Return all the value of vs in dictionary type.'''
        return self.get_entry_value('load-balance virtual-server', vs_name)


class load_balance_profile(telnet_ADC):
    def __init__(self, host,
                 username = 'admin', password = '', telnet_port=23,
                 vdom = None,
                 login_msg='login: ', password_msg='Password: ', finish_msg='#',
                 **kwargs):
        self.vdom = vdom
        self.login(host, username = 'admin', password = '',
                   telnet_port=23, login_msg='login: ', password_msg='Password: ', finish_msg='#')

    def set_value(self, profile_name, option, value):
        '''Set the option with value in the profile.'''

        self.config('load_balance profile', profile_name, option, value)

    def get_profile_list(self):
        '''Return the profile item list.'''
        return self.get_entry_list('load-balance profile')


    def get_profile_option_available_value(self, profile_name):
        '''Return the profile option available value in dic type'''
        return self.get_entry_option_available_value('load-balance profile', profile_name)

    def get_profile_value(self, profile_name):
        '''Return all the value of profile in dictionary type.'''
        return self.get_entry_value('load-balance profile', profile_name)

    def get_profile_type_list(self, profile_type):
        '''
            Return the profile list as of profile_type, 
            profile_type should be: 
            l2-load-balance, l7-load-balance, l4-load-balance, 
            lvs, haproxy, http, ssl, tcp, udp, predefined,
            geoip-list, whitelist
        '''
        if profile_type == 'predefined':
            return ['LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_RADIUS', 'LB_PROF_TCPS', 'LB_PROF_TURBOHTTP', 'LB_PROF_TCP', 'LB_PROF_UDP', 'LB_PROF_FTP']
        l7_type_avai = ['http', 'https', 'radius', 'tcps', 'turbohttp']
        l4_type_avai = ['tcp', 'udp', 'ftp']
        l2_type_avai = ['http', 'https', 'tcp', 'tcps']
        lvs_type_avai = ['tcp', 'udp', 'ftp', 'turbohttp']
        haproxy_type_avai = ['http', 'https', 'tcps']
        http_type_avai = ['http', 'https', 'tcp', 'turbohttp', 'tcps']
        tcp_type_avai = ['http', 'https', 'tcps', 'turbohttp', 'ftp', 'tcp']
        udp_type_avai = ['radius', 'udp']
        ssl_type_avai = ['https', 'tcps'] 

        l7_predefined_list = ['LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_RADIUS', 'LB_PROF_TCPS', 'LB_PROF_TURBOHTTP']
        l4_predefined_list = ['LB_PROF_TCP', 'LB_PROF_UDP', 'LB_PROF_FTP']
        l2_predefined_list = ['LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_TCP', 'LB_PROF_TCPS']
        lvs_predefined_list = ['LB_PROF_TCP', 'LB_PROF_UDP', 'LB_PROF_FTP', 'LB_PROF_TURBOHTTP']
        haproxy_predefined_list = ['LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_TCPS']
        http_predefined_list = ['LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_TCPS', 'LB_PROF_TURBOHTTP', 'LB_PROF_TCP']
        tcp_predefined_list = [ 'LB_PROF_HTTP', 'LB_PROF_HTTPS', 'LB_PROF_TCPS', 'LB_PROF_TURBOHTTP', 'LB_PROF_TCP', 'LB_PROF_FTP' ]
        udp_predefined_list = ['LB_PROF_RADIUS', 'LB_PROF_UDP']
        ssl_predefined_list = ['LB_PROF_HTTPS', 'LB_PROF_TCPS']


        result_list = []
        if profile_type == 'l7-load-balance':
            check_avai_list = l7_type_avai
            result_list = l7_predefined_list
        elif profile_type == 'l4-load-balance':
            check_avai_list = l4_type_avai
            result_list = l4_predefined_list
        elif profile_type == 'l2-load-balance':
            check_avai_list = l2_type_avai
            result_list = l2_predefined_list
        elif profile_type == 'lvs':
            check_avai_list = lvs_type_avai
            result_list = lvs_predefined_list
        elif profile_type == 'haproxy':
            check_avai_list = haproxy_type_avai
            result_list = haproxy_predefined_list
        elif profile_type == 'http':
            check_avai_list = http_type_avai
            result_list = http_predefined_list
        elif profile_type == 'udp':
            check_avai_list = udp_type_avai
            result_list = udp_predefined_list
        elif profile_type == 'ssl':
            check_avai_list = ssl_type_avai
            result_list = ssl_predefined_list
        elif profile_type == 'tcp':
            check_avai_list = tcp_type_avai
            result_list = tcp_predefined_list
        

        for i in self.get_profile_list():
            if i.find('LB_PROF_') != -1:
                continue
            if profile_type == 'geoip-list':
                if self.get_profile_value(i)['geoip-list'] != None:
                    result_list.append(i)

            elif profile_type == 'whitelist':
                if self.get_profile_value(i)['whitelist'] != None:
                    result_list.append(i)

            else:
                current_type = self.get_profile_value(i)['type']
                if current_type in check_avai_list:
                    result_list.append(i)

        return result_list


class load_balance_persistence(telnet_ADC):
    def __init__(self, host,
                 username = 'admin', password = '', telnet_port=23,
                 vdom = None,
                 login_msg='login: ', password_msg='Password: ', finish_msg='#',
                 **kwargs):
        self.vdom = vdom
        self.login(host, username = 'admin', password = '',
                   telnet_port=23, login_msg='login: ', password_msg='Password: ', finish_msg='#')


    def set_value(self, persistence_name, option, value):
        '''Set the option with value in the persistence.'''

        self.config('load_balance persistence', persistence_name, option, value)

    def get_persistence_list(self):
        '''Return the persistence item list.'''
        return self.get_entry_list('load-balance persistence')

    def get_persistence_option_available_value(self, persistence_name):
        '''Return the persistence option available value in dic type'''
        return self.get_entry_option_available_value('load-balance persistence', persistence_name)

    def get_persistence_value(self, persistence_name):
        '''Return all the value of persistence in dictionary type.'''
        return self.get_entry_value('load-balance persistence', persistence_name)

    def get_persistence_type_list(self, persistence_type):
        '''
            Return the list of persistence type.
            persistence_type should be:
            l2-load-balance, l7-load-balance, l4-load-balance, 
        '''
        pass



class load_balance_pool(telnet_ADC):
    def __init__(self, host,
                 username = 'admin', password = '', telnet_port=23,
                 vdom = None,
                 login_msg='login: ', password_msg='Password: ', finish_msg='#',
                 **kwargs):
        self.vdom = vdom
        self.login(host, username = 'admin', password = '',
                   telnet_port=23, login_msg='login: ', password_msg='Password: ', finish_msg='#')

    def set_pool_value(self, pool_name, option, value):
        '''Set the option with value in the pool.'''
        self.config('load_balance pool', pool_name, option, value)

    def set_pool_member_value(self, pool_name, pool_member_id, option, value):
        '''Set the option with value in the pool member.'''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        self.run_cmd('config load-balance pool')
        self.run_cmd('edit '+pool_name)
        self.run_cmd('config pool_member')
        self.run_cmd('edit '+pool_member_id)
        self.run_cmd('set '+option+' '+value)
        self.run_cmd('end')
        self.run_cmd('end')
        self.back_to_start_cmd()

    def get_pool_list(self):
        '''Return the pool item list.'''
        return self.get_entry_list('load-balance pool')

    def get_pool_member_list(self, pool_name):
        '''Return the pool member list of the pool.'''

        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        get_pool_list_result = self.run_cmd('get load-balance pool '+pool_name, show_info = False)
        pool_list = get_pool_list_result.split('\r\n')
        del pool_list[0]
        del pool_list[len(pool_list)-1]
        del pool_list[len(pool_list)-1]
        pool_member_checker = re.compile('== \[ .* \]')  # Match '== [ 1 ]'
        pool_member_list = []
        for in_pool in pool_list:
            if pool_member_checker.findall(in_pool) != []:
                pool_member_list.append(in_pool.replace('== [ ','').replace(' ]',''))
        if self.vdom != None:
            self.back_to_start_cmd()

        return pool_member_list

    def get_pool_option_available_value(self, pool_name):
        '''Return the pool option available value in dic type'''
        return self.get_entry_option_available_value('load-balance pool', pool_name)


    def get_pool_member_option_available_value(self, pool_name, pool_member_id):
        '''Return the entry option available value in dic type'''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        self.run_cmd('config load-balance pool', show_info = False)
        self.run_cmd('edit '+pool_name, show_info = False)
        self.run_cmd('config pool_member ', show_info = False)
        self.run_cmd('edit '+str(pool_member_id), show_info = False)
        
        
        option_result = self.run_cmd('set ?', show_info = False, line_break = False)
        option_list_1 = option_result.split('\r\n')
        self.run_cmd('', show_info = False)
        del option_list_1[0]
        del option_list_1[len(option_list_1)-1]
        del option_list_1[len(option_list_1)-1]
        option_list = []
        for in_option in option_list_1:
            option_list.append(in_option.split()[0].replace('*',''))

        option_value_dic = {}
        cmd_1_line_checker = re.compile('^ <.*> ') # Match ' <datasource>  '
        for in_option in option_list:
            value_result = self.run_cmd('set '+in_option+' ?', show_info = False, line_break = False)
            self.run_cmd('', show_info = False)
            value_list_1 = value_result.split('\r\n')
            del value_list_1[0]
            del value_list_1[len(value_list_1)-1]
            del value_list_1[len(value_list_1)-1]
            if cmd_1_line_checker.findall(value_list_1[0]) != []:
                del value_list_1[0]
            if value_list_1 == []:
                option_value_dic[in_option] = None
            else:
                available_value_list = []
                for i in value_list_1:
                    available_value_list.append(i.split()[0])
                option_value_dic[in_option] = available_value_list
        self.back_to_start_cmd()

        option_value_dic['ip'] = None
        option_value_dic['ip6'] = None
        return option_value_dic


    def get_pool_value(self, pool_name):
        '''Return all the value of pool in dictionary type.'''
        return self.get_entry_value('load-balance pool', pool_name)


    def get_pool_member_value(self, pool_name, pool_member_id):
        '''Return all the value of pool member.'''
        self.back_to_start_cmd()
        if self.vdom != None:
            self.enter_vdom(self.vdom)

        self.run_cmd('config load-balance pool', show_info = False)
        self.run_cmd('edit '+pool_name, show_info = False)
        self.run_cmd('config pool_member', show_info = False)
        self.run_cmd('edit '+pool_member_id, show_info = False)
        run_result = self.run_cmd('get', show_info = False)


        result_list_1 = run_result.split('\r\n')
        del result_list_1[0]
        del result_list_1[len(result_list_1)-1]
        del result_list_1[len(result_list_1)-1]
        vs_value_dic = {}
        for in_option in result_list_1:
            value_list = in_option.split()
            real_option = value_list[0]
            real_value = value_list[len(value_list)-1]
            if real_option == '==' and real_value == ']':
                continue
            if real_value == ':':
                vs_value_dic[real_option] = None
            else:
                vs_value_dic[real_option] = real_value
        self.back_to_start_cmd()
        return vs_value_dic







if __name__ == '__main__':
    print 'OK'







