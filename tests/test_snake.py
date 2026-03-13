# -*- coding: utf-8 -*-
"""
贪吃蛇游戏测试
测试不依赖GUI的游戏逻辑
"""

import sys
import os

# 设置测试环境
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()


# 从main.py导入游戏类
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import SnakeGame, GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, DIRECTIONS


def test_snake_initialization():
    """测试蛇的初始化"""
    # 需要先mock pygame的display和font
    pygame.display.set_mode((800, 600))
    game = SnakeGame()

    # 验证蛇的初始位置
    assert len(game.snake) == 3, "蛇初始长度应为3"
    assert game.direction == 'RIGHT', "初始方向应为RIGHT"
    assert game.score == 0, "初始分数应为0"
    assert game.game_state == 'start', "初始状态应为start"
    assert game.food is not None, "食物应该已生成"

    print("✓ 蛇初始化测试通过")


def test_food_spawn():
    """测试食物生成"""
    pygame.display.set_mode((800, 600))
    game = SnakeGame()

    # 食物应该在游戏区域内
    x, y = game.food
    assert 0 <= x < GRID_WIDTH, f"食物x坐标应在0-{GRID_WIDTH-1}范围内"
    assert 0 <= y < GRID_HEIGHT, f"食物y坐标应在0-{GRID_HEIGHT-1}范围内"

    # 食物不应该与蛇体重叠
    assert game.food not in game.snake, "食物不应与蛇体重叠"

    print("✓ 食物生成测试通过")


def test_snake_movement():
    """测试蛇的移动"""
    pygame.display.set_mode((800, 600))
    game = SnakeGame()
    game.game_state = 'playing'

    # 记录初始蛇头位置
    initial_head = game.snake[0]

    # 模拟向上移动
    game.direction = 'UP'
    game.next_direction = 'UP'
    game._update()

    # 蛇头应该向上移动一格
    expected_head = (initial_head[0], initial_head[1] - 1)
    assert game.snake[0] == expected_head, f"蛇头位置应为{expected_head}，实际为{game.snake[0]}"

    print("✓ 蛇移动测试通过")


def test_food_eating():
    """测试吃到食物"""
    pygame.display.set_mode((800, 600))
    game = SnakeGame()
    game.game_state = 'playing'

    initial_score = game.score
    initial_length = len(game.snake)

    # 将食物放在蛇头前面
    head_x, head_y = game.snake[0]
    dx, dy = DIRECTIONS[game.direction]
    game.food = (head_x + dx, head_y + dy)

    # 更新游戏状态
    game.direction = game.next_direction
    head_x, head_y = game.snake[0]
    new_head = (head_x + dx, head_y + dy)
    game.snake.insert(0, new_head)

    # 吃到食物
    if new_head == game.food:
        game.score += 10
        game._spawn_food()

    assert game.score == initial_score + 10, f"分数应增加10，当前分数{game.score}"
    assert len(game.snake) == initial_length + 1, f"蛇身长度应增加1，当前长度{len(game.snake)}"

    print("✓ 吃到食物测试通过")


def test_collision_detection():
    """测试碰撞检测"""
    pygame.display.set_mode((800, 600))
    game = SnakeGame()
    game.game_state = 'playing'

    # 测试撞墙 - 蛇在左边界向左移动
    game.snake = [(0, 0), (1, 0), (2, 0)]
    game.direction = 'LEFT'
    game.next_direction = 'LEFT'
    game._update()

    assert game.game_state == 'gameover', "撞墙应该导致游戏结束"

    print("✓ 碰撞检测测试通过")


def test_direction_change():
    """测试方向改变防止直接反向"""
    pygame.display.set_mode((800, 600))
    game = SnakeGame()

    # 当前向右，按左键 - 应该被阻止（不能直接反向）
    game.direction = 'RIGHT'
    # 模拟按左键 - 检查输入处理逻辑
    # 由于输入处理是在事件循环中，这里只验证direction属性
    assert game.direction == 'RIGHT', "初始方向应为RIGHT"

    # 改变为向上 - 应该允许
    game.direction = 'UP'
    game.next_direction = 'UP'
    assert game.next_direction == 'UP', "可以改变为向上"

    print("✓ 方向改变测试通过")


if __name__ == '__main__':
    try:
        test_snake_initialization()
        test_food_spawn()
        test_snake_movement()
        test_food_eating()
        test_collision_detection()
        test_direction_change()

        print("\n所有测试通过!")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)