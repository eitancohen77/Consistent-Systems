from Node import Node
from Network import Network
from BookStore import Book, book_key, seed_books, mock_data, print_book_data
from Systems import StrongConsistencyNetwork, EventualConsistencyNetwork
import threading

def demonstration():
    WIDTH = 70
    
    
    def banner(title):
        print("\n" + "=" * WIDTH)
        print(title.center(WIDTH))
        print("=" * WIDTH)
    
    
    def section(title):
        print("\n" + "-" * WIDTH)
        print(f" {title}")
        print("-" * WIDTH)
    
    
    def result_line(label, value):
        print(f"  {label:<38}{value}")
    
    
    # ------------------------------ strong demo ---------------------------------
    
    def run_strong_demo():
        banner("STRONG CONSISTENCY")
        print("  Single source-of-truth node. Every write is synchronously")
        print("  pushed to all nodes - and every read is confirmed against")
        print("  the primary - before returning. Slower, but never wrong.")
    
        strongC = StrongConsistencyNetwork(primary_node_id="A")
        strongC.add_node("A", latency=(0.05, 0.1))
        strongC.add_node("B", latency=(0.05, 0.1))
        strongC.add_node("C", latency=(0.05, 0.1))
        seed_books(strongC, mock_data())
    
        section("Timed write")
        write_elapsed = strongC.write(
            book_key("42"),
            {"book_id": "42", "title": "Dune", "author": "Frank Herbert", "stock": 2},
        )
        result_line("write() elapsed:", f"{write_elapsed:.3f}s")
        result_line("Converged after write?", strongC.is_converged(book_key("42")))
    
        section("Race: two users buy the last copy of A Game of Thrones (stock=1)")
        key = book_key("7")
    
        def check_in_stock(current):
            return current is not None and current["stock"] > 0
    
        def decrement_stock(current):
            updated = dict(current)
            updated["stock"] -= 1
            return updated
    
        results = {}
    
        def try_buy(user):
            success, elapsed = strongC.write_with_check(key, check_in_stock, decrement_stock)
            results[user] = (success, elapsed)
    
        t1 = threading.Thread(target=try_buy, args=("user_1",))
        t2 = threading.Thread(target=try_buy, args=("user_2",))
        t1.start(); t2.start()
        t1.join(); t2.join()
    
        for user, (success, race_elapsed) in results.items():
            result_line(f"{user}:", f"success={success}, {race_elapsed:.3f}s")
    
        winners = sum(1 for success, _ in results.values() if success)
        result_line("Exactly one buyer won?", winners == 1)
        result_line("Nodes converged?", strongC.is_converged(key))
    
        return {
            "write_time": write_elapsed,
            "oversold": winners > 1,
            "converged": strongC.is_converged(key),
        }
    
    
    # ----------------------------- eventual demo --------------------------------
    
    def run_eventual_demo():
        banner("EVENTUAL CONSISTENCY")
        print("  Writes return immediately, no coordination, no lock.")
        print("  Propagation happens in the background and is GUARANTEED")
        print("  to arrive eventually - but two concurrent writes can each")
        print("  succeed against stale local data before that happens.")
    
        eventualS = EventualConsistencyNetwork()
        eventualS.add_node("A", latency=(0.05, 0.1))
        eventualS.add_node("B", latency=(0.05, 0.1))
        eventualS.add_node("C", latency=(0.05, 0.1))
        seed_books(eventualS, mock_data())
    
        section("Timed write")
        success, write_elapsed = eventualS.write(
            book_key("42"),
            {"book_id": "42", "title": "Dune", "author": "Frank Herbert", "stock": 2},
            origin_node_id="A",
        )
        result_line("write() elapsed:", f"{write_elapsed:.3f}s")
    
        value, read_elapsed = eventualS.read(book_key("42"), "B")
        result_line("read() from B right after:", f"stock={value['stock']} ({read_elapsed:.3f}s)")
        result_line("Converged yet?", eventualS.is_converged(book_key("42")))
    
        section("Race: two users buy the last copy of A Game of Thrones (stock=1)")
        key = book_key("7")
    
        def check_in_stock(current):
            return current is not None and current["stock"] > 0
    
        def decrement_stock(current):
            updated = dict(current)
            updated["stock"] -= 1
            return updated
    
        success_a, elapsed_a = eventualS.write_with_check(key, "A", check_in_stock, decrement_stock)
        success_b, elapsed_b = eventualS.write_with_check(key, "B", check_in_stock, decrement_stock)
        result_line("user_1 (via A):", f"success={success_a}, {elapsed_a:.3f}s")
        result_line("user_2 (via B):", f"success={success_b}, {elapsed_b:.3f}s")
    
        oversold = success_a and success_b
        result_line("Both succeeded (oversold)?", oversold)
    
        section("Nodes BEFORE background propagation finishes")
        print_book_snapshot_indented(eventualS, "7")
        result_line("Converged?", eventualS.is_converged(key))
    
        section("Background propagation")
        convergence_wait = eventualS.convergence()
        eventualS.print_propagation_log(key=key)
        result_line("Time to converge after write():", f"{convergence_wait:.3f}s")
    
        section("Nodes AFTER convergence")
        print_book_snapshot_indented(eventualS, "7")
        result_line("Converged?", eventualS.is_converged(key))
        print()
        print("  Note: convergence only means the nodes now AGREE - it does")
        print("  NOT mean the value is correct. The book is still oversold.")
    
        return {
            "write_time": write_elapsed,
            "oversold": oversold,
            "converged": eventualS.is_converged(key),
        }
    
    
    def print_book_snapshot_indented(network, book_id):
        key = book_key(book_id)
        info = network.get_nodes_info(key)
        for node_id, value in info.items():
            stock = value["stock"] if value else None
            print(f"    {node_id}: stock={stock}")
    
    
    # -------------------------------- comparison ---------------------------------
    
    def print_comparison(strong_result, eventual_result):
        banner("SIDE-BY-SIDE COMPARISON")
        print(f"  {'':<20}{'STRONG':<20}{'EVENTUAL':<20}")
        print(f"  {'-'*18:<20}{'-'*18:<20}{'-'*18:<20}")
    
        strong_time = f"{strong_result['write_time']:.3f}s"
        eventual_time = f"{eventual_result['write_time']:.3f}s"
        print(f"  {'Write speed':<20}{strong_time:<20}{eventual_time:<20}")
        print(f"  {'Book oversold?':<20}{str(strong_result['oversold']):<20}"
            f"{str(eventual_result['oversold']):<20}")
        print(f"  {'Ends up converged?':<20}{str(strong_result['converged']):<20}"
            f"{str(eventual_result['converged']):<20}")
    
        if eventual_result["write_time"] > 0:
            speedup = strong_result["write_time"] / eventual_result["write_time"]
            print(f"\n  Eventual's write was ~{speedup:.1f}x faster than strong's.")
        print("  But strong is the only one of the two that never oversells -")
        print("  eventual trades that guarantee away for speed, and only")
        print("  promises the nodes will agree eventually, not that they'll")
        print("  agree on something CORRECT.")

    strong_result = run_strong_demo()
    eventual_result = run_eventual_demo()
    print_comparison(strong_result, eventual_result)
    print("\n" + "=" * WIDTH + "\n")


demonstration()