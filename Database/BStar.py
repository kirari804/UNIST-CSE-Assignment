class BStarNode:
    def __init__(self, d, leaf=False):
        self.d = d  # Order
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []

class BStarTree:
    def __init__(self, d):
        self.root = BStarNode(d, True)
        self.d = d
        self.splits_1_to_2 = 0
        self.splits_2_to_3 = 0

    def search(self, k, node=None):
        if node is None: node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == k:
            return (node, i)
        elif node.leaf:
            return None
        return self.search(k, node.children[i])

    def insert(self, k, value):
        root = self.root
        # Standard root split for simplicity if root is completely full
        if len(root.keys) >= 2 * self.d:
            new_root = BStarNode(self.d, False)
            new_root.children.append(self.root)
            self._split_1_to_2(new_root, 0) # Root always does 1-to-2
            self.root = new_root
        self._insert_non_full(self.root, k, value)

    def _insert_non_full(self, x, k, value):
        if len(x.keys) == 2 * self.d and x != self.root:
 
            pass 

        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(None); x.values.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i+1] = x.keys[i]
                x.values[i+1] = x.values[i]
                i -= 1
            x.keys[i+1] = k; x.values[i+1] = value
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            
  
            child = x.children[i]
            
            if len(child.keys) >= 2 * self.d:
               
                if not self._attempt_redistribution(x, i):
                    self._split_2_to_3(x, i)
                
              
                i = 0
                while i < len(x.keys) and k > x.keys[i]:
                    i += 1
            
      

            self._insert_non_full(x.children[i], k, value)



    def _attempt_redistribution(self, parent, idx):
        child = parent.children[idx]

        # Try right sibling
        if idx < len(parent.children) - 1:
            sibling = parent.children[idx + 1]
            if len(sibling.keys) < 2 * self.d:
                # Merge + redistribute evenly
                combined_keys = child.keys + [parent.keys[idx]] + sibling.keys
                combined_vals = child.values + [parent.values[idx]] + sibling.values

                mid = len(combined_keys) // 2

                child.keys = combined_keys[:mid]
                child.values = combined_vals[:mid]

                parent.keys[idx] = combined_keys[mid]
                parent.values[idx] = combined_vals[mid]

                sibling.keys = combined_keys[mid+1:]
                sibling.values = combined_vals[mid+1:]

                if not child.leaf:
                    combined_children = child.children + sibling.children
                    child.children = combined_children[:mid+1]
                    sibling.children = combined_children[mid+1:]

                return True

        # Try left sibling
        if idx > 0:
            sibling = parent.children[idx - 1]
            if len(sibling.keys) < 2 * self.d:
                combined_keys = sibling.keys + [parent.keys[idx-1]] + child.keys
                combined_vals = sibling.values + [parent.values[idx-1]] + child.values

                mid = len(combined_keys) // 2

                sibling.keys = combined_keys[:mid]
                sibling.values = combined_vals[:mid]

                parent.keys[idx-1] = combined_keys[mid]
                parent.values[idx-1] = combined_vals[mid]

                child.keys = combined_keys[mid+1:]
                child.values = combined_vals[mid+1:]

                if not child.leaf:
                    combined_children = sibling.children + child.children
                    sibling.children = combined_children[:mid+1]
                    child.children = combined_children[mid+1:]

                return True

        return False

    def _split_2_to_3(self, parent, idx):
        self.splits_2_to_3 += 1

        # ensure idx has a right sibling
        if idx == len(parent.children) - 1:
            idx -= 1

        A = parent.children[idx]
        B = parent.children[idx + 1]

        # Merge everything
        keys = A.keys + [parent.keys[idx]] + B.keys
        vals = A.values + [parent.values[idx]] + B.values

        if not A.leaf:
            children = A.children + B.children
        else:
            children = []

        total = len(keys)

        # Split into 3 parts as evenly as possible
        k1 = total // 3
        k2 = (2 * total) // 3

        # New node C
        C = BStarNode(self.d, A.leaf)

        # Assign keys
        A.keys = keys[:k1]
        A.values = vals[:k1]

        parent.keys[idx] = keys[k1]
        parent.values[idx] = vals[k1]

        C.keys = keys[k1+1:k2]
        C.values = vals[k1+1:k2]

        parent.keys.insert(idx+1, keys[k2])
        parent.values.insert(idx+1, vals[k2])

        B.keys = keys[k2+1:]
        B.values = vals[k2+1:]

        # Fix children
        if not A.leaf:
            A.children = children[:k1+1]
            C.children = children[k1+1:k2+1]
            B.children = children[k2+1:]

        parent.children.insert(idx+1, C)

    def _split_1_to_2(self, x, i):
        """Standard B-tree split for the root node."""
        self.splits_1_to_2 += 1
        d = self.d
        y = x.children[i]
        z = BStarNode(d, y.leaf)
        mid_idx = len(y.keys) // 2
        
        mid_key = y.keys[mid_idx]
        mid_val = y.values[mid_idx]
        
        z.keys = y.keys[mid_idx+1:]
        z.values = y.values[mid_idx+1:]
        y.keys = y.keys[:mid_idx]
        y.values = y.values[:mid_idx]
        
        if not y.leaf:
            z.children = y.children[mid_idx+1:]
            y.children = y.children[:mid_idx+1]
            
        x.children.insert(i + 1, z)
        x.keys.insert(i, mid_key)
        x.values.insert(i, mid_val)

    def get_split_count(self):
        # Return the sum so the evaluate.py script doesn't break
        return self.splits_1_to_2 + self.splits_2_to_3
    
    def calculate_utilization(self):
        visited = set()
        total_keys = 0
        total_nodes = 0

        def traverse(node):
            nonlocal total_keys, total_nodes
            # Use id(node) to ensure we only count this specific object once
            if node is not None and id(node) not in visited:
                visited.add(id(node))
                total_nodes += 1
                total_keys += len(node.keys)
                for child in node.children:
                    traverse(child)

        traverse(self.root)
        max_capacity = total_nodes * (2 * self.d)
        
        if max_capacity == 0: return 0
        # This will now return a value <= 100%
        return total_keys / max_capacity
    
    def get_range(self, start_k, end_k, node=None):
        if node is None: node = self.root
        res = []
        
        i = 0
        while i < len(node.keys):
            key = node.keys[i]
            if key >= start_k:
                # Check left child if not a leaf
                if not node.leaf:
                    res.extend(self.get_range(start_k, end_k, node.children[i]))
                
                # Check current key
                if key <= end_k:
                    # For B-tree, node.values[i] is the RID
                    res.append(node.values[i])
                else:
                    # Key is beyond range, no need to check further children
                    return res
            i += 1
            
        # Check the last child
        if not node.leaf:
            res.extend(self.get_range(start_k, end_k, node.children[i]))
        return res
    
    def _merge_nodes(self, x, i):
        """Merges child x.children[i] with x.children[i+1] for B* Tree."""
        left = x.children[i]
        right = x.children[i+1]

        # 1. Pull down the separator key from the parent
        left.keys.append(x.keys.pop(i))
        left.values.append(x.values.pop(i))

        # 2. Transfer all keys and values from the right sibling
        left.keys.extend(right.keys)
        left.values.extend(right.values)

        # 3. Transfer child pointers if they exist
        if not left.leaf:
            left.children.extend(right.children)

        # 4. Remove the empty right child pointer from the parent
        x.children.pop(i + 1)

        # 5. Root management: If the root becomes empty, the merged node is the new root
        if x == self.root and len(x.keys) == 0:
            self.root = left

    
    def delete(self, k, node=None):
        if node is None: node = self.root
        
        i = 0
        while i < len(node.keys) and k > node.keys[i]: i += 1
        
        if i < len(node.keys) and node.keys[i] == k:
            if node.leaf:
                node.keys.pop(i)
                node.values.pop(i)
            else:
                # Replace with successor (standard B-tree style)
                successor_leaf = node.children[i+1]
                while not successor_leaf.leaf: successor_leaf = successor_leaf.children[0]
                node.keys[i], node.values[i] = successor_leaf.keys[0], successor_leaf.values[0]
                self.delete(node.keys[i], node.children[i+1])
        elif not node.leaf:
            child = node.children[i]
            self.delete(k, child)
            
            # B* Stricter Underflow: check if below 2/3 capacity
            # Here we simplify to d for logic consistency, but B* is usually higher
            if len(child.keys) < self.d: 
                self._bstar_rebalance(node, i)
    
    def _borrow_from_prev(self, x, i):
        """Borrow a key from the left sibling (x.children[i-1])."""
        child = x.children[i]
        sibling = x.children[i-1]

        # 1. The separator key from the parent moves down to the child
        child.keys.insert(0, x.keys[i-1])
        child.values.insert(0, x.values[i-1])

        # 2. The last key of the sibling moves up to the parent
        x.keys[i-1] = sibling.keys.pop()
        x.values[i-1] = sibling.values.pop()

        # 3. If it's an internal node, move the corresponding child pointer
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x, i):
        """Borrow a key from the right sibling (x.children[i+1])."""
        child = x.children[i]
        sibling = x.children[i+1]

        # 1. The separator key from the parent moves down to the child
        child.keys.append(x.keys[i])
        child.values.append(x.values[i])

        # 2. The first key of the sibling moves up to the parent
        x.keys[i] = sibling.keys.pop(0)
        x.values[i] = sibling.values.pop(0)

        # 3. If it's an internal node, move the corresponding child pointer
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _bstar_rebalance(self, parent, i):

        if i > 0 and len(parent.children[i-1].keys) > self.d:
            self._borrow_from_prev(parent, i)
            
        # CASE 2: Borrow from the right sibling
        elif i < len(parent.children) - 1 and len(parent.children[i+1].keys) > self.d:
            self._borrow_from_next(parent, i)
            
        # CASE 3: Merge is necessary
        else:
            if i < len(parent.children) - 1:
                # We have a right sibling to merge with
                self._merge_nodes(parent, i)
            else:
                # We are the last child, merge with the left sibling
                # We pass i-1 so the function merges (i-1) and (i)
                self._merge_nodes(parent, i - 1)
