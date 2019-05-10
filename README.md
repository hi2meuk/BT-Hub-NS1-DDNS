# BT Hub NS1 DDNS

An add on service to hass.io to provide a free dynamic DNS service that works with the BT Home Hub and does not require montly login to a dynamic DNS provider.  hass.io plugins are based on docker containers and the underlying code is Python; it is therefore possible to run the container in any docker host including amd64 architectures.

It is developed and proven to work with the BT Hub 5. Other versions are expected to work, if not let me know.

## Design

A cron job calls the application every one minute.
The application retrieves the WAN IP address from the BT Hub and determings if it has changed by keeping track of last address.
If the address changes, a call to NS1's API is made to update the DNS record.

Private settings (API key, domain name etc) are held in config.json.  An example of the schema is provided.

## TODO

The log is only generated when there is an event which means after 24 hours the log in hass.io is empty.  Solution - a log line should be generated at least every 12hours confirming the current WAN IP address.
