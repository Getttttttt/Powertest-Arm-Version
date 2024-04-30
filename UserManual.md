# UserManual

Now I'll show you how to use the powertest tool.

## Download powertest.py

The first step is to download the **powertest** file and make sure it is in the same directory as the file or code you want to measure.

## Install prometheus and grafana

In addition to downloading and installing prometheus and grafana, you'll also need to configure nodes and download node_exporter (note your device model).

## Change the environment

There may be some environmental needs. Python3.7 or later is recommended. 

## In your code

Add the following statement to the import section of your code:

```bash
from tools.powertestNew import query_total_energy, get_system_info, getTargetsStatus
```

```bash
import requests
import urllib.request
import json
import subprocess
import re
import time
import platform
import pyJoules
from datetime import datetime, timedelta
```

You can add such a function (instance) to your code:
```bash
@measure_energy
def power_test():
    start_time = int(time.time())
    prometheus_server_address = 'http://localhost:9090'
    getTargetsStatus(prometheus_server_address)

    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)

    main(exp, args)

    end_time = int(time.time())
    query_total_energy(prometheus_server_address, start_time, end_time)
```
The **main** function contains the part you want to test.

## Grafana
**usage_data.csv** will be generated automatically, and you can generate your own visual interface in the same way as in **README.md**.

