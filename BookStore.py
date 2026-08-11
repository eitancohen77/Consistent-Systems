"""

The reason why we are not defining functions inside the Book dataclass is because
we dont want the Book to handle anything. We just want it to be a data type. Nothing 
more. If we were to add functions like get_id() it would ruin what we are trying to do
because that needs to be the orchestrator's (networks) job.
"""
from dataclasses import dataclass, asdict

@dataclass
class Book:
    book_id: str
    title:str
    author: str
    stock: int

    def as_dict(self):
        return asdict(self)



def book_key(book_id):
    return f"book:{book_id}"

def seed_books(network, books, node_ids=None):
    """
    This function works as a initalizer. It writes inital book records 
    directly into every node's local storage in the network. All nodes
    should look the same as we initalize them because we want to test
    the systems.
    """
    node_ids = node_ids or network.nodes.keys() # We can get the nodes_id through network
    for book in books:
        key = book_key(book.book_id)
        for node_id in node_ids:
            node = network.get_node(node_id)
            node.local_write(key, book.as_dict())

def mock_data():
    # A starting dataset to fuel our network nodes
    return [
        Book(book_id="42", title="Harry Potter", author="J.K. Rowling", stock=3),
        Book(book_id="7", title="A Game of Thrones", author="George R.R. Martin", stock=1),
        Book(book_id="93", title="Cracking the Coding Interview", author="Gayle Laakmann McDowell", stock=5)
    ]

def print_book_data(network, book_id):
    """
    Print what every node currently believes a book's record is. Used
    to show the convergence and divergence between the nodes in regards 
    to a specific key
    """
    key = book_key(book_id)
    nodes_info = network.get_nodes_info(key)
    for node_id, value in nodes_info.items():
        print(f"    {node_id}: {value}")
    print(f"Are the nodes Converged: {network.is_converged(key)}")


