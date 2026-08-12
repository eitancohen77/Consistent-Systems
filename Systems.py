import time
import threading 

from Network import Network

class StrongConsistencyNetwork(Network):
    """
    Here the primary node will be this system's source of truth. 
    Every write must go through this node, and every read is 
    validated through it.

    threading.Lock() - ensures that only one thread can modify 
    the network's data at a time. This would say, prevent 2 users
    from buying the last copy of a book at the same time by 
    forcing request's sequentially.
    """
    def __init__(self, primary_node_id):
        super().__init__()
        self.primary_node_id = primary_node_id
        self.lock = threading.Lock()

    def write(self, key, value):
        """
        Every write operation is funneled through the primary data node,
        then synchronously propagated to all the other nodes. This does
        not return until every node has a new value.
        """

        with self.lock:
            """
            For the updates method its a push-based replication. Essentially this means
            the primary/source node actively  sends updates to replica/target nodes.
            The pull-based replication is when the replica nodes send request from 
            main source node for updates.
            """
            start = time.time()
            primary_node = self.get_node(self.primary_node_id)
            primary_node.local_write(key, value)

            
            for node_id, node in self.nodes.items():
                # Skip over the node 
                if node_id == self.primary_node_id:
                    continue 
                node.latency_range()
                node.local_write(key, value)

            return time.time() - start

    def write_with_check(self, key, check_fn, apply_fn):
        """
        In our example of books. It could be the case that book stock reaches 0.
        If one of the server nodes wants to buy a book it needs to check if that
        node is allowed to (if stock is greater then 0). To do this, this takes a 
        check function (check_fn) that checks if the write is permissable, and a 
        apply function (apply_fn) that applies the functino the node wants. In this 
        case book stock -= 1.
        """
        start = time.time()
        primary_node = self.get_node(self.primary_node_id)
        current_value = primary_node.data.get(key)

        if check_fn(current_value) == False:
            return False, time.time() - start

        to_write_value = apply_fn(current_value)
        primary_node.local_write(key, to_write_value)

        for node_id, node in self.nodes.items():
            if node_id == self.primary_node_id:
                continue
            node.latency_range()
            node.local_write(key, to_write_value)

        return True, time.time() - start

    def read(self, key):
        start = time.time()
        primary_node = self.get_node(self.primary_node_id)
        primary_node.latency_range()
        value = primary_node.local_read(key)

        return value, time.time() - start

"""
Eventual consistency is a version of weak consistency where a write
lands on one of the nodes and returns immediately. However the difference
between eventual and weak is in eventual propagation to the other nodes
is guaranteed to "eventually" happen. It happens asynchronously, in the 
background.
"""
class EventualConsistencyNetwork(Network):
    def __init__(self):
        super().__init__()
        self.pending_threads = []

    def propagate(self, node, key, value):
        node.latency_range()
        node.local_write(key, value)

    def write(self, key, value, origin_node_id):
        """
        Write to the origin node (the node that executed the write) and
        returns immediately. Every other node in the system will thenn get 
        a background thread that will apply this write after a simulated 
        latency.
        """
        start = time.time()
        origin_node = self.get_node(origin_node_id)
        origin_node.local_write(key, value)

        for node_id, node in self.nodes.items():
            if node_id == origin_node_id:
                continue

            t = threading.Thread(target=self.propagate, args=(node, key, value), daemon=True)
            t.start()
            self.pending_threads.append(t)

        return True, time.time() - start

    def write_with_check(self, key, origin_node_id, check_fn, apply_fn):
        start = time.time()
        origin_node = self.get_node(origin_node_id)
        current_value = origin_node_id.data.get(key)

        if check_fn(current_value) == False:
            return False, time.time() - start

        to_write_value =  apply_fn(current_value)
        origin_node.local_write(key, to_write_value)

        for node_id, node in self.nodes.items():
            if node_id == origin_node_id:
                continue

            t = threading.Thread(target=self.propagate, args=(node, key, to_write_value), daemon=True)
            t.start()
            self.pending_threads.append(t)

        return True, time.time() - start
            
    