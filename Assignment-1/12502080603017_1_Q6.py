"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 6
Topic: Python Module Dependency Resolver
CO Mapping: CO-1, CO-2
Bloom Level: L4 (Analyze)

Description:
    Determines a valid Python module execution/loading order given import relationships:
    1. Directed Edge Interpretation: 'A imports B' means B must be loaded BEFORE A (B -> A).
    2. Topological Sort: Uses Kahn's Algorithm with a Min-Heap (Priority Queue) to always 
       pick the lexicographically smallest module among available zero-indegree candidates.
    3. Cycle Detection: If topological ordering cannot process all modules (processed_count < N),
       a DFS path-tracking stack detects and extracts exactly one cycle.
"""

import heapq
import sys

# Increase recursion depth for deep dependency graphs
sys.setrecursionlimit(300000)


def detect_cycle_dfs(modules: list[str], adj_out: dict[str, set[str]]) -> list[str]:
    """
    Performs Depth First Search (DFS) with node state tracking to extract one directed cycle.
    
    States:
        0 = Unvisited
        1 = Visiting (In current path)
        2 = Visited (Fully processed)
    """
    state = {m: 0 for m in modules}
    parent = {}
    cycle_path = []

    def dfs(u: str) -> bool:
        nonlocal cycle_path
        state[u] = 1  # Mark as visiting

        for v in sorted(adj_out[u]):
            if state[v] == 1:
                # Cycle found! Backtrack from u to v using parent pointers
                curr = u
                path = [curr]
                while curr != v:
                    curr = parent[curr]
                    path.append(curr)
                path.reverse()
                path.append(v)  # Complete the cycle ring
                cycle_path = path
                return True
            elif state[v] == 0:
                parent[v] = u
                if dfs(v):
                    return True

        state[u] = 2  # Mark as visited
        return False

    for m in sorted(modules):
        if state[m] == 0:
            if dfs(m):
                return cycle_path

    return []


def resolve_dependencies(modules: list[str], edges: list[tuple[str, str]]) -> str:
    """
    Computes valid module loading order or extracts a circular dependency cycle.
    """
    # Graph representations
    adj_out = {m: set() for m in modules}  # Outgoing edges: u -> v (u must be loaded before v)
    in_degree = {m: 0 for m in modules}

    # Process imports: "mod_a imports mod_b" means mod_b must be loaded BEFORE mod_a (mod_b -> mod_a)
    for mod_a, mod_b in edges:
        if mod_a in adj_out and mod_b in adj_out:
            if mod_a not in adj_out[mod_b]:  # Ignore duplicate edges
                adj_out[mod_b].add(mod_a)
                in_degree[mod_a] += 1

    # Min-Heap for Lexicographical Kahn's Topological Sort
    heap = []
    for m in modules:
        if in_degree[m] == 0:
            heapq.heappush(heap, m)

    load_order = []

    while heap:
        curr = heapq.heappop(heap)
        load_order.append(curr)

        for neighbor in adj_out[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # Check if topological sort covered all modules
    if len(load_order) == len(modules):
        return " ".join(load_order)

    # Cycle detected: Extract the cycle using DFS
    cycle_nodes = detect_cycle_dfs(modules, adj_out)
    return f"CYCLE {' '.join(cycle_nodes)}"


def main():
    """Main execution block for stream input processing."""
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    iterator = iter(input_data)

    try:
        header = next(iterator).strip()
        if not header:
            return
        n, e = map(int, header.split())

        modules = []
        for _ in range(n):
            modules.append(next(iterator).strip())

        edges = []
        for _ in range(e):
            line = next(iterator).strip()
            if line:
                parts = line.split()
                edges.append((parts[0], parts[1]))

        result = resolve_dependencies(modules, edges)
        print(result)

    except StopIteration:
        pass


if __name__ == "__main__":
    main()
