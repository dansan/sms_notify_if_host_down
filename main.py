#!/usr/bin/python2.7
# encoding: utf-8
'''
notify_sms.send_sms -- Send a short message via SIP provider sipgate.

notify_sms.send_sms is a module to send a short message to a mobile phone
using the XMLRPC API of SIP provider sipgate.de.

API Documentation on it can be found here: http://www.sipgate.de/basic/api
The website is in german, but the linked PDF with the API documentation is in
english: http://www.sipgate.de/beta/public/static/downloads/basic/api/sipgate_api_documentation.pdf


@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
@deffield    updated: 05.01.2015
'''

import sys
import os
import traceback

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from notify_sms.sipgate_sms import Sipgate_SMS

__all__ = []
__version__ = 0.1
__date__ = '2015-01-05'
__updated__ = '2015-01-05'

DEBUG = 1


def main(argv=None):  # IGNORE:C0111
    '''Send SMS as specified on the command line.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    args = parse_cmd_line()
    try:
        ssms = Sipgate_SMS(args.username, args.password, bool(args.verbose))
        ssms.send(args.destination, args.message)
    except:
        print "Could not send message:\n"
        traceback.print_exc(file=sys.stderr)
        return 1


def parse_cmd_line():
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Daniel Tröder on %s.
  Copyright 2015 Daniel Tröder. All rights reserved.

  Licensed under the GPLv3
  https://www.gnu.org/licenses/gpl.txt

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("username", help="sipgate account username")
        parser.add_argument("password", help="sipgate account password")
        parser.add_argument("destination", help="number to send SMS to")
        parser.add_argument("message", help="the message, max 160 characters")
        parser.add_argument("-v", "--verbose", dest="verbose",
                            action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument(
            '-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        if len(args.message) > 160:
            print "Message to long."

        if args.verbose > 0:
            print("Verbose mode on")
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    return args

if __name__ == "__main__":
    sys.exit(main())
