from Node import Node
from Network import Network
from BookStore import Book, book_key, seed_books, mock_data, print_book_data
from Systems import StrongConsistencyNetwork
import threading

def testNetwork():
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

def testBookStore():
    net = Network()
    node_ids = ["A", "B", "C"]
    for node_id in node_ids:
        net.add_node(node_id)

    data = mock_data()
    seed_books(net, data)

    for book in data:
        print_book_data(net, book.book_id)

def testStrongConsistentSystem():
    strongC = StrongConsistencyNetwork(primary_node_id="A")
    strongC.add_node("A", latency=(0.02, 0.05))
    strongC.add_node("B", latency=(0.02, 0.05))
    strongC.add_node("C", latency=(0.02, 0.05))

    seed_books(strongC, mock_data())
    print(strongC.get_node(strongC.primary_node_id))

    new_write = {"book_id": "42", "title": "Harry Potter", "author": "J.K. Rowling", "stock":2}
    elapsed = strongC.write(book_key("42"), new_write)
    print(f"write() operation took {elapsed} seconds")


    
    print_book_data(strongC, "42")

    # Check read operation 
    value, read_elapsed = strongC.read(book_key("42"))
    print(f"read() took {read_elapsed} seconds value: {value}")

    print("\n=== Race condition: two users buy the last copy of Neuromancer (stock=1) ===")

    key = book_key("7")

    def check_in_stock(data):
        if data and data["stock"] > 0:
            return True
        return False

    def decrement_stock(data):
        updated = dict(data)
        updated["stock"] -= 1
        return updated

    results = {}

    def try_buy(user_name):
        success, elapsed = strongC.write_with_check(key, check_in_stock, decrement_stock)
        results[user_name] = (success, elapsed)

    t1 = threading.Thread(target=try_buy, args=("user_1",))
    t2 = threading.Thread(target=try_buy, args=("user_2",))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for user, (success, elapsed) in results.items():
        print(f"{user}: success={success}, took {elapsed:.3f} seconds")


    print("\nHow the node see the data:")
    print_book_data(strongC, "7")
    print("\nExactly one buyer should have succeeded")

testStrongConsistentSystem()