# encoding: utf-8
"""
Class for counting messages sent in 1 hour.
"""
import datetime

__author__ = "Daniel Tröder"
__copyright__ = "2015, Daniel Tröder"
__credits__ = ["Daniel Tröder"]
__license__ = "GPLv3"
__maintainer__ = "Daniel Tröder"
__email__ = "daniel@admin-box.com"


class MsgCount(object):
    """
    Class for counting messages sent in 1 hour.
    """

    def __init__(self, msglimit):
        """
        :type msglimit: integer
        """
        self.msg_limit = max(0, msglimit)
        self.msg_count = 0
        self.msg_list = dict()

    def can_send(self):
        """
        Checks if is there enough credit left to send a message.

        :return: True if balance is positive.
        :rtype: bool
        """
        # Purge old notifications, lowering the msg_count.
        for ts, count in self.msg_list.items():
            if datetime.datetime.now() - ts > datetime.timedelta(hours=1):
                self.msg_count -= count
                del self.msg_list[ts]

        return self.msg_count < self.msg_limit

    def update(self, count):
        """
        Update balance.

        :param integer count: number of msg sent since last update.
        """
        count = max(0, count)

        self.msg_count += count
        self.msg_list[datetime.datetime.now()] = count
