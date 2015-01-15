# encoding: utf-8
"""
generic_tcp_connect -- tries to connect to a TCP socket
"""

from check_service import CheckService
import socket
import logging

__author__ = "Daniel Tröder"
__copyright__ = "2015, Daniel Tröder"
__credits__ = ["Daniel Tröder"]
__license__ = "GPLv3"
__maintainer__ = "Daniel Tröder"
__email__ = "daniel@admin-box.com"

logger = logging.getLogger()


class GenericTCPConnect(CheckService):

    """
    tries to connect to a TCP socket
    """

    def run(self):
        """
        Runs the check, raises no exception.

        :return: True if success
        :rtype: bool
        """
        try:
            s = socket.create_connection(address=(self.host, self.port), timeout=10)
            s.close()
            success = True
        except Exception, e:
            success = False
            logger.debug("Could not connect to %s:%d (TCP): %s", self.host, self.port, e)
        return success
