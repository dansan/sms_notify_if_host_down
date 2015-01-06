# encoding: utf-8
'''
@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
'''


class Check_service(object):
    '''
    Base class for service check classes.
    '''

    def __init__(self, host, port, protocol="TCP", verbose=0):
        '''
        :param str host: FQDN or IP
        :param integer port: port
        :param integer verbose: print debug information to stdout
        :param str protocol: protocol to use (default is TCP)
        '''
        self.host = host
        self.port = port
        self.protocol = protocol
        self.verbose = verbose

    def run(self):
        '''
        Runs the check, raises no exception.

        :return: True if success
        :rtype: bool
        '''
        raise NotImplementedError
