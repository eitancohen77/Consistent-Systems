import time

"""
A single node in a distributed system, able to hold its own local copy
of the data. 
Need to implement latency to simulate network delay so that propagation 
feels more realistic instead of instant
"""
class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.data = {}
        self.log = []

    def local_write(self, key, value):
        self.data[key] = value
        self.log.append(("write", key, value, time.time()))

    def local_read(self, key):
        if key not in self.data:
            raise KeyError(f"Key '{key}' does not exist in system")

        value = self.data[key]
        self.log.append(("read", key, value, time.time()))
        return value

    def get_log(self):
        prefix = "Node("
        padding = " " * (len(prefix) + 12)
        entries = f"\n{padding}".join(str(entry) for entry in self.log)
        return f"Node({self.node_id}, log data={entries})"

    def __repr__(self):
        prefix = "Node("
        padding = " " * (len(prefix) + 12)
        entries = f"{padding}".join(str(f"{key}: {value}") for key,value in self.data.items())
        return f"{prefix}{self.node_id}, data={entries})"



