class BTreeNode:
    def __init__(self, d, leaf=False):
        self.d = d  # Minimum degree
        self.leaf = leaf
        self.keys = []
        self.values = []  # Record pointers
        self.children = []

class BTree:
    def __init__(self, d):
        self.root = BTreeNode(d, True)
        self.d = d
        self.split_count = 0

    def search(self, k, node=None):
        if node is None:
            node = self.root
        
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and node.keys[i] == k:
            return (node, i)  # Found key and its index
        elif node.leaf:
            return None
        else:
            return self.search(k, node.children[i])

    def insert(self, k, value):
        root = self.root
        # If root is full, split it
        if len(root.keys) == (2 * self.d):
            new_root = BTreeNode(self.d, False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, k, value)
        else:
            self._insert_non_full(root, k, value)

    def _insert_non_full(self, x, k, value):
        i = len(x.keys) - 1
        if x.leaf:
            # Insert key into leaf
            x.keys.append(None)
            x.values.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i+1] = x.keys[i]
                x.values[i+1] = x.values[i]
                i -= 1
            x.keys[i+1] = k
            x.values[i+1] = value
        else:
            # Find child to descend into
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.d):
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.children[i], k, value)

    def _split_child(self, x, i):
        self.split_count += 1
        d = self.d
        y = x.children[i]
        z = BTreeNode(d, y.leaf)
        
        # Split keys and values: y gets d-1 keys, z gets d keys
        mid_key = y.keys[d]
        mid_val = y.values[d]
        
        z.keys = y.keys[d+1:]
        z.values = y.values[d+1:]
        
        if not y.leaf:
            z.children = y.children[d+1:]
            y.children = y.children[:d+1]
            
        y.keys = y.keys[:d]
        y.values = y.values[:d]
        
        # Insert mid_key into parent x
        x.children.insert(i + 1, z)
        x.keys.insert(i, mid_key)
        x.values.insert(i, mid_val)

    def get_split_count(self):
        return self.split_count
    
    def calculate_utilization(self):
        nodes = []
        def traverse(node):
            if node:
                nodes.append(node)
                for child in node.children:
                    traverse(child)
        
        traverse(self.root)
        
        total_keys = sum(len(n.keys) for n in nodes)
        # Max keys per node is 2*d
        total_capacity = len(nodes) * (2 * self.d)
        
        return total_keys / total_capacity if total_capacity > 0 else 0
    
    def get_range(self, start_k, end_k, node=None):
        if node is None: node = self.root
        res = []
        
        i = 0
        # Find the first child/key index
        while i < len(node.keys) and start_k > node.keys[i]:
            i += 1
            
        while i < len(node.keys):
            # Visit child before the key
            if not node.leaf:
                res.extend(self.get_range(start_k, end_k, node.children[i]))
                
            # Check the key itself
            if node.keys[i] > end_k:
                return res
            if node.keys[i] >= start_k:
                res.append(node.values[i])
            i += 1
            
        # Visit the final child
        if not node.leaf:
            res.extend(self.get_range(start_k, end_k, node.children[i]))
        return res
    def _borrow_from_prev(self, x, i):
        """Borrow a key from the left sibling (x.children[i-1])."""
        child = x.children[i]
        sibling = x.children[i-1]

        # The parent separator moves down to the child
        child.keys.insert(0, x.keys[i-1])
        child.values.insert(0, x.values[i-1])

        # The last key of the sibling moves up to the parent
        x.keys[i-1] = sibling.keys.pop()
        x.values[i-1] = sibling.values.pop()

        # If not a leaf, move the child pointer too
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x, i):
        """Borrow a key from the right sibling (x.children[i+1])."""
        child = x.children[i]
        sibling = x.children[i+1]

        # The parent separator moves down to the child
        child.keys.append(x.keys[i])
        child.values.append(x.values[i])

        # The first key of the sibling moves up to the parent
        x.keys[i] = sibling.keys.pop(0)
        x.values[i] = sibling.values.pop(0)

        # Move the child pointer
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge_nodes(self, x, i):
        """Merges child x.children[i] with x.children[i+1]."""
        left = x.children[i]
        right = x.children[i+1]

        # 1. Pull down the separator key from the parent into the left child
        left.keys.append(x.keys.pop(i))
        left.values.append(x.values.pop(i))

        # 2. Add all keys and values from the right sibling into the left
        left.keys.extend(right.keys)
        left.values.extend(right.values)

        # 3. Add child pointers if it's an internal node
        if not left.leaf:
            left.children.extend(right.children)

        # 4. Remove the now-empty right child pointer from parent
        x.children.pop(i + 1)

        # 5. If parent is root and becomes empty, update root
        if x == self.root and len(x.keys) == 0:
            self.root = left
            
    def delete(self, k, x=None):
        if x is None: x = self.root
        t = self.d
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1

        if i < len(x.keys) and x.keys[i] == k:
            if x.leaf:
                x.keys.pop(i)
                x.values.pop(i)
            else:
                self._delete_internal_node(x, k, i)
        elif not x.leaf:
            self._delete_from_child(x, i, k)

    def _delete_internal_node(self, x, k, i):
        t = self.d
        left_child = x.children[i]
        right_child = x.children[i+1]

        if len(left_child.keys) >= t:
            # Replace with predecessor
            curr = left_child
            while not curr.leaf: curr = curr.children[-1]
            pred_k, pred_v = curr.keys[-1], curr.values[-1]
            x.keys[i], x.values[i] = pred_k, pred_v
            self.delete(pred_k, left_child)
        elif len(right_child.keys) >= t:
            # Replace with successor
            curr = right_child
            while not curr.leaf: curr = curr.children[0]
            succ_k, succ_v = curr.keys[0], curr.values[0]
            x.keys[i], x.values[i] = succ_k, succ_v
            self.delete(succ_k, right_child)
        else:
            # Merge children and delete
            self._merge_nodes(x, i)
            self.delete(k, left_child)

    def _delete_from_child(self, x, i, k):
        if len(x.children[i].keys) < self.d:
            self._fill_node(x, i)
        # Re-index because children might have merged
        if i > len(x.keys): i -= 1
        self.delete(k, x.children[i])

    def _fill_node(self, x, i):
        if i != 0 and len(x.children[i-1].keys) >= self.d:
            self._borrow_from_prev(x, i)
        elif i != len(x.keys) and len(x.children[i+1].keys) >= self.d:
            self._borrow_from_next(x, i)
        else:
            if i != len(x.keys): self._merge_nodes(x, i)
            else: self._merge_nodes(x, i-1)