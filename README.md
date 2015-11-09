minstore
========

This software provides an API to save and retrieve values by key. It's file
storage based engine and supports to have multiple instances working from
different connected nodes concurrently. The same records are saved into all
nodes.

Requirements
------------

* Python 2.7+

Install
-------

* Copy the files to a directory.
* Configure the file servers.list.

Usage
-----

`python api.py SERVERS_LIST_PATH BASE_PATH [PORT]`

* See the --help option for more information.

Test
----

* Provided some test cases. See test.py

Author
------

* Jaume Mila <jaume@westial.com>