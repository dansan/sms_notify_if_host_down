#!/usr/bin/env python
# encoding: utf-8
"""
notify_sms.cli -- Send a short message via SIP provider sipgate.

notify_sms.cli is a module to send a short message to a mobile phone
using the XMLRPC API of SIP provider sipgate.de.

API Documentation on it can be found here: http://www.sipgate.de/basic/api
The website is in german, but the linked PDF with the API documentation is in
english: http://www.sipgate.de/beta/public/static/downloads/basic/api/sipgate_api_documentation.pdf
"""

import sys
import os
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from sipgate_sms import Sipgate_SMS

__all__ = []
__version__ = 0.1
__date__ = '2015-01-05'
__updated__ = '2015-01-07'

__author__ = "Daniel Tröder"
__copyright__ = "2015, Daniel Tröder"
__credits__ = ["Daniel Tröder"]
__license__ = "GPLv3"
__maintainer__ = "Daniel Tröder"
__email__ = "daniel@admin-box.com"
__status__ = "Development"

DEBUG = 0

logger = logging.getLogger()


def main(argv=None):  # IGNORE:C0111
    """Send SMS as specified on the command line."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    args = parse_cmd_line()
    setup_logging(args)

    try:
        ssms = Sipgate_SMS(args.username, args.password)
        ssms.send(args.mobile, args.message)
    except:
        logger.exception("Could not send message:\n")
        return 1


def parse_cmd_line():
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Daniel Tröder on %s.
  Copyright 2015 Daniel Tröder. All rights reserved.

  Licensed under the GPLv3
  https://www.gnu.org/licenses/gpl.txt

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("username", help="sipgate account username")
        parser.add_argument("password", help="sipgate account password")
        parser.add_argument("mobile", help="mobile phone number to send SMS to")
        parser.add_argument("message", help="the message, max 160 characters")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        if len(args.message) > 160:
            logger.error("Message to long.")

    except KeyboardInterrupt:
        # handle keyboard interrupt
        return 0
    except Exception, e:
        if DEBUG:
            raise e
        indent = len(program_name) * " "
        logger.error(program_name + ": " + repr(e))
        logger.error(indent + "  for help use --help")
        return 2

    return args


def setup_logging(args):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())
