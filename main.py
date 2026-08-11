from Node import Node
from Network import Network

net = Network()
net.add_node("A")
net.add_node("B")
net.add_node("C")

book = "book_35_stock"
net.get_node("A").local_write(book, 5)
print("After Write to Node A")
print(net.get_node("A").local_read(book))
print(f"Is the Network converged?: {net.is_converged(book)}") # Should output False. because the othe nodes are empty

net.get_node("B").local_write(book, 5)
net.get_node("C").local_write(book, 5)
print("After writing to Node B and C")
print(net.get_nodes_info(book))
print(f"Is the Network converged?: {net.is_converged(book)}")
