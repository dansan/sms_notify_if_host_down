sms_notify_if_host_down
=======================

Sends a short text message via SIP if a network service is down.


This is not a replacement for nagios!
My server hoster has a proper monitoring solution running, but they only send emails. Additionally I want a short text message pushed to my mobile in case a server / VM / service crashes.

The check_service and notify_sms packages have been designed such that it should be simple to add your own service checks and SIP providers.

