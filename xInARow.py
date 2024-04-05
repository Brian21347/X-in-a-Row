import pygame  # a library that is used to create a display window
from typing import Any

pygame.init()


# this function is defined here so that the constants BLOCKS and
# WINNING_POINTS are defined at the top along with the other constants
def verified_input(prompt: str, target_type: Any, *criteria: str) -> Any:
    """
    Prompts the user and verifies that the response can be turned into the target type
    and passes the criteria.
    If it does not valid, the user will be prompted again with the prompt

    Note that there can be as many criteria as is needed and that it needs to be a
    conditional statement in the form of a string that will be evaluated.
    (the string should include the_input as it will be evaluated by the eval function)

    Note also that the return type is the type inputted from target_type
    """
    while True:
        the_input = input(prompt)

        try:
            the_input = target_type(the_input)
            for criterion in criteria:
                if not eval(criterion):
                    raise ValueError(f'The criterion "{criterion}" was not meet.')
            return the_input

        except Exception as e:
            print(f'''\
Sorry, "{the_input}" is an invalid input because it failed this criterion:
{e}

Please try again.
                   '''
                  )


print(
    """
The rules of X in a row:

The first person to connect X pieces in a row wins. 
The green circle represents player one's move,
and the red circle represents player two's move.
    """
)

# constants
BLOCKS: int = verified_input(
    'What size do you wish the grid to be? (the grid is a square, enter the side length. ' +
    'Note that the input needs to be between three and 25, inclusive)\n>>>',
    int, '25 >= the_input >= 3'
)
print()
WINNING_POINTS: int = verified_input(
    'How many in a row will be required to win?\n>>>',
    int, f'{BLOCKS} >= the_input >= 3'
)
print()
BOARD_SIZE = int(BLOCKS ** 2)

# display constants
MARGIN = 10
SCREEN = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
pygame.display.set_caption(f'{WINNING_POINTS} in a row!')
img = pygame.image.load("Icon.png")
pygame.display.set_icon(img)
CLOCK = pygame.time.Clock()
FRAME_RATE = 60

# a global variable for order that the moves that have been played
board: list[int] = []  # note that the x and y positions are reversed, it is in the form (y, x)


def main() -> None:
    """The main game loop."""
    block_size = (min(SCREEN.get_size()) - 2 * MARGIN) // BLOCKS
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # checking the move is on screen
                if pos[0] - MARGIN >= block_size * BLOCKS or \
                        pos[1] - MARGIN >= block_size * BLOCKS + MARGIN or \
                        pos[0] <= MARGIN or pos[1] <= MARGIN:
                    continue

                converted_pos = (pos[0] - MARGIN) // block_size * BLOCKS + (
                        pos[1] - MARGIN) // block_size

                if converted_pos not in board:
                    board.append(int(converted_pos))

            elif event.type == pygame.VIDEORESIZE:
                block_size = (min(SCREEN.get_size()) - 2 * MARGIN) // BLOCKS

        # checking for a victory
        victory_condition = check_for_victory()

        # False == 0, so there is that OR condition
        if victory_condition is False or victory_condition != 0:
            if victory_condition:  # victory_condition is True, player one won
                print("Player one won!")

            if victory_condition is False:  # victory_condition is False, player two won
                print("Player one won!")

            if victory_condition is None:
                print("There was a draw!")

            running = False

        # covering the screen with a light yellow color
        SCREEN.fill('#dcb35c')

        # drawing a preview for the next piece
        pos = pygame.mouse.get_pos()
        pos = pos[0] - MARGIN, pos[1] - MARGIN  # removing the margin
        if not (pos[0] >= block_size * BLOCKS or pos[1] >= block_size * BLOCKS
                or pos[0] <= 0 or pos[1] <= 0):
            # centering the position
            converted_pos = (pos[0] // block_size + .5) * block_size + MARGIN, \
                            (pos[1] // block_size + .5) * block_size + MARGIN
            color = 'green' if len(board) % 2 == 0 else 'red'

            # half of the block size minus two (the lines have a width of one,
            # so the minus two is to make sure the circle does not overlap with the lines)
            circle_size = (min(SCREEN.get_size()) - 2 * MARGIN) // BLOCKS / 2 - 2

            # drawing the circle
            pygame.draw.circle(SCREEN, color, converted_pos, circle_size)

        # updating the board
        draw_board(block_size)
        draw_grid()
        pygame.display.update()
        CLOCK.tick(FRAME_RATE)

    print('The game has been ended, this was the board ("o" is player one and "x" is player two):')
    print_board()

    pygame.quit()


def draw_board(block_size) -> None:
    """Draws the board visually."""
    for i, play in enumerate(board):
        converted_play = divmod(play, BLOCKS)
        converted_play = (converted_play[0] + .5) * block_size + MARGIN, \
                         (converted_play[1] + .5) * block_size + MARGIN
        color = 'green' if i % 2 == 0 else 'red'
        circle_size = (min(SCREEN.get_size()) - 2 * MARGIN) // BLOCKS / 2 - 2
        pygame.draw.circle(SCREEN, color, converted_play, circle_size)


def draw_grid() -> None:
    """Draws the grid visually."""
    width, height = SCREEN.get_size()
    grid_side_len = min(width, height) - 2 * MARGIN
    gap_between_lines = grid_side_len // BLOCKS

    # horizontal lines
    for x in range(MARGIN, grid_side_len + MARGIN + 1, gap_between_lines):
        pygame.draw.line(SCREEN, 'black', (x, MARGIN),
                         (x, gap_between_lines * BLOCKS + MARGIN))

    # vertical lines
    for y in range(MARGIN, grid_side_len + MARGIN + 1, gap_between_lines):
        pygame.draw.line(SCREEN, 'black', (MARGIN, y),
                         (gap_between_lines * BLOCKS + MARGIN, y))


def separating_moves() -> tuple[list[int], list[int]]:
    """Separates the moves that the players make."""
    player_one_moves = []
    player_two_moves = []

    for i, move in enumerate(board):
        if i % 2 == 0:
            player_one_moves.append(move)
        else:
            player_two_moves.append(move)

    return player_one_moves, player_two_moves


def check_for_victory() -> int | bool | None:
    """Called each time a move is played, only determines if the last move caused a victory."""
    if len(board) == 0:
        return 0

    if len(board) < WINNING_POINTS:
        return 0

    # only the positive directions, the negatives are checked by negating the positives
    offsets = (
        BLOCKS - 1, BLOCKS + 1,  # diagonals
        BLOCKS, 1  # cardinals
    )

    for offset in offsets:

        # checking in positive and negative directions
        num_in_a_row = num_in_a_row_in_a_dir(offset)
        num_in_a_row += num_in_a_row_in_a_dir(-offset)

        num_in_a_row -= 1  # checks the original move twice, so one needs to be removed

        if num_in_a_row >= WINNING_POINTS:
            return bool(len(board) % 2)
            # True means player 1 won and False means player 2 won

    # 0 means that the game is unfinished and None means that there was a draw
    return None if len(board) == BOARD_SIZE else 0


def num_in_a_row_in_a_dir(offset: int) -> int:
    """Finds the number of pieces that the player who last placed a piece down has in a row."""
    players_moves = separating_moves()[1 - len(board) % 2]
    num_in_a_row = 0
    move = board[-1]

    while move in players_moves:
        num_in_a_row += 1
        """
        Unintended behaviors:
            - If offset was BLOCKS - 1, 2, and the program was checking at position 0, 
                it would check position 2
            - If offset was -BLOCKS + 1, -2, and the program was checking at position 2, 
                it would check position 0
            - If offset was 1 and the program was checking at position 2, it would check position 3
            - If offset was -1 and the program was checking at position 3, it would check position 2

        012
        345
        678
        """
        if offset == BLOCKS - 1 and move % BLOCKS == 1:
            break
        if offset == -BLOCKS + 1 and move % BLOCKS == BLOCKS - 1:
            break
        if offset == 1 and move % BLOCKS == BLOCKS - 1:
            break
        if offset == -1 and move % BLOCKS == 0:
            break

        move += offset

    return num_in_a_row


def print_board() -> None:
    """Prints the board as text."""
    to_display = [['+'] + ['-'] * BLOCKS + ['+']]
    for i in range(BLOCKS):
        to_display.append(['|'])
        for j in range(BLOCKS):
            to_display[-1].append('_')
        to_display[-1].append('|')
    to_display.append(['+'] + ['-'] * BLOCKS + ['+'])

    # changing  underscores to x's or o's if there is a piece at that position
    for i, move in enumerate(board):
        x, y = divmod(move, BLOCKS)
        to_display[y + 1][x + 1] = 'x' if i % 2 else 'o'

    for y in to_display:
        for x in y:
            print(x, end='')
        print()  # creating a new line


if __name__ == '__main__':
    main()
