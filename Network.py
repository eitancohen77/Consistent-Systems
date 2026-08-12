from Node import Node
class Network():
    """
    Network class connecting all the nodes togehter to create a system.
    nodes = {0: Node(0)
     1: Node(1)
     2: Node(2)
     . . . }
    """
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, latency=(0.01, 0.2)):
        node = Node(node_id, latency)
        self.nodes[node_id] = node
        return Node

    def get_node(self, node_id):
        if node_id not in self.nodes:
            raise KeyError("Node id not in network")
        return self.nodes[node_id]

    def get_all_nodes(self):
        return list(self.nodes.values())

    def get_nodes_info(self, key):
        """
        Returns the value of a key from all the nodes.
        This will be a powerful function to see the before/during/after
        of an operation to see if the nodes agree/disagree with eachothe 
        Because of this, we will not use local_read and instead look into 
        the data directly 
        """
        results = {}
        for node_id, node in self.nodes.items():
            results[node_id] = node.data.get(key)
        return results

    def write(self, key, value):
        raise NotImplementedError(
            "Inheritied classes are responsible with implementing this function"
        )
    
    def read(self, key):
        raise NotImplementedError(
            "Inheritied classes are responsible with implementing this function"
        )

    def is_converged(self, key):
        """
        This function returns True if every node currently agrees on the value of a key
        """

        values = list(self.get_nodes_info(key).values()) # Get only the values out nodes information
        if values == None:
            return True

        for item in values:
            if item != values[0]:
                return False
        return True

    def __repr__(self):
        return f"Network(nodes={list(self.nodes.keys())})"


