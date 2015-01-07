#!/usr/bin/env python
# encoding: utf-8
'''
sms_notify_if_host_down -- checks multiple hosts/services, sends a text message if down

main is the start module to run the checks and react to downtime.

@author:     Daniel Tröder
@copyright:  2015 Daniel Tröder
@license:    GPLv3
@contact:    daniel@admin-box.com
@deffield    updated: 06.01.2015
'''

import sys
import os
import re
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from check_service.generic_tcp_connect import Generic_TCP_connect

__all__ = []
__version__ = 0.1
__date__ = '2015-01-06'
__updated__ = '2015-01-07'

DEBUG = 0
LOGFILE = '/tmp/sms_notify.log'

logger = logging.getLogger()


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    args, services = parse_cmd_line()

    logger.debug("Starting with parameters '%s' to check on services '%s'.", args, services)

    results = list()
    for service in services:
        gtc = Generic_TCP_connect(service["host"], service["port"], "TCP")
        success = gtc.run()
        results.append(success)
        logger.debug("Host: %s Port: %s Success: %s", service["host"], service["port"], success)
        if not success and not args.forceallchecks:
            break

    return int(not all(results))


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
        parser = ArgumentParser(
            description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-f', '--forceallchecks', action='store_true',
                            help="do not stop running checks after the first one fails [default: %(default)s]")
        parser.add_argument('-l', '--logfile', help="set logfile [default: '%s']" % LOGFILE)
        parser.add_argument("-q", "--quiet", action="store_true",
                            help="show errors only on the console [default: %(default)s]")
        parser.add_argument("-t", "--test", action="store_true",
                            help="test run - don't send SMS [default: %(default)s]")
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="enable noise on the console [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument("username", help="SIP account username")
        parser.add_argument("password", help="SIP account password")
        parser.add_argument(
            "mobile", help="mobile phone number to send SMS to (starting with country code, e.g. 4917712345678)")
        parser.add_argument(
            dest="services", help="TCP service to check in format host:port or IP:port", metavar="service", nargs='+')

        # Process arguments
        args = parser.parse_args()
    except KeyboardInterrupt:
        # handle keyboard interrupt
        return 0
    except Exception, e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    setup_logging(args)

    services = list()
    for service in args.services:
        # check service format, even if socket class does it too...
        try:
            host, port = service.split(":")
        except:
            parser.error("Invalid service '%s'." % service)

        if is_valid_service(host, port, parser):
            port = int(port)
            services.append({"host": host, "port": port})

    return args, services


def setup_logging(args):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fh = logging.FileHandler(args.logfile or LOGFILE)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-5s %(module)s.%(funcName)s:%(lineno)d  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)

    if args.verbose:
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
    elif args.quiet:
        ch.setLevel(logging.ERROR)
        fh.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.INFO)
        fh.setLevel(logging.INFO)

    logger.addHandler(ch)
    logger.addHandler(fh)


def is_valid_service(host, port, parser):
    try:
        port = int(port)
    except:
        parser.error("Invalid port '%s'." % port)
    if port > 65535 or port < 1:
        raise ValueError("Invalid port number '%d'." % port)
    # https://stackoverflow.com/questions/11264005/using-a-regex-to-match-ip-addresses-in-python
    pat = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    is_ip = pat.match(host)
    if is_ip:
        for octet in host.split("."):
            if int(octet) > 256:
                parser.error("Invalid IP '%s'." % host)
    else:
        if not is_valid_hostname(host):
            parser.error("Invalid hostname '%s'." % host)
    return True


def is_valid_hostname(hostname):
    # https://stackoverflow.com/questions/2532053/validate-a-hostname-string
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())
