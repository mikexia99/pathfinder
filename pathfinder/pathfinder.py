import pygame
import queue

WIDTH = 750
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Path Finding Algorithm')
ROWS = 30

YELLOW = (255, 255, 0)          #START
BLUE = (0, 0, 255)              #END
RED = (255, 0, 0)               #VISITED
WHITE = (255, 255, 255)         #CLEAR
BLACK = (0, 0, 0)               #OBSTACLE
GREEN = (0, 255, 0)             #PATH
GREY = (128, 128, 128)          #LINE

DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1)]

class Cell:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
    
    def get_pos(self):
        return self.row, self.col
    
    def visited(self):
        return self.color == RED

    def is_obstacle(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == YELLOW

    def is_end(self):
        return self.color == BLUE
    
    def reset(self):
        self.color = WHITE

    def visit(self):
        self.color = RED
    
    def create_obstacle(self):
        self.color = BLACK
    
    def create_start(self):
        self.color = YELLOW
    
    def create_end(self):
        self.color = BLUE

    def create_path(self):
        self.color = GREEN
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        for d in DIRECTIONS:
            row_inc, col_inc = d

            if (self.row + row_inc < ROWS and self.col + col_inc < ROWS 
                and self.row + row_inc >= 0 and self.col + col_inc >= 0 
                and not grid[self.row + row_inc][self.col + col_inc].is_obstacle()):

                self.neighbors.append(grid[self.row + row_inc][self.col + col_inc])
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(prev_paths, draw):
    while len(prev_paths) > 0:
        curr = prev_paths.pop()
        curr.create_path()
        draw()

def astar(draw, grid, start, end):

    count = 0
    pq = queue.PriorityQueue()
    pq.put((0, count, [start]))
    cost = {cell: float('inf') for row in grid for cell in row}
    cost[start] = 0
    future_cost = {cell: float('inf') for row in grid for cell in row}
    future_cost[start] = h(start.get_pos(), end.get_pos())

    visited = {start}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        prev_paths = pq.get()[2]

        curr = prev_paths[-1]

        if curr == end:
            reconstruct_path(prev_paths[1:-1], draw)
            return True

        for neighbor in curr.neighbors:

            curr_cost = cost[curr] + 1

            if curr_cost < cost[neighbor]:
                cost[neighbor] = curr_cost
                future_cost[neighbor] = curr_cost + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in visited:
                    count += 1
                    pq.put((future_cost[neighbor], count, prev_paths + [neighbor]))
                    visited.add(neighbor)
        draw()
        if curr != start:
            curr.visit()
    
    return False

def make_grid(width):
    grid = []
    gap = width // ROWS

    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            cell = Cell(i, j, gap)
            grid[i].append(cell)

    return grid


def draw_grid(win, width):
    gap = width // ROWS
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(ROWS):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, width):
    win.fill(WHITE)

    for row in grid:
        for cell in row:
            cell.draw(win)

    draw_grid(win, width)
    pygame.display.update()

def get_clicked_pos(pos, width):
    gap = width // ROWS
    y, x = pos

    if x >= width or x < 0 or y >= width or y < 0:
        return None, None

    row = y // gap
    col = x // gap

    return row, col

def main(win, width):
    grid = make_grid(width)
    start = None
    end = None
    run = True
    started = False

    while run:
        draw(win, grid, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, width)

                if row != None and col != None:

                    cell = grid[row][col]

                    if not start and cell != end:
                        start = cell
                        start.create_start()

                    elif not end and cell != start:
                        end = cell
                        end.create_end()

                    elif cell != end and cell != start:
                        cell.create_obstacle()
            
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, width)
                
                cell = grid[row][col]
                cell.reset()

                if cell == start:
                    start = None
                elif cell == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for cell in row:
                            cell.update_neighbors(grid)
                        
                    astar(lambda: draw(win, grid, width), grid, start, end)

                if event.key == pygame.K_RETURN:
                    start = None
                    end = None
                    grid = make_grid(width)

    pygame.quit()

main(WIN, WIDTH)