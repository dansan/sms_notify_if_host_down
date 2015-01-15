#!/usr/bin/env python
# encoding: utf-8
"""
sms_notify_if_host_down -- checks multiple hosts/services, sends a text message if down

main is the start module to run the checks and react to downtime.
"""

import sys
import os
import re
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import ConfigParser
from daemon.daemon import DaemonContext
from daemon.runner import make_pidlockfile
import time
import signal

from check_service.generic_tcp_connect import GenericTCPConnect
from notify_sms.sipgate_sms import SipgateSMS
from notify_sms.msg_count import MsgCount

__all__ = []
__version__ = 0.1
__date__ = '2015-01-06'
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
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    args, services = parse_cmd_line()
    setup_logging(args)

    logger.info("** STARTING **")
    logger.debug("Configuration:")
    for conf in ["%s: %s" % (arg, getattr(args, arg)) for arg in dir(args) if
                 not arg.startswith("_") and arg not in ["password"]]:
        logger.debug("    %s", conf)

    if args.daemonize:
        daemon_context = DaemonContext()
        daemon_context.files_preserve = [lh.stream for lh in logger.handlers]
        if args.pid_file:
            try:
                daemon_context.pidfile = make_pidlockfile(args.pid_file, 2)
            except:
                logger.exception("PIDfile creation failed.")
                exit(1)
        daemon_context.signal_map = {signal.SIGTERM: main_quit, signal.SIGHUP: main_quit}
        daemon_context.open()

        logger.info("Forked into background with PID %s.", os.getpid())
        if daemon_context.pidfile:
            logger.debug("PIDfile written to '%s'.", args.pid_file)
        if args.write_conf_file:
            logger.debug("Configuration written to '%s'.", args.write_conf_file)

    failed_services = 0
    msg_count = MsgCount(args.msg_limit)

    while True:
        try:
            results = run_checks(args, services)
            failed_services = reduce(lambda x, y: x + y, [int(not x[0]) for x in results], 0)
            if failed_services >= args.threshold:
                if msg_count.can_send():
                    count = notify(results, services, args)
                    msg_count.update(count)
                else:
                    logger.info("Service(s) failed, but didn't send message because limit reached.")
        except Exception, e:
            logger.exception("Running checks or notifying.")
            raise e
        if args.daemonize:
            time.sleep(args.interval * 60)
        else:
            break
    return failed_services


def main_quit(ec=0):
    logger.info("** EXIT **")
    exit(ec)


def run_checks(args, services):
    """
    run checks on network services

    :param object args: returned by ArgumentParser.parse_args()
    :param list services: [{host, port}, ...]
    :return: list results: [(success, host, port, protocol), ...]
    """
    results = list()
    for service in services:
        gtc = GenericTCPConnect(service["host"], service["port"], "TCP")
        success = gtc.run()
        results.append((success, service["host"], service["port"], "TCP"))
        logger.debug("Host: %s Port: %s Connected: %s", service["host"], service["port"], success)
        if not success and not args.force_all_checks:
            break
    return results


def notify(results, services, args):
    """
    send message about failed service-checks to args.mobile

    :param list results: [(success, host, port, protocol), ...]
    :param list services: [{host, port}, ...]
    :param object args: returned by ArgumentParser.parse_args()
    :return: number of messages sent
    :rtype: integer
    """
    msg = "Service(s) failed: %s" % " ".join(["%s:%d(%s)" % (x[1], x[2], x[3]) for x in results if not x[0]])
    if len(results) < len(services):
        msg += " (%d checks not run)" % (len(services) - len(results))
    logger.info(msg)
    count = 0
    ssms = SipgateSMS(args.username, args.password)
    for msg_slice in range(0, len(msg), 160):
        message = msg[msg_slice:msg_slice + 160]
        if args.test:
            logger.info("Test run - not sending SMS >>%s<< to >>%s<<.", message, args.mobile)
        else:
            ssms.send(args.mobile, message)
        count += 1
    return count


def parse_cmd_line():
    """
    parse command line, check and set sane values

    :return: tuple (object, list): (returned by ArgumentParser.parse_args() , [{host, port}, ...])
    """
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
        conf_parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter, add_help=False)
        conf_parser.add_argument("-c", "--conf_file",
                                 help="Specify config file, cmdline option overwrite values from file.", metavar="FILE")
        args, remaining_argv = conf_parser.parse_known_args()
        if args.conf_file:
            config = ConfigParser.SafeConfigParser()
            config.read([args.conf_file])
            defaults = dict(config.items("Defaults"))
            if defaults.get("services"):
                defaults["services"] = defaults["services"].split()
        else:
            defaults = {"daemonize": False, "threshold": 1, "force_all_checks": False, "interval": 1, "logfile": None,
                        "msg_limit": 1, "mobile": None, "password": None, "pid_file": None, "quiet": False,
                        "services": None, "test": False, "username": None, "verbose": False, "write_conf_file": None}

        parser = ArgumentParser(parents=[conf_parser], description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.set_defaults(**defaults)
        parser.add_argument("-d", "--daemonize", action="store_true",
                            help="Run in background [default: %(default)s]")
        parser.add_argument('-e', '--threshold', help="Notify only if at least x tests fail [default: %(default)s]",
                            type=int)
        parser.add_argument('-f', '--force_all_checks', action='store_true',
                            help="Do not stop running checks after the first one fails [default: %(default)s]")
        parser.add_argument('-i', '--interval', help="Run check(s) every x minutes [default: %(default)s]",
                            type=int)
        parser.add_argument('-l', '--logfile', help="Set logfile [default: %(default)s]")
        parser.add_argument('--msg_limit', help="Limit num of msg sent per hour [default: %(default)s]", type=int)
        parser.add_argument("-m", "--mobile",
                            help="Mobile phone number to send SMS to (starting with country code, e.g. 4917712345678) [required]")
        parser.add_argument("-p", "--password", help="SIP account password [required]")
        parser.add_argument('--pid_file', help="Set pid_file [default: %(default)s]")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-q", "--quiet", action="store_true",
                           help="Show errors only on the console [default: %(default)s]")
        parser.add_argument("-s", "--service", dest="services", metavar="service", nargs='+',
                            help="TCP service to check in format host:port or IP:port [required]")
        parser.add_argument("-t", "--test", action="store_true",
                            help="Test run - don't send SMS [default: %(default)s]")
        parser.add_argument("-u", "--username", help="SIP account username [required]")
        group.add_argument("-v", "--verbose", action="store_true",
                           help="Enable noise on the console [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument("-w", "--write_conf_file", help="Write configuration given on cmdline to file",
                            metavar="FILE")

        # Process remaining arguments
        args = parser.parse_args(remaining_argv)

        args.interval = max(1, args.interval)
        args.msg_limit = max(1, args.msg_limit)

        for argn in ["logfile", "pid_file", "write_conf_file"]:
            filen = getattr(args, argn, None)
            if filen:
                path = os.path.abspath(filen)
                file_dir = os.path.dirname(path)
                if not os.access(file_dir, os.W_OK):
                    parser.error("Directory '%s' for %s not writable." % (file_dir, argn))
                else:
                    setattr(args, argn, path)

    except KeyboardInterrupt:
        # handle keyboard interrupt
        return 0
    except Exception, e:
        if DEBUG:
            raise e
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    # check for required arguments, as argparse was not instructed to do it
    if not all([args.mobile, args.services, args.username, args.password]):
        parser.error("Missing at least one of the required arguments: -m mobile, -s service, -u username, -p password.")

    services = list()
    for service in args.services:
        # check service format, even if socket class does it too...
        try:
            host, port = service.split(":")
            if is_valid_service(host, port, parser):
                port = int(port)
                services.append({"host": host, "port": port})
        except:
            parser.error("Invalid service '%s'." % service)

    if not args.force_all_checks and args.threshold > 1:
        parser.error("Threshold cannot be higher than 1 if force_all_checks is off.")

    if args.write_conf_file:
        config = ConfigParser.SafeConfigParser()
        config.add_section('Defaults')
        for arg in dir(args):
            if not arg.startswith("_") and arg not in ["conf_file", "services", "write_conf_file"]:
                config.set('Defaults', arg, str(getattr(args, arg)))
        config.set('Defaults', "services", reduce(lambda x, y: x + y, [x + " " for x in args.services], "").rstrip())

        with open(args.write_conf_file, 'wb') as configfile:
            try:
                config.write(configfile)
            except Exception, e:
                parser.error("Could not write configuration file '%s': %s" % (args.write_conf_file, e))

    return args, services


def setup_logging(args):
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()

    if args.verbose:
        ch.setLevel(logging.DEBUG)
    elif args.quiet:
        ch.setLevel(logging.ERROR)
    else:
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    if args.logfile:
        fh = logging.FileHandler(args.logfile)
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-5s %(module)s.%(funcName)s:%(lineno)d  %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        if args.verbose:
            fh.setLevel(logging.DEBUG)
        else:
            fh.setLevel(logging.INFO)
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
