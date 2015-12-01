Example - cloud cache
=====================

Three application nodes:

* cache1 running on 127.0.0.1:8001 as the public interface.
* cache2 127.0.0.1:8002, and cache3 127.0.0.1:8003 running on background.
* cache1 bounces the data to cache2 and cache3 nodes and works as cache.
* cache1 does not persist into local storage.
* cache2 and cache3 only as persistent storage, their servers.list is empty.