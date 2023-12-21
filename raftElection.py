import random
import time


class Node:
    def __init__(self, id):
        self.id = id
        self.state = "follower"  # initial state
        self.voted_for = None
        self.timeout = random.randint(5, 10)  # random timeout between 150ms and 300ms
        self.election_timer = 0

    def tick(self):
        self.election_timer += 1
        if self.state == "follower":
            if self.election_timer >= self.timeout:
                self.start_election()
        elif self.state == "candidate":
            # In a real implementation, a candidate would send RPC requests to other nodes here
            # For simplicity, we just simulate the process and assume the node wins the election
            self.win_election()

    def start_election(self):
        self.state = "candidate"
        self.voted_for = self
        self.election_timer = 0
        print(f"Node {self.id} started an election")

    def win_election(self):
        self.state = "leader"
        print(f"Node {self.id} won the election")


def simulate_election(n, ticks):
    nodes = [Node(i) for i in range(1, n + 1)]
    for _ in range(ticks):
        for node in nodes:
            node.tick()
            print(f"Node {node.id} is now a {node.state}")
        time.sleep(0.1)  # Sleep for 100ms between each tick

if __name__ == "__main__":
    simulate_election(3, 1000)  # Simulate an election with 5 nodes over 1000 ticks
