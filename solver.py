import sys

# The 13 regions of the board (12 pentominoes + 1 tetromino)
SQUARES = [
    [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],        # Region 0
    [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3)],        # Region 1
    [(0, 5), (0, 6), (1, 6), (2, 6), (2, 5)],        # Region 2
    [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7)],        # Region 3
    [(5, 7), (6, 7), (7, 7), (7, 6), (7, 5)],        # Region 4
    [(3, 6), (4, 6), (3, 5), (4, 5), (5, 5)],        # Region 5
    [(6, 0), (7, 0), (7, 1), (7, 2), (7, 3)],        # Region 6
    [(1, 4), (1, 5), (2, 2), (2, 3), (2, 4)],        # Region 7
    [(3, 0), (3, 1), (3, 2), (2, 1), (4, 1)],        # Region 8
    [(4, 0), (5, 0), (5, 1), (6, 1), (6, 2)],        # Region 9
    [(5, 6), (6, 6), (6, 5), (6, 4), (7, 4)],        # Region 10
    [(4, 2), (5, 2), (5, 3), (5, 4), (6, 3)],        # Region 11
    [(3, 3), (4, 3), (3, 4), (4, 4)]                 # Region 12 (tetromino)
]

CELL_TO_REGION = {}
for i, r in enumerate(SQUARES):
    for c in r:
        CELL_TO_REGION[c] = i

CHECKPOINTS = {
    0: (0, 0, 1), 3: (6, 2, 0), 6: (4, 3, 0), 9: (3, 5, 0), 12: (0, 4, 1),
    15: (5, 7, 0), 18: (3, 2, 0), 25: (5, 5, 0), 32: (5, 2, 0), 39: (1, 3, 0),
    46: (1, 2, 0), 53: (7, 7, 0)
}

Z_TRACE = [
    1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

def get_knight_moves(x, y, z):
    moves = []
    # 2D moves (Level)
    for dx, dy in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx <= 7 and 0 <= ny <= 7:
            moves.append((nx, ny, z))
    # 3D moves (Up/Down)
    for dz in [-1, 1]:
        nz = z + dz
        if 0 <= nz <= 1:
            for dx, dy in [(0,-2), (0,2), (-2,0), (2,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    moves.append((nx, ny, nz))
    return moves

path = [(0, 0, 1)]
visited_xy = set([(0, 0)])
tower_in_region = {CELL_TO_REGION[(0, 0)]: (0, 0)}
current_score = 0
found_path = None

def dfs(move):
    global current_score, found_path
    
    if found_path is not None:
        return
        
    cx, cy, cz = path[-1]
    
    # Pruning based on Manhattan distance to future checkpoints
    for m_cp, cp in CHECKPOINTS.items():
        if m_cp >= move:
            dist = abs(cx - cp[0]) + abs(cy - cp[1])
            if dist > (m_cp - move + 1) * 3:
                return
            break

    next_moves = get_knight_moves(cx, cy, cz)
    valid_next = 0
    
    for nm in next_moves:
        nx, ny, nz = nm
        
        # A cell (x,y) cannot be visited twice, regardless of Z.
        if (nx, ny) in visited_xy:
            continue
            
        if move < 54:
            if nz != Z_TRACE[move]: continue
        else:
            if nz < cz and (current_score == 0 or current_score % move != 0): continue
            
        if move in CHECKPOINTS and (nx, ny, nz) != CHECKPOINTS[move]:
            continue
            
        r = CELL_TO_REGION[(nx, ny)]
        placed_tower = False
        
        if nz == 1:
            if r in tower_in_region and tower_in_region[r] != (nx, ny): continue
            if r not in tower_in_region:
                tower_in_region[r] = (nx, ny)
                placed_tower = True
        else:
            if r in tower_in_region and tower_in_region[r] == (nx, ny): continue
            
        valid_next += 1
        
        prev_score = current_score
        if nz == cz: current_score += move
        elif nz > cz: current_score *= move
        else: current_score //= move
        
        visited_xy.add((nx, ny))
        path.append(nm)
        
        dfs(move + 1)
        
        path.pop()
        visited_xy.remove((nx, ny))
        current_score = prev_score
        if placed_tower: del tower_in_region[r]
        
    # Stop immediately upon visiting all 13 towers
    if len(tower_in_region) == 13:
        if move > 53: # it went beyond 53 and got trapped
            found_path = list(path)
            return

dfs(1)

if found_path:
    print(f"FOUND STRICT PATH OF LENGTH {len(found_path)}")
    print(found_path)
    
    scores = [0] * len(found_path)
    for m in range(1, len(found_path)):
        pz = found_path[m-1][2]
        cz = found_path[m][2]
        prev_score = scores[m-1]
        if pz == cz: scores[m] = prev_score + m
        elif cz > pz: scores[m] = prev_score * m
        else: scores[m] = prev_score // m
            
    grid_vals = [[[] for _ in range(8)] for _ in range(8)]
    for i, (x, y, z) in enumerate(found_path):
        grid_vals[y][x].append(scores[i])
        
    unvisited_xy = []
    for y in range(8):
        for x in range(8):
            if not grid_vals[y][x]:
                unvisited_xy.append((x, y))
                
    total_ans = 0
    for ux, uy in unvisited_xy:
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = ux + dx, uy + dy
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                for v in grid_vals[ny][nx]:
                    total_ans += v
                    
    print(f"Total unvisited squares: {len(unvisited_xy)}")
    print(f"Final Answer (Sum of Neighbor Sums): {total_ans}")
else:
    print("NO PATH FOUND!")
for ux, uy in unvisited_xy:
    sum_n = 0
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = ux + dx, uy + dy
        if 0 <= nx <= 7 and 0 <= ny <= 7:
            for v in grid_vals[ny][nx]:
                sum_n += v
    print(f"- ({ux}, {uy}) -> Sum = {sum_n}")
