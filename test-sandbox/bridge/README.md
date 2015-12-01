Example - bridge mode
=====================

Three application nodes:

* bridge1 running on 127.0.0.1:8001 as the public interface.
* bridge2 127.0.0.1:8002, and bridge3 127.0.0.1:8003 running on background.
* bridge1 replicates the data into bridge2.
* bridge2 replicates the data into bridge3.
* bridge3 only as storage.