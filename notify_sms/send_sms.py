# encoding: utf-8
'''
@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
'''


class Send_SMS(object):
    '''
    Base class for SMS sending function.
    '''

    def __init__(self, username, password):
        '''
        :param str destination: phone number (RFC3824), starting with country code (e.g. 4917712345678)
        :param str message: the message
        :raises Exception: if there was an error connecting (wrong username/password)
        '''
        self.username = username
        self.password = password

    def send(self, destination, message):
        '''
        This function can be called multiple times.

        :param str destination: phone number (RFC3824), starting with country code (e.g. 4917712345678)
        :param str message: the message, max 160 characters
        :return: True if success
        :rtype: bool
        :raises Exception: if there was an error sending the message (wrong phone number)
        '''
        raise NotImplementedError
