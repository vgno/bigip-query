# F5 Bigip Query tool

This is a small tool to scratch an itch. To easily see what backends are behind a VIP and what policies and rules are attached.
Default it lists all, but you can also query by adding a glob that will match name, ip or rules.

## Install instructions

This code needs python3

### Normal

```shell
$ pip3 install -r requirements.txt
```
### VENV Virtual enviroment

```shell
$ python3 -mvenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Usage

List all VIPS
```shell
$ ./bigip-query.py 
``` 

Query a VIP by IP address
```shell
$ ./bigip-query.py 1.2.3.4
```
Query a VIP by IP address
```shell
$ ./bigip-query.py <name>
```

Query VIPs by Irule
```shell
$ ./bigip-query.py <irulename>
```

Query all VIPS NOT having a irule
```shell
$ ./bigip-query.py -n <irulename>


## TODO

* Use tokens instead of users
* Check actual certificates, not only ssl-profile
* Create single binary(?)

