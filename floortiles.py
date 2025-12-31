import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
# with some debugging help from Claude

def draw_tile_map(tiles, grid_cols=5):
    colors = ["black", "green", "red", "blue", "grey", "beige"]
    
    grid_rows = (len(tiles) + grid_cols - 1) // grid_cols
    tile_size = 1
    
    fig, ax = plt.subplots(figsize=(grid_cols * 2, grid_rows * 2))
    
    for index, tile in enumerate(tiles):
        row = index // grid_cols
        col = index % grid_cols
        is_vertical = (row + col) % 2 == 1  # Tile 0 is horizontal
        
        x = col * tile_size
        y = (grid_rows - row - 1) * tile_size
        
        if is_vertical:
            # Vertical bars
            for i, color_idx in enumerate(tile):
                ax.add_patch(plt.Rectangle(
                    (x + i*tile_size/4, y), 
                    tile_size/4, tile_size, 
                    color=colors[color_idx]
                ))
        else:
            # Horizontal bars
            for i, color_idx in enumerate(tile):
                ax.add_patch(plt.Rectangle(
                    (x, y + i*tile_size/4), 
                    tile_size, tile_size/4, 
                    color=colors[color_idx]
                ))
    
    ax.set_xlim(0, grid_cols * tile_size)
    ax.set_ylim(0, grid_rows * tile_size)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()



def issafe(vertex, tile, edges_dict, colormap):
    """
    Check if a tile assignment is valid given the adjacency constraints.
    
    Args:
        vertex: The tile position to check
        tile: List of 4 colors [c0, c1, c2, c3] to assign
        edges_dict: Dictionary with keys 'all_to_first', 'first_to_all', 'all_to_last', 'last_to_all'
        colormap: Current color assignments (0 means unassigned)
    
    Returns:
        True if tile can be safely assigned, False otherwise
    """
    
    # Check all_to_first: all 4 bars of current tile touch first bar of neighbor
    for edge in edges_dict['all_to_first']:
        if edge[0] == vertex:  # Current vertex is source
            neighbor = edge[1]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                neighbor_first_bar = colormap[neighbor][0]
                # Check if any of our 4 bars matches neighbor's first bar
                if neighbor_first_bar in tile:
                    return False
        elif edge[1] == vertex:  # Current vertex is target
            neighbor = edge[0]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                our_first_bar = tile[0]
                # Check if our first bar matches any of neighbor's 4 bars
                if our_first_bar in colormap[neighbor]:
                    return False
    
    # Check first_to_all: first bar of current tile touches all 4 bars of neighbor
    for edge in edges_dict['first_to_all']:
        if edge[0] == vertex:  # Current vertex is source
            neighbor = edge[1]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                our_first_bar = tile[0]
                # Check if our first bar matches any of neighbor's 4 bars
                if our_first_bar in colormap[neighbor]:
                    return False
        elif edge[1] == vertex:  # Current vertex is target
            neighbor = edge[0]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                neighbor_first_bar = colormap[neighbor][0]
                # Check if neighbor's first bar matches any of our 4 bars
                if neighbor_first_bar in tile:
                    return False
    
    # Check all_to_last: all 4 bars of current tile touch last bar of neighbor
    for edge in edges_dict['all_to_last']:
        if edge[0] == vertex:  # Current vertex is source
            neighbor = edge[1]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                neighbor_last_bar = colormap[neighbor][3]
                # Check if any of our 4 bars matches neighbor's last bar
                if neighbor_last_bar in tile:
                    return False
        elif edge[1] == vertex:  # Current vertex is target
            neighbor = edge[0]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                our_last_bar = tile[3]
                # Check if our last bar matches any of neighbor's 4 bars
                if our_last_bar in colormap[neighbor]:
                    return False
    
    # Check last_to_all: last bar of current tile touches all 4 bars of neighbor
    for edge in edges_dict['last_to_all']:
        if edge[0] == vertex:  # Current vertex is source
            neighbor = edge[1]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                our_last_bar = tile[3]
                # Check if our last bar matches any of neighbor's 4 bars
                if our_last_bar in colormap[neighbor]:
                    return False
        elif edge[1] == vertex:  # Current vertex is target
            neighbor = edge[0]
            if colormap[neighbor] != 0:  # Neighbor is assigned
                neighbor_last_bar = colormap[neighbor][3]
                # Check if neighbor's last bar matches any of our 4 bars
                if neighbor_last_bar in tile:
                    return False
    
    return True


# Example usage with backtracking:
def solve_coloring(n, tiles_list, edges_dict):
    """
    Solve the tile coloring problem using backtracking.
    
    Args:
        n: Grid size (n x n)
        tiles_list: List of all possible tile configurations
        edges_dict: Edge dictionary from generate_grid_edges()
    
    Returns:
        colormap if solution found, None otherwise
    """
    num_tiles = n * n
    colormap = [0] * num_tiles
    
    def backtrack(vertex):
        if vertex == num_tiles:
            return True  # All tiles assigned successfully
        
        for tile in tiles_list:
            if issafe(vertex, tile, edges_dict, colormap):
                colormap[vertex] = tile
                
                if backtrack(vertex + 1):
                    return True
                
                colormap[vertex] = 0  # Backtrack
        
        return False
    
    if backtrack(0):
        return colormap
    else:
        return None

def generate_grid_edges(n):
    """
    Generate edges for an N-by-N grid where tiles alternate vertical/horizontal.
    Tile 0 is horizontal, then tiles alternate in a checkerboard pattern.
    
    Args:
        n: Size of the grid (n x n tiles)
    
    Returns:
        Dictionary with four edge lists:
        - 'all_to_first': All 4 bars of tile1 touch first bar of tile2
        - 'first_to_all': First bar of tile1 touches all 4 bars of tile2
        - 'all_to_last': All 4 bars of tile1 touch last bar of tile2
        - 'last_to_all': Last bar of tile1 touches all 4 bars of tile2
    """
    all_to_first = []  # All 4 bars touch first bar
    first_to_all = []  # First bar touches all 4 bars
    all_to_last = []   # All 4 bars touch last bar
    last_to_all = []   # Last bar touches all 4 bars
    
    for row in range(n):
        for col in range(n):
            node = row * n + col
            is_vertical = (row + col) % 2 == 1  # Tile 0 is horizontal
            
            if is_vertical:
                # Vertical tile (bars run vertically)
                
                # Right neighbor (horizontal tile)
                if col + 1 < n:
                    neighbor = node + 1
                    # Last bar of vertical touches all bars of horizontal (to the right)
                    last_to_all.append([node, neighbor])
                
                # Left neighbor (horizontal tile)
                if col - 1 >= 0:
                    neighbor = node - 1
                    # First bar of vertical touches all bars of horizontal (to the left)
                    first_to_all.append([node, neighbor])
                
                # Top neighbor (horizontal tile)
                if row - 1 >= 0:
                    neighbor = node - n
                    # All bars of vertical touch last bar of horizontal (above)
                    all_to_last.append([node, neighbor])
                
                # Bottom neighbor (horizontal tile)
                if row + 1 < n:
                    neighbor = node + n
                    # All bars of vertical touch first bar of horizontal (below)
                    all_to_first.append([node, neighbor])
                    
            else:
                # Horizontal tile (bars run horizontally)
                
                # Right neighbor (vertical tile)
                if col + 1 < n:
                    neighbor = node + 1
                    # All bars of horizontal touch first bar of vertical (to the right)
                    all_to_first.append([node, neighbor])
                
                # Left neighbor (vertical tile)
                if col - 1 >= 0:
                    neighbor = node - 1
                    # All bars of horizontal touch last bar of vertical (to the left)
                    all_to_last.append([node, neighbor])
                
                # Top neighbor (vertical tile)
                if row - 1 >= 0:
                    neighbor = node - n
                    # Last bar of horizontal touches all bars of vertical (above)
                    last_to_all.append([node, neighbor])
                
                # Bottom neighbor (vertical tile)
                if row + 1 < n:
                    neighbor = node + n
                    # First bar of horizontal touches all bars of vertical (below)
                    first_to_all.append([node, neighbor])
    
    return {
        'all_to_first': all_to_first,
        'first_to_all': first_to_all,
        'all_to_last': all_to_last,
        'last_to_all': last_to_all
    }

    
tiles = [[3,1,4,5],[5,4,1,3],[3,1,4,2],[2,4,1,3],[3,2,4,1],[1,4,2,3],[4,2,1,3],[3,1,2,4],[2,3,1,4],[4,1,3,2],[2,3,0,4],[4,0,3,2],[2,0,1,5],[5,1,0,2],[0,1,2,5],[5,2,1,0],[2,4,1,3],[3,1,4,2],[3,1,2,5],[5,2,1,3],[3,1,4,5],[5,4,1,3],[3,0,1,5],[5,1,0,3]]
    
edges = generate_grid_edges(10)
colormap = solve_coloring(10, tiles, edges)
draw_tile_map(colormap)
