class BPlusNode:
    def __init__(self, d, leaf=False):
        self.d = d
        self.leaf = leaf
        self.keys = []
        self.values = []  # In internal nodes, these are child pointers; in leaves, RIDs
        self.next = None  # Linked list pointer for leaf nodes

class BPlusTree:
    def __init__(self, d):
        self.root = BPlusNode(d, True)
        self.d = d
        self.split_count = 0

    def get_split_count(self):
        return self.split_count

    def search(self, k):
        """Always descends to the leaf level."""
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and k >= node.keys[i]:
                i += 1
            node = node.values[i]
        
        # Binary or linear search within the leaf
        for i, key in enumerate(node.keys):
            if key == k:
                return node.values[i]
        return None

    def range_query(self, k_start, k_end):
        """Returns all values within [k_start, k_end]."""
        results = []
        node = self.root
        
        # 1. Find the starting leaf
        while not node.leaf:
            i = 0
            while i < len(node.keys) and k_start >= node.keys[i]:
                i += 1
            node = node.values[i]
        
        # 2. Traverse the linked list of leaves
        while node:
            for i, key in enumerate(node.keys):
                if k_start <= key <= k_end:
                    results.append(node.values[i])
                if key > k_end:
                    return results
            node = node.next
        return results

    def insert(self, k, value):
        root = self.root
        if len(root.keys) == 2 * self.d:
            new_root = BPlusNode(self.d, False)
            new_root.values.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, k, value)

    def _split_child(self, parent, i):
        self.split_count += 1 
        d = self.d
        old_node = parent.values[i]
        new_node = BPlusNode(d, old_node.leaf)
        
        mid_idx = d
        # B+ Tree Split Logic: 
        # In leaves, the middle key stays in the leaf AND is copied to parent.
        # In internal nodes, the middle key is moved to parent.
        
        if old_node.leaf:
            new_node.keys = old_node.keys[mid_idx:]
            new_node.values = old_node.values[mid_idx:]
            new_node.next = old_node.next
            old_node.next = new_node
            
            old_node.keys = old_node.keys[:mid_idx]
            old_node.values = old_node.values[:mid_idx]
            
            # Copy the smallest key of the new leaf to parent
            parent.keys.insert(i, new_node.keys[0])
        else:
            mid_key = old_node.keys[mid_idx]
            new_node.keys = old_node.keys[mid_idx+1:]
            new_node.values = old_node.values[mid_idx+1:]
            
            old_node.keys = old_node.keys[:mid_idx]
            old_node.values = old_node.values[:mid_idx+1]
            
            parent.keys.insert(i, mid_key)
            
        parent.values.insert(i + 1, new_node)

    def _insert_non_full(self, node, k, value):
        i = len(node.keys) - 1
        if node.leaf:
            # Linear insert into leaf
            node.keys.append(None); node.values.append(None)
            while i >= 0 and k < node.keys[i]:
                node.keys[i+1] = node.keys[i]
                node.values[i+1] = node.values[i]
                i -= 1
            node.keys[i+1] = k
            node.values[i+1] = value
        else:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            i += 1
            if len(node.values[i].keys) == 2 * self.d:
                self._split_child(node, i)
                if k >= node.keys[i]:
                    i += 1
            self._insert_non_full(node.values[i], k, value)
    
    def calculate_utilization(self):
        nodes = []
        def traverse(node):
            if node:
                nodes.append(node)
                if not node.leaf:
                    # In B+, internal node 'values' are the child pointers
                    for child in node.values:
                        traverse(child)
        
        traverse(self.root)
        total_keys = sum(len(n.keys) for n in nodes)
        # Max capacity is 2*d
        total_capacity = len(nodes) * (2 * self.d)
        
        return total_keys / total_capacity if total_capacity > 0 else 0
    
    def get_range(self, start_k, end_k):
        rids = []
        # 1. Find the leaf containing start_k
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and start_k >= node.keys[i]:
                i += 1
            node = node.values[i]
        
        # 2. Use the next pointer to scan horizontally
        current = node
        while current:
            for i, key in enumerate(current.keys):
                if key >= start_k and key <= end_k:
                    rids.append(current.values[i])
                if key > end_k:
                    return rids
            current = current.next # Moving to the next leaf node
        return rids
    
    def delete(self, k):
        if not self.root.keys:
            return
        self._delete_recursive(None, self.root, 0, k)
        # Root collapse: if root is not a leaf and has only 1 child
        if len(self.root.keys) == 0 and not self.root.leaf:
            if len(self.root.values) > 0:
                self.root = self.root.values[0]

    def _delete_recursive(self, parent, node, idx_in_parent, k):
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1

        if node.leaf:
            if i < len(node.keys) and node.keys[i] == k:
                node.keys.pop(i)
                node.values.pop(i)
            return

        # Internal node: descend
        child = node.values[i]
        self._delete_recursive(node, child, i, k)

        # Post-recursion underflow check
        if len(child.keys) < self.d:
            self._handle_underflow(node, i)

    def _handle_underflow(self, parent, i):
        child = parent.values[i]
        
        # 1. Borrow from Left Sibling
        if i > 0 and len(parent.values[i-1].keys) > self.d:
            left_sib = parent.values[i-1]
            if child.leaf:
                child.keys.insert(0, left_sib.keys.pop())
                child.values.insert(0, left_sib.values.pop())
                parent.keys[i-1] = child.keys[0] # New separator is child's new first key
            else:
                # Internal node: pull parent key down, push sibling key up
                child.keys.insert(0, parent.keys[i-1])
                child.values.insert(0, left_sib.values.pop())
                parent.keys[i-1] = left_sib.keys.pop()
            
        # 2. Borrow from Right Sibling
        elif i < len(parent.values) - 1 and len(parent.values[i+1].keys) > self.d:
            right_sib = parent.values[i+1]
            if child.leaf:
                child.keys.append(right_sib.keys.pop(0))
                child.values.append(right_sib.values.pop(0))
                parent.keys[i] = right_sib.keys[0] # New separator is sibling's new first key
            else:
                # Internal node: pull parent key down, push sibling key up
                child.keys.append(parent.keys[i])
                child.values.append(right_sib.values.pop(0))
                parent.keys[i] = right_sib.keys.pop(0)
            
        # 3. Merge
        else:
            if i > 0: # Merge child with its left sibling
                left_sib = parent.values[i-1]
                if not child.leaf:
                    # Pull down the separator from parent
                    left_sib.keys.append(parent.keys.pop(i-1))
                else:
                    parent.keys.pop(i-1)
                
                left_sib.keys.extend(child.keys)
                left_sib.values.extend(child.values)
                if child.leaf:
                    left_sib.next = child.next
                parent.values.pop(i)
            else: # Merge child with its right sibling
                right_sib = parent.values[i+1]
                if not child.leaf:
                    # Pull down the separator from parent
                    child.keys.append(parent.keys.pop(i))
                else:
                    parent.keys.pop(i)
                
                child.keys.extend(right_sib.keys)
                child.values.extend(right_sib.values)
                if child.leaf:
                    child.next = right_sib.next
                parent.values.pop(i+1)