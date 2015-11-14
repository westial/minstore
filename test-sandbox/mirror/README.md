Example - mirror mode
=====================

Three application nodes:

* mirror1 running on 127.0.0.1:8001 as the public interface.
* mirror2 127.0.0.1:8002, and mirror3 127.0.0.1:8003 running on background.
* mirror1 replicates the data into mirror2 and also into mirror 3.
* mirror2 and mirror3 stop both chain, their servers.list is empty.