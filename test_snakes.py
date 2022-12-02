import pytest

import snakes
from snakes import Snake, SnakeBody, SnakeHead, Frame, Cardinal, Apple, Position, GameOver
from typing import Deque


@pytest.mark.parametrize("direction, expected_xy", (
    (Cardinal.UP, (1, 2)),
    (Cardinal.DOWN, (1, 0)),
    (Cardinal.LEFT, (0, 1)),
    (Cardinal.RIGHT, (2, 1)),
))
def test_move_direction(direction, expected_xy):
    frame = Frame(Snake(SnakeHead(Position(1,1), direction), []), None, 3, 3)
    expected = Frame(Snake(SnakeHead(Position(*expected_xy), direction), []), None, 3, 3)
    assert snakes.next_frame(frame=frame, player_input=None) == expected


@pytest.mark.parametrize("starting_direction, input_direction, expected_direction, expected_xy", (
    (Cardinal.UP, Cardinal.UP, Cardinal.UP, (1, 2)),
    (Cardinal.UP, Cardinal.LEFT, Cardinal.LEFT, (0, 1)),
    (Cardinal.UP, Cardinal.RIGHT, Cardinal.RIGHT, (2, 1)),
    (Cardinal.UP, Cardinal.DOWN, Cardinal.UP, (1, 2)),  # invalid change direction
    (Cardinal.DOWN, Cardinal.UP, Cardinal.DOWN, (1, 0)),  # invalid change direction
    (Cardinal.DOWN, Cardinal.RIGHT, Cardinal.RIGHT, (2, 1)),
    (Cardinal.LEFT, Cardinal.RIGHT, Cardinal.LEFT, (0, 1)),  # invalid change direction
    (Cardinal.RIGHT, Cardinal.LEFT, Cardinal.RIGHT, (2, 1)),  # invalid change direction
))
def test_direction_change(starting_direction, input_direction, expected_direction, expected_xy):
    frame = Frame(Snake(SnakeHead(Position(1,1), starting_direction), []), None, 3, 3)
    expected = Frame(Snake(SnakeHead(Position(*expected_xy), expected_direction), []), None, 3, 3)
    assert snakes.next_frame(frame=frame, player_input=input_direction) == expected


@pytest.mark.parametrize("direction", (
    Cardinal.UP,
    Cardinal.DOWN,
    Cardinal.LEFT,
    Cardinal.RIGHT,
))
def test_edge_detection(direction):
    frame = Frame(Snake(SnakeHead(Position(0,0), direction), []), None, 1, 1)
    with pytest.raises(GameOver):
        snakes.next_frame(frame=frame, player_input=None)


@pytest.mark.parametrize("snake_body, expected_body", (
    (
        [SnakeBody(Position(0,7))],
        [SnakeBody(Position(0,8))]
    ),
    (
        [SnakeBody(Position(0,7)), SnakeBody(Position(1,7))],
        [SnakeBody(Position(0,8)), SnakeBody(Position(0,7))]
    ),
))
def test_move_body(snake_body, expected_body):
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 8), Cardinal.UP), body=Deque(snake_body)), apple=None, width=5, height=10)
    expected_frame = Frame(snake=Snake(head=SnakeHead(Position(0, 9), Cardinal.UP), body=Deque(expected_body)), apple=None, width=5, height=10)
    assert snakes.next_frame(frame, None) == expected_frame


def test_eat_apple():
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 7), Cardinal.UP), body=Deque([SnakeBody(Position(0,6))])), apple=Apple(Position(0, 8)), width=5, height=10)
    expected_frame = Frame(snake=Snake(head=SnakeHead(Position(0, 8), Cardinal.UP), body=Deque([SnakeBody(Position(0, 7)), SnakeBody(Position(0,6))])), apple=None, width=5, height=10)
    assert snakes.next_frame(frame, None) == expected_frame