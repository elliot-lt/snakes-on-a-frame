import pytest
from pytest_mock import MockerFixture

import snakes
from snakes import Snake, SnakeBody, SnakeHead, Frame, Cardinal, Apple, Position, GameOver, BitYourOwnTail, HitEdgeOfScreen
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
    with pytest.raises(HitEdgeOfScreen):
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


def test_eat_apple__snake_grows(mocker: MockerFixture):
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 7), Cardinal.UP), body=Deque([SnakeBody(Position(0,6))])), apple=Apple(Position(0, 8)), width=5, height=10)
    expected_frame = Frame(snake=Snake(head=SnakeHead(Position(0, 8), Cardinal.UP), body=Deque([SnakeBody(Position(0, 7)), SnakeBody(Position(0,6))])), apple=mocker.ANY, width=5, height=10)
    assert snakes.next_frame(frame, None) == expected_frame

# A
# HT

# HA
# TT
def test_eat_apple__apple_respawns_on_free_space(mocker: MockerFixture):
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 0), Cardinal.UP), body=Deque([SnakeBody(Position(1,0))])), apple=Apple(Position(0, 1)), width=2, height=2)
    next_frame = snakes.next_frame(frame, None)
    assert isinstance(next_frame.apple, Apple)
    assert next_frame.apple.pos == Position(1, 1)
    assert next_frame.snake.head.pos == Position(0, 1)

# ATT
# HT

# HTT
# TTA
def test_eat_apple__apple_respawns_on_free_space_3_by_3(mocker: MockerFixture):
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 0), Cardinal.UP), body=Deque([SnakeBody(Position(1,0)), SnakeBody(Position(1,1)), SnakeBody(Position(2,1))])), apple=Apple(Position(0, 1)), width=3, height=2)
    next_frame = snakes.next_frame(frame, None)
    assert isinstance(next_frame.apple, Apple)
    assert next_frame.apple.pos == Position(2, 0)
    assert next_frame.snake.head.pos == Position(0, 1)


# TT
# HTT (facing RIGHT)
def test_hitting_tail_game_over():
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 0), Cardinal.DOWN), body=Deque([SnakeBody(Position(0, 1)), SnakeBody(Position(1,1)), SnakeBody(Position(1,0)), SnakeBody(Position(2,0))])), apple=None, width=5, height=10)
    with pytest.raises(BitYourOwnTail):
        snakes.next_frame(frame=frame, player_input=Cardinal.RIGHT)

# TT
# HT (facing RIGHT)
def test_tail_moves_just_in_time():
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 0), Cardinal.DOWN), body=Deque([SnakeBody(Position(0, 1)), SnakeBody(Position(1,1)), SnakeBody(Position(1,0))])), apple=None, width=5, height=10)
    expected = Frame(snake=Snake(head=SnakeHead(Position(1, 0), Cardinal.RIGHT), body=Deque([SnakeBody(Position(0,0)), SnakeBody(Position(0, 1)), SnakeBody(Position(1,1))])), apple=None, width=5, height=10)
    assert snakes.next_frame(frame=frame, player_input=Cardinal.RIGHT) == expected


# AT
# HT
@pytest.mark.xfail(raises=IndexError, reason="We don't handle no valid spaces for the next apple, implement next time")
def test_eat_apple__apple_cannot_respawn(mocker: MockerFixture):
    frame = Frame(snake=Snake(head=SnakeHead(Position(0, 0), Cardinal.UP), body=Deque([SnakeBody(Position(1,0)), SnakeBody(Position(1,1))])), apple=Apple(Position(0, 1)), width=2, height=2)
    with pytest.raises(GameOver):
        snakes.next_frame(frame, None)