# encoding: utf-8
"""
Base class for service check classes.
"""

__author__ = "Daniel Tröder"
__copyright__ = "2015, Daniel Tröder"
__credits__ = ["Daniel Tröder"]
__license__ = "GPLv3"
__maintainer__ = "Daniel Tröder"
__email__ = "daniel@admin-box.com"


class CheckService(object):

    """
    Base class for service check classes.
    """

    def __init__(self, host, port, protocol="TCP"):
        """
        :param str host: FQDN or IP
        :param integer port: port
        :param str protocol: protocol to use (default is TCP)
        """
        self.host = host
        self.port = port
        self.protocol = protocol

    def run(self):
        """
        Runs the check, raises no exception.

        :return: True if success
        :rtype: bool
        """
        raise NotImplementedError
