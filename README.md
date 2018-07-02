# zmq_hk

A simple camera information transfer server.Map side ZMQ protocols used to send data, the program USES the ZMQ protocol server accepts messages at the same time, and the message into the HTTP protocol related data, and then sends the data using the POST this information, and in the local set port record return messages.

## preparation

- Download the source code `zmq_hk`.
- Python 3.5.3+.

## Install the environment and dependencies

- Create and enter a virtual environment.

```
cd zmq_hk
python3 -m venv env
source env/bin/activate
```

- Install dependency module.

```
pip install -e .
```

## How to perform？

`zmq_hk` is run via the `zmq-hk` command. Run the `--help` subcommand to see the list of options:

```
$ zmq-hk --help
Usage: zmq-hk [OPTIONS]

  Keeper for SAM2

Options:
  --cctv_url TEXT    CCTV Server url, ENV: CCTV_URL
  --api INTEGER      Api port, default=8099, ENV: RPS_PORT
  --debug
  --out_socket TEXT  Zmq Server router
  --help             Show this message and exit.
```

### Let's send a message!

Sending messages can be done using the `zmq-hk` command.

- example:

```
$ zmq-hk --cctv_url=http://127.0.0.1:8099/cctv --api=8099 --out_socket=tcp://127.0.0.1:5570

See more documentation at http://www.mingvale.com
2018-03-09 10:18:35,238 INFO [log] Start Runing...
2018-03-09 10:18:35,238 INFO [cli] Basic Information: {'cctv_url': 'http://127.0.0.1:8099/cctv', 'out_socket': 'tcp://127.0.0.1:5570', 'api': 8099}
2018-03-09 10:18:35,250 DEBUG [selector_events] Using selector: KqueueSelector
2018-03-09 10:18:35,270 INFO [main] config cctv...
2018-03-09 10:18:35,270 INFO [main] output socket is: tcp://127.0.0.1:5570
2018-03-09 10:18:35,287 INFO [main] ... Done!
======== Running on http://0.0.0.0:8099 ========
(Press CTRL+C to quit)

```

### Build exec file

```
$ ./build.sh
```
if everything is ok, get follow file in dist directory:
 - `zmq-hk`           # main exec file
 - `zmq-hk.conf`      # upstart config file
 - `install.sh`       # install script on target

### Deployment
 - scp dist/zmq-hk dist/zmq-hk.conf dist/install.sh to target machine,
 for example:

   ```
   $ scp dist/zmq-hk sysadmin@192.168.1.176:.
   $ scp dist/zmq-hk.conf sysadmin@192.168.1.176:.
   $ scp dist/install.sh sysadmin@192.168.1.176:.
   ```
 - ssh log on target machine:
  
   ```
   $ ssh sysadmin@192.168.1.176
   ```
   
 - on target machine, run:
 
   ```
   $ sudo stop zmq-hk
   $ sudo ./install.sh
   ```
 - start an upstart job
 
   ```
   $ sudo start zmq-hk
   ```
 -  check the job status: 

   ``` 
   $ status zmq-hk
   ```
 - check run log:
 
   ``` 
   $ sudo cat /var/log/upstart/zmq-hk.log
   ``` 
 


### Note:

- `identity = b'SAM-CCTV'` is ZMQ configuration representation.
- `dealer` is the work space.
