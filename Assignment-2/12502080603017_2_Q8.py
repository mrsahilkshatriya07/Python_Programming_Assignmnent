import sys

MOD = 1000000007


def optimize_matrix_path(n: int, m: int, grid: list):
    """
    Finds the maximum score path and the number of distinct maximum-score paths
    from (0,0) to (n-1,m-1) with moves: Right, Down, and Diagonally Down-Right.

    Time Complexity: O(n * m)
    Space Complexity: O(m)
    """
    # Quick check for start or end cell blocked
    if grid[0][0] == 'X' or grid[n - 1][m - 1] == 'X':
        print("IMPOSSIBLE")
        return

    # dp_score[j] stores maximum score to reach column j in current row
    dp_score = [-float('inf')] * m
    # dp_ways[j] stores number of max-score paths to reach column j in current row
    dp_ways = [0] * m

    # Base Case: Initialize top-left cell (0, 0)
    dp_score[0] = int(grid[0][0])
    dp_ways[0] = 1

    for i in range(n):
        # Temporary arrays for row i
        next_score = [-float('inf')] * m
        next_ways = [0] * m

        for j in range(m):
            if grid[i][j] == 'X':
                continue

            cell_val = int(grid[i][j])

            # Special Base Case handling for cell (0,0)
            if i == 0 and j == 0:
                next_score[0] = dp_score[0]
                next_ways[0] = dp_ways[0]
                continue

            best_prev_score = -float('inf')
            ways_count = 0

            # 1. Incoming from TOP: cell (i-1, j) -> dp_score[j]
            if i > 0 and dp_score[j] != -float('inf'):
                s = dp_score[j]
                w = dp_ways[j]
                if s > best_prev_score:
                    best_prev_score = s
                    ways_count = w
                elif s == best_prev_score:
                    ways_count = (ways_count + w) % MOD

            # 2. Incoming from LEFT: cell (i, j-1) -> next_score[j-1]
            if j > 0 and next_score[j - 1] != -float('inf'):
                s = next_score[j - 1]
                w = next_ways[j - 1]
                if s > best_prev_score:
                    best_prev_score = s
                    ways_count = w
                elif s == best_prev_score:
                    ways_count = (ways_count + w) % MOD

            # 3. Incoming from DIAGONAL: cell (i-1, j-1) -> dp_score[j-1]
            if i > 0 and j > 0 and dp_score[j - 1] != -float('inf'):
                s = dp_score[j - 1]
                w = dp_ways[j - 1]
                if s > best_prev_score:
                    best_prev_score = s
                    ways_count = w
                elif s == best_prev_score:
                    ways_count = (ways_count + w) % MOD

            # If at least one valid incoming path exists
            if best_prev_score != -float('inf'):
                next_score[j] = best_prev_score + cell_val
                next_ways[j] = ways_count % MOD

        # Move to next row
        dp_score = next_score
        dp_ways = next_ways

    # Final result check at bottom-right cell (n-1, m-1)
    if dp_score[m - 1] == -float('inf'):
        print("IMPOSSIBLE")
    else:
        print(f"{dp_score[m - 1]} {dp_ways[m - 1]}")


if __name__ == "__main__":
    input_data = sys.stdin.read().split()
    if not input_data:
        sys.exit(0)

    n = int(input_data[0])
    m = int(input_data[1])

    idx = 2
    grid = []
    for i in range(n):
        row = input_data[idx:idx + m]
        grid.append(row)
        idx += m

    optimize_matrix_path(n, m, grid)
