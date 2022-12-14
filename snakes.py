import dataclasses
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Deque

class Cardinal(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


@dataclass
class Position:
    x: int
    y: int

    def as_tuple(self):
        return self.x, self.y


@dataclass
class Entity:
    pos: Position


@dataclass
class SnakeHead(Entity):
    facing: Cardinal


@dataclass
class SnakeBody(Entity):
    pass


@dataclass
class Snake:
    head: SnakeHead
    body: Deque[SnakeBody]


@dataclass
class Apple(Entity):
    pass


@dataclass
class Frame:
    snake: Snake
    apple: Optional[Apple]
    width: int
    height: int


STD_WIDTH = 80
STD_HEIGHT = 20
BORING_FRAME = Frame(Snake(SnakeHead(Position(0,0), Cardinal.UP), Deque()), Apple(Position(STD_WIDTH - 1, STD_HEIGHT - 1)), STD_WIDTH, STD_HEIGHT)

def head_char(cardinal: Cardinal) -> str:
    if cardinal == Cardinal.UP:
        return "ꜛ"
    elif cardinal == Cardinal.DOWN:
        return "↓"
    elif cardinal == Cardinal.RIGHT:
        return "→"
    elif cardinal == Cardinal.LEFT:
        return "←"
    else:
        raise Exception("Unknown Cardinal")

def char_to_cardinal(c: str) -> Optional[Cardinal]:
        if c == "ꜛ":
            return Cardinal.UP
        elif c == "↓":
            return Cardinal.DOWN
        elif c == "→":
            return Cardinal.RIGHT
        elif c == "←":
            return Cardinal.LEFT
        else:
            raise Exception("Unknown Cardinal")

def draw_frame(frame: Frame) -> List[str]:
    frame_chars: List[List[str]] = [[" " for _ in range(frame.width)] for _ in range(frame.height)]
    x,y = frame.snake.head.pos.as_tuple()
    c = head_char(frame.snake.head.facing)
    frame_chars[y][x] = c

    for body in frame.snake.body:
        x,y = body.pos.as_tuple()
        frame_chars[y][x] = "+"
    
    if frame.apple:
        x,y = frame.apple.pos.as_tuple()
        frame_chars[y][x] = "*"
    
    frame_chars.reverse()
    rows = ["".join(row) for row in frame_chars]
    return rows


def parse_frame(lines: str) -> Frame:
    rows = lines.split("\n")
    rows.reverse()
    snake_head = None
    snake_body = []
    apple = None
    height = len(rows)
    width = len(rows[0])
    for y, row in enumerate(rows):
        for x, col in enumerate(row):
            if col == ' ':
                # Nothing
                continue
            elif col == "*":
                # Apple
                apple = Apple(Position(x, y))
            elif col == "+":
                # Body
                snake_body.append(SnakeBody(Position(x, y)))
            else:
                # Head
                facing = char_to_cardinal(col)
                snake_head = SnakeHead(Position(x, y), facing)
    
    if snake_head is None:
        raise Exception("No snake head found")

    return Frame(Snake(snake_head, snake_body), apple, width, height)


with open('rendered_frame.txt', 'r') as f:
    BORING_RENDERED_FRAME = f.read()


if __name__ == "__main__":
    print("\n".join(draw_frame(BORING_FRAME)))
    print(parse_frame(BORING_RENDERED_FRAME))


class GameOver(Exception):
    pass

class HitEdgeOfScreen(GameOver):
    pass

class BitYourOwnTail(GameOver):
    pass

## Assumptions:
# The snake moves every frame
# If the snake *can* change to the direction of the player input it does so
# The snake changes direction *before* it moves
#
# The snake eats an apple like so, on the frame where the snake head would move
# onto the apple, we remove the apple from the frame and inject an additional body
# segment into the tail
#  --> a
#  -->a
#  --->

# Hitting my own tail, we won't count it as a hit if you move
# onto the same square as your tail moved out of in the same frame
#     |
# --> |
# |----

#     
# --->|
# |----

# ---->
# |----
def next_frame(frame: Frame, player_input: Optional[Cardinal]) -> Frame:
    if player_input is not None and is_legal_input(frame.snake.head.facing, player_input):
        frame.snake.head.facing = player_input
    
    snake_direction = frame.snake.head.facing

    old_head_pos = dataclasses.replace(frame.snake.head.pos)

    if snake_direction == Cardinal.UP:
        frame.snake.head.pos.y += 1
    if snake_direction == Cardinal.DOWN:
        frame.snake.head.pos.y -= 1
    if snake_direction == Cardinal.RIGHT:
        frame.snake.head.pos.x += 1
    if snake_direction == Cardinal.LEFT:
        frame.snake.head.pos.x -= 1
    

    
    head_on_apple = frame.apple and frame.snake.head.pos == frame.apple.pos

    if head_on_apple or frame.snake.body:
        tail = SnakeBody(old_head_pos)
        frame.snake.body.appendleft(tail)
        
    # Do we want to refactor this some more in particular the elif is necesasary
    # because we should only pop the tail if we did not inject the neck
    if head_on_apple:
        frame.apple.pos = new_apple_position(frame)
    elif frame.snake.body:
        frame.snake.body.pop()

    
    new_x,new_y = frame.snake.head.pos.as_tuple()
    if new_x < 0:
        raise HitEdgeOfScreen
    if new_x >= frame.width:
        raise HitEdgeOfScreen
    if new_y < 0:
        raise HitEdgeOfScreen
    if new_y >= frame.height:
        raise HitEdgeOfScreen
    if frame.snake.head.pos in (segment.pos for segment in frame.snake.body):
        raise BitYourOwnTail

    return frame


def is_legal_input(current_facing: Cardinal, player_input: Cardinal):
    # Disallow 180 degree turns. 
    # This works because the difference between up/down and left/right is always 2.
    return abs(current_facing.value - player_input.value) != 2


def new_apple_position(frame: Frame) -> Position:
    all_positions = {(x,y) for x in range(frame.width) for y in range(frame.height)}
    valid_positions = all_positions - {segment.pos.as_tuple() for segment in frame.snake.body}
    valid_positions.remove(frame.snake.head.pos.as_tuple())

    return Position(*random.choice(tuple(valid_positions)))
