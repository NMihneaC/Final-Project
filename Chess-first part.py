import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (253,245,201)
BLACK = (75,56,50)

# Load piece images
def load_images():
    pieces = ['bp', 'bk', 'bb', 'bq', 'br', 'bn', 'wp', 'wk', 'wb', 'wq', 'wr', 'wn']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(
            pygame.image.load(f'assets/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE)
        )
    return images

# Draw board
def draw_board(win):
    colors = [WHITE, BLACK]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

starting_position = [
    ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
]
def draw_pieces(win, board, images):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                win.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

selected_piece = None  # Stores (row, col) of selected piece
dragging = False  # Tracks if the piece is being moved


# Highlight legal moves (green circles)
def draw_legal_moves(win, legal_moves):
    for move in legal_moves:
        pygame.draw.circle(win, (0, 255, 0),
                           (move[1] * SQUARE_SIZE + SQUARE_SIZE // 2, move[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)


# Legal move checker function
def get_legal_moves(board, row, col, piece):
    legal_moves = []

    directions = {
        'p': [(1, 0), (2, 0)],  # Pawn: forward one or two (if on starting row)
        'n': [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)],  # Knight
        'r': [(0, 1), (0, -1), (1, 0), (-1, 0)],  # Rook: horizontal/vertical
        'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop: diagonals
        'q': [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],  # Queen
        'k': [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # King
    }

    if piece[1] == 'p':
        direction = -1 if piece[0] == 'w' else 1  # White moves down, Black moves up

        # Normal move (1 square forward)
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            legal_moves.append((row + direction, col))

            # First move (2 squares forward), only on starting row
            if (piece[0] == 'w' and row == 6) or (piece[0] == 'b' and row == 1):
                if board[row + 2 * direction][col] is None:
                    legal_moves.append((row + 2 * direction, col))

        # Capture diagonally (only if an enemy piece is there)
        for dx in [-1, 1]:
            new_row, new_col = row + direction, col + dx
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if target_piece and target_piece[0] != piece[0]:  # Check if it's an enemy piece
                    legal_moves.append((new_row, new_col))


    elif piece[1] == 'n':  # Knight
        for dx, dy in directions['n']:
            new_row, new_col = row + dx, col + dy
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col] is None or board[new_row][new_col][0] != piece[0]:
                    legal_moves.append((new_row, new_col))

    elif piece[1] in ['r', 'b', 'q']:  # Rook, Bishop, Queen (Sliding pieces)
        for dx, dy in directions[piece[1]]:
            for step in range(1, 8):  # Move multiple squares in the given direction
                new_row, new_col = row + dx * step, col + dy * step
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board[new_row][new_col] is None:
                        legal_moves.append((new_row, new_col))
                    elif board[new_row][new_col][0] != piece[0]:
                        legal_moves.append((new_row, new_col))
                        break  # Capture, but stop sliding
                    else:
                        break  # Stop if there's a friendly piece
                else:
                    break  # Out of bounds

    elif piece[1] == 'k':  # King
        for dx, dy in directions['k']:
            new_row, new_col = row + dx, col + dy
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col] is None or board[new_row][new_col][0] != piece[0]:
                    legal_moves.append((new_row, new_col))

    return legal_moves