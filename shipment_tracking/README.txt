SHIPMENT TRACKER - Doubly linked list (Python)

How to use
1. Unzip the folder.
2. Double-click index.html (it opens in your browser).
   Nothing to install. All CSS and JavaScript are inside the same file.
   The first time it needs internet: Python runs inside the browser (Pyodide).

Files
- index.html   : interface + the Python logic (Pyodide).
- shipment.py  : the doubly linked list (Checkpoint and ShipmentRoute). Test it alone with:  python shipment.py
- bridge.py    : connects the interface with the list (already included inside index.html).

Methods (as in the class PDF)
append, prepend, insert, remove, traverse_to_index, print_list
+ go_next, go_prev, go_head, go_tail to traverse in both directions
+ investigate_backward: walks back with prev until it finds a delay or customs inspection.

Case study: an international courier tracks a container through Port A -> Customs B -> Distribution Center C -> Destination.
Forward audit uses next; finding where a delay happened uses prev, with no database queries.
