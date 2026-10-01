"""International shipment traceability built on a doubly linked list.

Data Structures - Doubly linked lists.
Every checkpoint (port, customs, hub, destination) is a node with two
pointers: next (forward in the route) and prev (backward in the route).
Run it without a UI:  python shipment.py
"""

STATUSES = ("on_time", "delayed", "inspected")


class Checkpoint:
    """List node: checkpoint data plus two pointers."""

    def __init__(self, cp_id, name, kind):
        self.id = cp_id
        self.name = name
        self.kind = kind            # port | customs | hub | warehouse | destination
        self.status = "on_time"     # on_time | delayed | inspected
        self.delay_hours = 0
        self.next = None            # following checkpoint (towards destination)
        self.prev = None            # previous checkpoint (towards origin)


class ShipmentRoute:
    """Doubly linked list of checkpoints crossed by one container."""

    def __init__(self):
        self.head = None      # origin
        self.tail = None      # destination
        self.length = 0
        self.current = None   # where the container is being audited
        self._counter = 0     # ids are never reused

    def _new_checkpoint(self, name, kind):
        self._counter += 1
        return Checkpoint(f"CP{self._counter}", name, kind)

    # add to end
    def append(self, name, kind):
        node = self._new_checkpoint(name, kind)
        if self.head is None:
            self.head = node
            self.tail = node
            self.current = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.length += 1
        return node

    # add to start
    def prepend(self, name, kind):
        node = self._new_checkpoint(name, kind)
        if self.head is None:
            self.head = node
            self.tail = node
            self.current = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.length += 1
        return node

    # reach an index starting from the closest end
    def traverse_to_index(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("No checkpoint at that position.")
        if index <= self.length // 2:
            node = self.head
            for _ in range(index):
                node = node.next
        else:
            node = self.tail
            for _ in range(self.length - 1 - index):
                node = node.prev
        return node

    # insert at an index
    def insert(self, index, name, kind):
        if index <= 0:
            return self.prepend(name, kind)
        if index >= self.length:
            return self.append(name, kind)
        node = self._new_checkpoint(name, kind)
        leader = self.traverse_to_index(index - 1)
        follower = leader.next
        leader.next = node
        node.prev = leader
        node.next = follower
        follower.prev = node
        self.length += 1
        return node

    # delete at an index
    def remove(self, index):
        node = self.traverse_to_index(index)
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        if self.current is node:
            self.current = node.next or node.prev
        node.next = None
        node.prev = None
        self.length -= 1
        return node

    # traverse in both directions
    def go_next(self):
        if self.current is None or self.current.next is None:
            return False
        self.current = self.current.next
        return True

    def go_prev(self):
        if self.current is None or self.current.prev is None:
            return False
        self.current = self.current.prev
        return True

    def go_head(self):
        self.current = self.head

    def go_tail(self):
        self.current = self.tail

    def set_status(self, node, status, hours=0):
        if status not in STATUSES:
            raise ValueError("Unknown status.")
        node.status = status
        node.delay_hours = 0 if status == "on_time" else max(0, int(hours))

    # backtrace: walk backwards with prev until a delay or inspection is found
    def investigate_backward(self):
        steps = 0
        node = self.current
        while node is not None:
            if node.status != "on_time":
                return node, steps
            node = node.prev
            steps += 1
        return None, steps

    def total_delay(self):
        total = 0
        node = self.head
        while node is not None:
            total += node.delay_hours
            node = node.next
        return total

    def index_of(self, node):
        i = 0
        node_at = self.head
        while node_at is not None:
            if node_at is node:
                return i
            node_at = node_at.next
            i += 1
        return -1

    def to_text(self):
        parts = []
        node = self.head
        while node is not None:
            parts.append(node.name)
            node = node.next
        return " <-> ".join(parts) if parts else "(empty route)"

    def print_list(self):
        print(self.to_text())


if __name__ == "__main__":
    route = ShipmentRoute()
    route.append("Port A", "port")
    route.append("Customs B", "customs")
    route.append("Distribution Center C", "hub")
    route.append("Destination", "destination")
    route.print_list()
    route.insert(2, "Warehouse X", "warehouse")
    route.print_list()
    route.set_status(route.traverse_to_index(1), "inspected", 18)
    route.go_tail()
    found, steps = route.investigate_backward()   # walks back using prev
    print("Issue found at", found.name, "after", steps, "steps back")
    route.remove(2)
    route.print_list()
