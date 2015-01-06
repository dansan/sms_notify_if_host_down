# encoding: utf-8
'''
generic_tcp_connect -- trys to connect toa TCP socket

@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
'''

from check_service import Check_service
import socket


class Generic_TCP_connect(Check_service):
    '''
    trys to connect to a TCP socket
    '''
    def run(self):
        '''
        Runs the check, raises no exception.

        :return: True if success
        :rtype: bool
        '''
        if self.verbose > 0:
            print("Connecting to '%s', port %d, TCP..." % (self.host, self.port))
        try:
            s = socket.create_connection(address=(self.host, self.port), timeout=10)
            s.close()
            success = True
        except Exception, e:
            success = False
            if self.verbose > 0:
                print("Could not connect: %s" % str(e))
        if self.verbose > 0:
            print("... connected: %s" % str(success))
        return success
