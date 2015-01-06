# encoding: utf-8
'''
@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
'''
import xmlrpclib
from send_sms import Send_SMS


class Sipgate_SMS(Send_SMS):
    '''
    Send a text message to a cell phone via SIP provider sipgate.
    '''
    def __init__(self, username, password, verbose=False):
        '''
        :param str destination: phone number (RFC3824), starting with country code (e.g. 4917712345678) 
        :param str message: the message
        :param integer verbose: print information to stdout
        :raises xmlrpclib.ProtocolError: if there was an error connecting (wrong username/password)
        '''
        super(Sipgate_SMS, self).__init__(username, password, verbose)

        if self.verbose:
            print "Connecting to https://%s:xxxxxxxx@samurai.sipgate.net/RPC2" % self.username

        XMLRPC_URL = "https://%s:%s@samurai.sipgate.net/RPC2" % (self.username, self.password)
        self.rpc_srv = xmlrpclib.ServerProxy(XMLRPC_URL)
        reply = self.rpc_srv.samurai.ClientIdentify(
            {"ClientName": "sms_notify_if_host_down (python xmlrpclib)", "ClientVersion": "0.1", "ClientVendor": "https://github.com/dansan/sms_notify_if_host_down/"})

        if self.verbose:
            print "Login success. Server reply to ClientIdentify(): '%s'" % reply

    def send(self, destination, message):
        '''
        This function can be called multiple times.

        :param str destination: phone number (RFC3824), starting with country code (e.g. 4917712345678) 
        :param str message: the message, max 160 characters
        :return: True if success
        :rtype: bool
        :raises xmlrpclib.Fault: if there was an error sending the message (wrong phone number)
        :raises ValueError: if the message was longer than 160 characters
        '''
        if len(message) > 160:
            raise ValueError("Message to long.")
        reply = self.rpc_srv.samurai.SessionInitiate(
            {"RemoteUri": "sip:%s@sipgate.de" % destination, "TOS": "text", "Content": message})

        if self.verbose:
            print "SMS send success. Server reply to SessionInitiate(): '%s'" % reply
