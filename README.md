minstore
========

This software provides a RESTful API to process, persist, spread and retrieve 
any kind of data sets. 

It's based on a file storage engine and after process and store the data, 
properly configured, spreads the new records to multiple nodes with the 
same application installed on.
 
Authentication is still not supported.


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


One or multiple instances
-------------------------

This application can be configured as an individual data storage service in only 
one instance into one server.

Also you can install multiple instances of this application within a range
of servers and configure a strategy of communication among themselves.
 
There are three strategies supported:

* **Mirroring**: one server, the emitter, processes and stores a copy of the input 
data and spreads the processed data to others. And the receivers only store the 
data.
* **Bridge**: when a receiver gets enabled the flag "bridge" by a request parameter,
 this receiver will spreads the data to others. If the new receivers get the 
 "bridge" flag enabled, they will spread to others, and so on.
* **Cache**: two nodes or more are required, the first endpoint and at least one
 dependant server more. First endpoint bounces the request to the seconds one
 and waits for the response. Saves the valid response into the local cache and
 returns the result to the client. When the client requests a record get, if
 the record is into the cache, the record is provided to the client faster. 
 
To enable the "Mirroring" strategy, the "servers.list" configuration file into
the emitter must be a list of receiver servers URL, "http/s" and port included.
For example, the list below is the configuration to spread the data processed
to three servers:

```
http://127.0.0.1:8001
http://127.0.0.1:8002
http://192.168.2.56:8001
```

The "Bridging" strategy is complementary of the strategy above. To enable this
last one, the first row in the list of the "servers.list" configuration file 
must be an asterisk `*`. For example, the list below is the configuration to 
spread the data processed to three servers. If those three servers have 
a configured "servers.list" file, the spreading continues with the new 
configuration/s:

```
*
http://127.0.0.1:8001
http://127.0.0.1:8002
http://192.168.2.56:8001
```

To use "Cache" strategy, set the URI query parameter "cache" to "1" on the GET, PUT and POST requests. Example of request URL with enabled cache, valid for GET, PUT and POST: `http://myapi.com:8000/text/?cache=1`.


Usage
-----

###Server

####Starting server

`python api.py SERVERS_LIST_PATH BASE_PATH [PORT]`

See the --help option for more information.


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
* GET and DELETE look for the record within all nodes before raise a 404 error.


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