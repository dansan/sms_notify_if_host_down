sms_notify_if_host_down
=======================

Sends a short text message via SIP if a network service is down.


This is not a replacement for nagios!
My server hoster has a proper monitoring solution running, but they only send emails. Additionally I want a short text message pushed to my mobile in case a server / VM / service crashes.

The check_service and notify_sms packages have been designed such that it should be simple to add your own service checks and SIP providers.

Usage
=====

```
$ ./main.py -h
usage: main.py [-h] [-c FILE] [-d] [-e THRESHOLD] [-f] [-i INTERVAL]
               [-l LOGFILE] [--msg_limit MSG_LIMIT] [-m MOBILE] [-p PASSWORD]
               [--pid_file PID_FILE] [-q] [-s service [service ...]] [-t]
               [-u USERNAME] [-v] [-V] [-w FILE]

  -h, --help            show this help message and exit
  -c FILE, --conf_file FILE
                        Specify config file, cmdline option overwrite values
                        from file.
  -d, --daemonize       Run in background [default: False]
  -e THRESHOLD, --threshold THRESHOLD
                        Notify only if at least x tests fail [default: 1]
  -f, --force_all_checks
                        Do not stop running checks after the first one fails
                        [default: False]
  -i INTERVAL, --interval INTERVAL
                        Run check(s) every x minutes [default: 1]
  -l LOGFILE, --logfile LOGFILE
                        Set logfile [default: None]
  --msg_limit MSG_LIMIT
                        Limit num of msg sent per hour [default: 1]
  -m MOBILE, --mobile MOBILE
                        Mobile phone number to send SMS to (starting with
                        country code, e.g. 4917712345678) [required]
  -p PASSWORD, --password PASSWORD
                        SIP account password [required]
  --pid_file PID_FILE   Set pid_file [default: None]
  -q, --quiet           Show errors only on the console [default: False]
  -s service [service ...], --service service [service ...]
                        TCP service to check in format host:port or IP:port
                        [required]
  -t, --test            Test run - don't send SMS [default: False]
  -u USERNAME, --username USERNAME
                        SIP account username [required]
  -v, --verbose         Enable noise on the console [default: False]
  -V, --version         show program's version number and exit
  -w FILE, --write_conf_file FILE
                        Write configuration given on cmdline to file
```

Configuration file
------------------

Defaults can be read from a configuration file and are overwritten by command line arguments.
To create a configuration file use `-w`.

```
./main.py -d -w sms_notify.conf --pid_file sms_notify.pid -l sms_notify.log \
    -e 1 -tv -m 3 -i 2 -u dansan -p s3cr3t -m 1234567890 \
    -s 127.0.0.1:21 127.0.0.1:22 127.0.0.1:23 127.0.0.1:24
```

This will create a configuration file `sms_notify.conf` that can henceforth be used with `-c`.

At least store the password in the configuration file, so that it does not show up in the process list!

Dependencies
============

- python-daemon
