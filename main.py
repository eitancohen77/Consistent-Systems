from Node import Node

network = []

for i in range(3):
    bookStore = Node(i)
    network.append(bookStore)

for bookStore in network:
    bookStore.local_write("book_32", 5)

print(network[0].local_read("book_32"))
print(network[0].get_log())
print(network[0])