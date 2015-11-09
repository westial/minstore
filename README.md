minstore
========

This software provides an API to persist and retrieve key value pairs. 

It's based on a file storage engine that populates the new records to multiple nodes with the same application installed on.


This application is a proof of concept and is totally not recommended using as is in a production environment.

Requirements
------------

* Python 2.7+

### Python packages

* wsgiservice
* unittest2 (for testing purposes only)

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

Provided some test cases. See test.py

Pending Improvements
--------------------

* Installer script.
* Indexes: faster access to the key columns of a record.
* Request authentication.
* Compare and synchronize the nodes.

Author
------

Jaume Mila <jaume@westial.com>