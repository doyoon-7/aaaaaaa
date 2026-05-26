import pygame
import random
import sys

# 초기화
pygame.init()

# 색상 정의
BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
GRAY     = (40,  40,  40)
DARK     = (15,  15,  25)
CYAN     = (0,   240, 240)
YELLOW   = (240, 240, 0)
MAGENTA  = (200, 0,   200)
RED      = (240, 30,  30)
GREEN    = (30,  220, 30)
BLUE     = (30,  100, 240)
ORANGE   = (240, 140, 0)
GHOST    = (80,  80,  100)

# 화면 설정
CELL = 32
COLS = 10
ROWS = 20
PANEL = 200
W = COLS * CELL + PANEL
H = ROWS * CELL
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("TETRIS")
clock = pygame.time.Clock()

# 폰트
try:
    font_big   = pygame.font.SysFont("monospace", 36, bold=True)
    font_mid   = pygame.font.SysFont("monospace", 22, bold=True)
    font_small = pygame.font.SysFont("monospace", 16)
except:
    font_big   = pygame.font.Font(None, 36)
    font_mid   = pygame.font.Font(None, 22)
    font_small = pygame.font.Font(None, 16)

# 테트로미노 정의 (모양, 색상)
PIECES = [
    # I
    {"shape": [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], "color": CYAN},
    # O
    {"shape": [[1,1],[1,1]], "color": YELLOW},
    # T
    {"shape": [[0,1,0],[1,1,1],[0,0,0]], "color": MAGENTA},
    # S
    {"shape": [[0,1,1],[1,1,0],[0,0,0]], "color": GREEN},
    # Z
    {"shape": [[1,1,0],[0,1,1],[0,0,0]], "color": RED},
    # J
    {"shape": [[1,0,0],[1,1,1],[0,0,0]], "color": BLUE},
    # L
    {"shape": [[0,0,1],[1,1,1],[0,0,0]], "color": ORANGE},
]

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def new_piece():
    p = random.choice(PIECES)
    shape = [row[:] for row in p["shape"]]
    return {"shape": shape, "color": p["color"], "x": COLS//2 - len(shape[0])//2, "y": 0}

def valid(board, piece, ox=0, oy=0, shape=None):
    s = shape if shape else piece["shape"]
    for r, row in enumerate(s):
        for c, cell in enumerate(row):
            if cell:
                nx, ny = piece["x"] + c + ox, piece["y"] + r + oy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def place(board, piece):
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell:
                board[piece["y"] + r][piece["x"] + c] = piece["color"]

def clear_lines(board):
    full = [i for i, row in enumerate(board) if all(row)]
    for i in full:
        board.pop(i)
        board.insert(0, [None] * COLS)
    return len(full)

def ghost_y(board, piece):
    gy = piece["y"]
    while valid(board, piece, 0, gy - piece["y"] + 1):
        gy += 1
    return gy

def draw_cell(surface, x, y, color, size=CELL, offset_x=0, offset_y=0, alpha=255):
    rect = pygame.Rect(offset_x + x * size, offset_y + y * size, size - 1, size - 1)
    if alpha < 255:
        s = pygame.Surface((size-1, size-1), pygame.SRCALPHA)
        s.fill((*color, alpha))
        surface.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surface, color, rect)
        # 하이라이트
        pygame.draw.rect(surface, tuple(min(v+60,255) for v in color), (rect.x, rect.y, rect.w, 3))
        pygame.draw.rect(surface, tuple(min(v+40,255) for v in color), (rect.x, rect.y, 3, rect.h))

def draw_board(surface, board):
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if cell:
                draw_cell(surface, c, r, cell)
            else:
                pygame.draw.rect(surface, GRAY, (c*CELL, r*CELL, CELL-1, CELL-1), 1)

def draw_piece(surface, piece, oy=None):
    y_base = oy if oy is not None else piece["y"]
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell and y_base + r >= 0:
                draw_cell(surface, piece["x"] + c, y_base + r, piece["color"])

def draw_ghost(surface, board, piece):
    gy = ghost_y(board, piece)
    if gy != piece["y"]:
        for r, row in enumerate(piece["shape"]):
            for c, cell in enumerate(row):
                if cell and gy + r >= 0:
                    draw_cell(surface, piece["x"] + c, gy + r, GHOST)

def draw_preview(surface, piece_data, px, py):
    shape = piece_data["shape"]
    color = piece_data["color"]
    size = 22
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, color, (px + c*size, py + r*size, size-2, size-2))

def draw_panel(surface, score, level, lines, next_piece):
    ox = COLS * CELL
    pygame.draw.rect(surface, (20, 20, 35), (ox, 0, PANEL, H))
    pygame.draw.line(surface, (60, 60, 90), (ox, 0), (ox, H), 2)

    def label(text, x, y, font=font_small, color=WHITE):
        s = font.render(text, True, color)
        surface.blit(s, (x, y))

    label("TETRIS", ox+20, 15, font_big, CYAN)
    pygame.draw.line(surface, CYAN, (ox+10, 55), (ox+PANEL-10, 55), 1)

    label("SCORE", ox+15, 75, font_small, (150,150,200))
    label(str(score), ox+15, 93, font_mid, WHITE)

    label("LEVEL", ox+15, 135, font_small, (150,150,200))
    label(str(level), ox+15, 153, font_mid, WHITE)

    label("LINES", ox+15, 195, font_small, (150,150,200))
    label(str(lines), ox+15, 213, font_mid, WHITE)

    label("NEXT", ox+15, 265, font_small, (150,150,200))
    pygame.draw.rect(surface, (30,30,50), (ox+10, 285, PANEL-20, 100))
    draw_preview(surface, next_piece, ox+30, 295)

    label("← → 이동", ox+12, 405, font_small, (120,120,160))
    label("↑  회전",   ox+12, 422, font_small, (120,120,160))
    label("↓  소프트",  ox+12, 439, font_small, (120,120,160))
    label("SPC 하드드롭", ox+12, 456, font_small, (120,120,160))
    label("P   일시정지", ox+12, 473, font_small, (120,120,160))

def overlay(text, subtext=""):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 160))
    screen.blit(s, (0, 0))
    t1 = font_big.render(text, True, CYAN)
    screen.blit(t1, (W//2 - t1.get_width()//2, H//2 - 50))
    if subtext:
        t2 = font_mid.render(subtext, True, WHITE)
        screen.blit(t2, (W//2 - t2.get_width()//2, H//2 + 10))
    pygame.display.flip()

def level_speed(level):
    return max(80, 800 - (level - 1) * 70)

def main():
    board = [[None]*COLS for _ in range(ROWS)]
    piece = new_piece()
    next_p = new_piece()
    score = 0
    level = 1
    total_lines = 0
    fall_timer = 0
    paused = False
    game_over = False

    LINE_SCORES = [0, 100, 300, 500, 800]

    # 시작 화면
    screen.fill(DARK)
    overlay("TETRIS", "아무 키나 눌러 시작!")
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                waiting = False

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        main()
                        return
                    continue

                if event.key == pygame.K_p:
                    paused = not paused

                if paused:
                    continue

                if event.key == pygame.K_LEFT:
                    if valid(board, piece, -1, 0):
                        piece["x"] -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid(board, piece, 1, 0):
                        piece["x"] += 1
                elif event.key == pygame.K_UP:
                    rotated = rotate(piece["shape"])
                    if valid(board, piece, 0, 0, rotated):
                        piece["shape"] = rotated
                    elif valid(board, piece, 1, 0, rotated):
                        piece["shape"] = rotated; piece["x"] += 1
                    elif valid(board, piece, -1, 0, rotated):
                        piece["shape"] = rotated; piece["x"] -= 1
                elif event.key == pygame.K_DOWN:
                    if valid(board, piece, 0, 1):
                        piece["y"] += 1
                        score += 1
                elif event.key == pygame.K_SPACE:
                    gy = ghost_y(board, piece)
                    score += (gy - piece["y"]) * 2
                    piece["y"] = gy
                    place(board, piece)
                    cleared = clear_lines(board)
                    total_lines += cleared
                    score += LINE_SCORES[cleared] * level
                    level = total_lines // 10 + 1
                    piece = next_p
                    next_p = new_piece()
                    if not valid(board, piece, 0, 0):
                        game_over = True

        if paused:
            overlay("일시정지", "P 키로 재개")
            continue

        if game_over:
            overlay("GAME OVER", f"점수: {score}   R키로 재시작")
            continue

        # 낙하
        fall_timer += dt
        speed = level_speed(level)
        if fall_timer >= speed:
            fall_timer = 0
            if valid(board, piece, 0, 1):
                piece["y"] += 1
            else:
                place(board, piece)
                cleared = clear_lines(board)
                total_lines += cleared
                score += LINE_SCORES[cleared] * level
                level = total_lines // 10 + 1
                piece = next_p
                next_p = new_piece()
                if not valid(board, piece, 0, 0):
                    game_over = True

        # 그리기
        screen.fill(DARK)
        draw_board(screen, board)
        draw_ghost(screen, board, piece)
        draw_piece(screen, piece)
        draw_panel(screen, score, level, total_lines, next_p)
        pygame.display.flip()

if __name__ == "__main__":
    main()
