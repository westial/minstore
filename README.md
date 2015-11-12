minstore
========

This software provides a RESTful API to persist and retrieve key value pairs. 

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

###Starting a server

`python api.py SERVERS_LIST_PATH BASE_PATH [PORT]`

* See the --help option for more information.

###API Client

Open a browser and go to the url with port. Example: http://127.0.0.1:8001/text.

You need a html form or a HTTP requester for operations as follows:

* Inserts a new record: `POST /text/<uid> { uid: xxx, value: xxx }`
* Updates an existing record: `PUT /text/<uid> { uid: xxx, value: xxx }`
* Deletes an existing record: `DELETE /text/<uid> { uid: xxx, value: xxx }`



###Rules and restrictions

* POST and PUT methods returns the full record saved into storage.
* GET method returns the full record found into storage.
* A POST request to an existing record returns a 400 error code.
* A PUT, DELETE or GET request to an existing record returns a 404 error code.

Processes
---------

There are 2 processes transforming the record before to persist. Appending new
processes is very easy.

Storage Engine
--------------

The FileStorage engine implements the Storage super class. It allows to inject 
another storage engine to change how and where the information is persisted.

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