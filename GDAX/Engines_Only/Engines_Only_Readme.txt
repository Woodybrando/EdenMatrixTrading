These Engine only files are meant to be run with Supervisor,
using supervisord to keep them running after an
unexpected crash


0. Install supervisor instructions can be found here:
http://supervisord.org/configuration.html

1. for example this needs to be added to /etc/supervisord.conf


[program:EdenMatrixTrading]
command=/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/Engines_Only/GDAX-LTC-BTC.py
autostart=yes
autorestart=yes
startretries=3
stderr_logfile=/var/log/supervisor/GDAX-LTC-BTC.err.log
stdout_logfile=/var/log/supervisor/GDAX-LTC-BTC.log
user=SomeUsername



2. start supervisord

this will run the engine in the background

3. start supervisorctl