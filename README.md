# Neurainodes
This project is based on [Bitnodes](https://github.com/ayeowch/bitnodes).

Neurainodes is currently being developed to estimate the size of the Neurai network by finding all the reachable nodes in the network. These are the nodes that accept incoming connections. Why you should run a full node is explained here on the [Bitcoin wiki](https://en.bitcoin.it/wiki/Full_node). The current methodology involves sending [`getaddr`](https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery) messages recursively to find all the reachable nodes in the network, starting from a set of seed nodes. It is worth mentioning that this method of estimating network size [does not list all full nodes](https://en.bitcoin.it/wiki/Clearing_Up_Misconceptions_About_Full_Nodes) because not all nodes have an open port that can be probed using Neurainodes. These nodes are either behind firewalls or they are configured to not listen for connections.

The goal is to run the service as efficient as possible. The ravennodes crawler, web_updater, and website currently all run on an a1 medium AWS server (1 vCPu, 2GB RAM). 

## TOC
- [Neurainodes](#neurainodes)
  - [TOC](#toc)
- [Neurainodes Crawler](#neurainodes-crawler)
  - [Main Changes](#main-changes)
  - [Dependencies](#dependencies)
      - [Python Packages](#python-packages)
  - [Steps on setting up a machine to run Neurainodes](#steps-on-setting-up-a-machine-to-run-neurainodes)
    - [Ubuntu 18.04:](#ubuntu-1804)
      - [Install redis](#install-redis)
      - [Install Neurainodes and set up dependencies](#install-neurainodes-and-set-up-dependencies)
      - [Update open file limits to prevent Neurainodes crashing on IO errors](#update-open-file-limits-to-prevent-neurainodes-crashing-on-io-errors)
      - [Start redis service](#start-redis-service)
      - [To start the Neurainodes crawler](#to-start-the-neurainodes-crawler)
- [Neurainodes Web-updater](#neurainodes-web-updater)
  - [Dependencies](#dependencies-1)
    - [Python Packages](#python-packages-1)
  - [To start the Neurainodes Web-updater](#to-start-the-neurainodes-web-updater)
- [Neurainodes website](#neurainodes-website)
  - [Dependencies](#dependencies-2)
    - [Python Packages](#python-packages-2)
  - [Website hosting](#website-hosting)
- [Call for improvements](#call-for-improvements)

# Neurainodes Crawler

## Main Changes
- Changed parameters to support Neurai
- Turned off Tor network support.

## Dependencies
- Python 2.7 virtual environment
- [Redis](https://redislabs.com/)

#### Python Packages ####
| Package     | Version
| ----------- | -------
| dpkt        | 1.9.1 
| flake8      | 3.5.0 
| geoip2      | 2.9.0 
| scipy       | 0.13.0 
| gevent      | 1.3.4
| ipaddress   | 1.0.22
| PySocks     | 1.6.8
| pytest      | 3.7.3
| redis       | 2.10.6
| requests    | 2.20.0

## Steps on setting up a machine to run Neurainodes 
### Ubuntu 18.04:
#### Install redis 
```
sudo apt update && sudo apt upgrade
cd ~/
sudo apt install redis

# I prefer running redis manually
# Optional, remove the service: sudo service redis-server disable
```
#### Install Neurainodes and set up dependencies
```
#Move redis conf file
sudo cp [LOCATION]/crawler/depends/redis/redis.conf /etc/redis/
#Install Python requirements
cd [LOCATION]/crawler
pip install -r requirements.txt
#Update GeoIP
bash geoip/update.sh
```
**NOTE:** For GeoIP, you now need an account at maxmind.com and acquire a license key. Add this key to `~/.bashrc`:
```
export MAXMIND_LICENSE_KEY=YOUR-KEY-HERE
```

#### Update open file limits to prevent Neurainodes crashing on IO errors
```
# Edit the following file:
sudo nano /etc/security/limits.conf
	#Add the following:
	* soft nofile 1000000
	* hard nofile 1000000
 	root soft nofile 1000000
	root hard nofile 1000000
	
# If you run an Ubuntu GUI, Edit the following files too:
sudo nano /etc/systemd/user.conf
	#Change the following setting:
	DefaultLimitNOFILE=1000000
sudo nano /etc/systemd/system.conf 
	#Change the following setting:
	DefaultLimitNOFILE=1000000
```
#### Start redis service
```
#Login as admin
sudo -i
#Update /proc/sys/net/core/somaxconn
sysctl -w net.core.somaxconn=511
#Disable THP
echo never > /sys/kernel/mm/transparent_hugepage/enabled
# Set overcommit_memory to 1
sysctl vm.overcommit_memory=1
#Start Redis Server
redis-server /etc/redis/redis.conf
#Alternatively, run redis in the background with redis-server /etc/redis/redis.conf --daemonize yes

#Make sure the file redis.sock is made in /tmp/
```
#### To start the Neurainodes crawler
Open a new console, activate the python 2.7 virtual environment and start the crawler:
```
cd [LOCATION]/Neurainodes
./start.sh
```
Data output will be available in `~/Neurainodes/data/export/5241564e`

Process logs  will be available in `~/Neurainodes/log`

# Neurainodes Web-updater
- Data change watcher [adaptation from Michael Cho](https://www.michaelcho.me/article/using-pythons-watchdog-to-monitor-changes-to-a-directory) looking for crawler updates
- Data updater generating ravencoin nodes tables and world maps for the website

## Dependencies
- Python 3.7 virtual environment

### Python Packages
| Package     | Version
| ----------- | -------
pandas        | 0.24.1
watchdog      | 0.9.0
numpy         | 1.16.1
plotly        | 3.6.1

## To start the Neurainodes Web-updater
Open a new console, activate the python 3.7 virtual environment and start the updater:
```
cd [LOCATION]/web_updater
./start.sh
```

# Neurainodes website
- Website built using flask

## Dependencies
- Python 3.7 virtual environment

### Python Packages
See website/requirements.txt

## Website hosting
[Website is hosted according to this guide](https://medium.com/ymedialabs-innovation/deploy-flask-app-with-nginx-using-gunicorn-and-supervisor-d7a93aa07c18)

# Call for improvements
Everyone is welcome to propose changes. Currently, the whole system is set up using python for self-educational purposes. 
Using an SQL type database, for example, will drastically improve performance. 

___

-Jeroz

https://github.com/jeroz1/Neurainodes
https://github.com/RavenCommunity/Neurainodes


