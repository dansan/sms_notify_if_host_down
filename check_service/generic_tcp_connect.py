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
import logging

logger = logging.getLogger()


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
        logger.debug("Connecting to '%s', port %d, TCP...", self.host, self.port)
        try:
            s = socket.create_connection(address=(self.host, self.port), timeout=10)
            s.close()
            success = True
        except Exception, e:
            success = False
            logger.debug("Could not connect: %s", e)
        logger.debug("... connected: %s", success)
        return success
