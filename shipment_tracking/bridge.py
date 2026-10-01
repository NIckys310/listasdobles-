# Bridge between the UI (HTML/JS) and the doubly linked list in Python.
import json

route = ShipmentRoute()
_dump = json.dumps


def _state(ok=True, msg="", code=""):
    items = []
    node = route.head
    while node is not None:
        items.append({
            "id": node.id, "name": node.name, "kind": node.kind,
            "status": node.status, "delay": node.delay_hours,
            "prev": node.prev.name if node.prev else None,
            "next": node.next.name if node.next else None,
        })
        node = node.next
    return json.dumps({
        "ok": ok, "msg": msg, "code": code, "items": items,
        "length": route.length, "total_delay": route.total_delay(),
        "current_id": route.current.id if route.current else None,
        "current_index": route.index_of(route.current) if route.current else -1,
    })


def handle(action, payload_json):
    global route
    data = json.loads(payload_json or "{}")
    try:
        if action in ("append", "prepend", "insert"):
            name = str(data["name"]).strip()[:40]
            if not name:
                return _state(False, "Type a checkpoint name first.")
            kind = data["kind"]
            if action == "append":
                node = route.append(name, kind)
                code = f"route.append({_dump(name)}, {_dump(kind)})"
            elif action == "prepend":
                node = route.prepend(name, kind)
                code = f"route.prepend({_dump(name)}, {_dump(kind)})"
            else:
                index = int(data["index"])
                node = route.insert(index, name, kind)
                code = f"route.insert({index}, {_dump(name)}, {_dump(kind)})"
            route.current = node
            return _state(msg=f"{node.name} added at position {route.index_of(node)}.", code=code)
        if action == "remove_current":
            if route.current is None:
                return _state(False, "There is no checkpoint to remove.")
            index = route.index_of(route.current)
            node = route.remove(index)
            return _state(msg=f"{node.name} removed. Its neighbours were linked together.",
                          code=f"route.remove({index})")
        if action == "next":
            moved = route.go_next()
            return _state(moved, f"Advanced to {route.current.name}." if moved else "Already at the destination (tail).",
                          "route.go_next()" if moved else "")
        if action == "prev":
            moved = route.go_prev()
            return _state(moved, f"Traced back to {route.current.name}." if moved else "Already at the origin (head).",
                          "route.go_prev()" if moved else "")
        if action == "head":
            route.go_head()
            return _state(msg="Jumped to the origin (head).", code="route.go_head()")
        if action == "tail":
            route.go_tail()
            return _state(msg="Jumped to the destination (tail).", code="route.go_tail()")
        if action == "select":
            index = int(data["index"])
            route.current = route.traverse_to_index(index)
            return _state(msg=f"Selected {route.current.name}.", code=f"route.traverse_to_index({index})")
        if action == "status":
            if route.current is None:
                return _state(False, "Select a checkpoint first.")
            hours = int(data.get("hours") or 0)
            route.set_status(route.current, data["status"], hours)
            return _state(msg=f"{route.current.name} marked as {data['status'].replace('_', ' ')}.",
                          code=f"route.set_status(route.current, {_dump(data['status'])}, {hours})")
        if action == "investigate":
            found, steps = route.investigate_backward()
            if found is None:
                return _state(False, f"Walked back {steps} step(s): no delay or inspection upstream.",
                              "route.investigate_backward()")
            route.current = found
            return _state(msg=f"Issue found at {found.name}, {steps} step(s) back (via prev).",
                          code="route.investigate_backward()")
        if action == "reset":
            route = ShipmentRoute()
            return _state(msg="Route cleared.", code="route = ShipmentRoute()")
        if action == "demo":
            route = ShipmentRoute()
            for item in data["checkpoints"]:
                route.append(item["name"], item["kind"])
            route.set_status(route.traverse_to_index(1), "inspected", 26)
            route.go_tail()
            return _state(msg="Demo route loaded. The container is at the destination: try Investigate.",
                          code=f"route = ShipmentRoute()\nroute.append(...)  # x{route.length} checkpoints")
        return _state(False, "Unknown action.")
    except IndexError:
        return _state(False, "No checkpoint at that position.")
    except (ValueError, KeyError, TypeError):
        return _state(False, "Invalid data.")
