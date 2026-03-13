#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贪吃蛇游戏 - Snake Game
一款画面精美、操作流畅的贪吃蛇游戏
"""

import os
import sys
import logging
import random
import math
import pygame
from pygame import gfxdraw
from datetime import datetime
from pathlib import Path

# ============================================
# 日志系统配置
# ============================================
def setup_logging():
    """配置日志系统"""
    # 获取程序运行目录
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent

    # 创建 logs 目录
    log_dir = base_dir / 'logs'
    log_dir.mkdir(exist_ok=True)

    # 日志文件名包含日期
    log_file = log_dir / f'snake_{datetime.now().strftime("%Y%m%d")}.log'

    # 配置日志格式
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger('SnakeGame')


# 初始化日志
logger = setup_logging()


# ============================================
# 游戏常量配置
# ============================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 颜色配置
COLORS = {
    'bg': (26, 26, 46),           # 深色背景
    'bg_light': (30, 30, 55),     # 稍亮的背景
    'snake_head': (0, 200, 100),  # 蛇头颜色
    'snake_body': (0, 180, 80),   # 蛇身颜色
    'food': (255, 80, 80),        # 食物颜色
    'food_glow': (255, 120, 120), # 食物发光
    'text': (240, 240, 240),      # 主文字
    'text_secondary': (180, 180, 180),  # 次要文字
    'border': (100, 100, 150),    # 边框颜色
    'grid': (40, 40, 60),         # 网格线
}

# 方向
DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
}

# 速度配置 (毫秒)
INITIAL_SPEED = 150
MIN_SPEED = 50
SPEED_INCREMENT = 5

# 最高分文件
HIGH_SCORE_FILE = 'highscore.txt'


# ============================================
# 游戏类
# ============================================
class SnakeGame:
    """贪吃蛇游戏主类"""

    def __init__(self):
        """初始化游戏"""
        logger.info("初始化贪吃蛇游戏")

        # 初始化 pygame
        pygame.init()
        pygame.display.set_caption('贪吃蛇 - Snake Game')

        # 设置字体
        self.font_title = None
        self.font_score = None
        self.font_text = None
        self._init_fonts()

        # 创建屏幕
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.game_state = 'start'  # start, playing, paused, gameover
        self.score = 0
        self.high_score = self._load_high_score()
        self.current_speed = INITIAL_SPEED

        # 蛇和食物
        self.snake = []
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.food = None

        # 动画效果
        self.food_pulse = 0

        # 初始化游戏
        self._init_game()

        logger.info(f"游戏初始化完成，最高分: {self.high_score}")

    def _init_fonts(self):
        """初始化字体"""
        # 尝试使用系统中文字体
        font_names = [
            'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei',
            'Noto Sans CJK SC', 'Source Han Sans SC', 'Droid Sans Fallback'
        ]

        # 先尝试系统中文字体
        system_fonts = pygame.font.get_fonts()
        chinese_font = None

        for font_name in font_names:
            if font_name.lower() in [f.lower() for f in system_fonts]:
                chinese_font = font_name
                break

        if chinese_font:
            try:
                self.font_title = pygame.font.SysFont(chinese_font, 48, bold=True)
                self.font_score = pygame.font.SysFont(chinese_font, 24)
                self.font_text = pygame.font.SysFont(chinese_font, 20)
                logger.info(f"使用中文字体: {chinese_font}")
                return
            except Exception as e:
                logger.warning(f"加载中文字体失败: {e}")

        # 回退到默认字体（使用内置字体）
        try:
            # 尝试加载 pygame 内置字体
            self.font_title = pygame.font.Font(None, 48)
            self.font_score = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 20)
            logger.info("使用默认字体")
        except Exception as e:
            logger.error(f"字体初始化失败: {e}")

    def _load_high_score(self):
        """加载最高分"""
        try:
            if getattr(sys, 'frozen', False):
                score_file = Path(sys.executable).parent / HIGH_SCORE_FILE
            else:
                score_file = Path(__file__).parent / HIGH_SCORE_FILE

            if score_file.exists():
                with open(score_file, 'r', encoding='utf-8') as f:
                    score = int(f.read().strip())
                logger.info(f"加载最高分: {score}")
                return score
        except Exception as e:
            logger.error(f"加载最高分失败: {e}")
        return 0

    def _save_high_score(self):
        """保存最高分"""
        try:
            if getattr(sys, 'frozen', False):
                score_file = Path(sys.executable).parent / HIGH_SCORE_FILE
            else:
                score_file = Path(__file__).parent / HIGH_SCORE_FILE

            with open(score_file, 'w', encoding='utf-8') as f:
                f.write(str(self.high_score))
            logger.info(f"保存最高分: {self.high_score}")
        except Exception as e:
            logger.error(f"保存最高分失败: {e}")

    def _init_game(self):
        """初始化游戏状态"""
        # 蛇初始位置和长度
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.snake = [
            (mid_x, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y)
        ]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.score = 0
        self.current_speed = INITIAL_SPEED

        # 生成第一个食物
        self._spawn_food()

        logger.info("游戏状态已初始化")

    def _spawn_food(self):
        """生成食物"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                logger.debug(f"生成食物位置: ({x}, {y})")
                break

    def _handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("用户关闭游戏")
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("用户按ESC退出")
                    return False

                if self.game_state == 'start':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.game_state = 'playing'
                        logger.info("开始游戏")

                elif self.game_state == 'playing':
                    if event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        self.game_state = 'paused'
                        logger.info("游戏暂停")

                    # 方向控制（防止直接反向）
                    elif event.key == pygame.K_UP and self.direction != 'DOWN':
                        self.next_direction = 'UP'
                    elif event.key == pygame.K_DOWN and self.direction != 'UP':
                        self.next_direction = 'DOWN'
                    elif event.key == pygame.K_LEFT and self.direction != 'RIGHT':
                        self.next_direction = 'LEFT'
                    elif event.key == pygame.K_RIGHT and self.direction != 'LEFT':
                        self.next_direction = 'RIGHT'

                elif self.game_state == 'paused':
                    if event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        self.game_state = 'playing'
                        logger.info("游戏继续")

                elif self.game_state == 'gameover':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self._init_game()
                        self.game_state = 'playing'
                        logger.info("重新开始游戏")

        return True

    def _update(self):
        """更新游戏状态"""
        if self.game_state != 'playing':
            return

        # 更新方向
        self.direction = self.next_direction

        # 计算新的蛇头位置
        head_x, head_y = self.snake[0]
        dx, dy = DIRECTIONS[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # 检查碰撞
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake):
            self._game_over()
            return

        # 移动蛇
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            logger.info(f"吃到食物，当前分数: {self.score}")

            # 速度递增
            if self.current_speed > MIN_SPEED:
                self.current_speed = max(MIN_SPEED, INITIAL_SPEED - (self.score // 50) * SPEED_INCREMENT)
                logger.debug(f"游戏速度: {self.current_speed}ms")

            # 生成新食物
            self._spawn_food()
        else:
            # 没吃到食物，移除尾部
            self.snake.pop()

    def _game_over(self):
        """游戏结束"""
        self.game_state = 'gameover'
        logger.info(f"游戏结束，最终得分: {self.score}")

        # 更新最高分
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
            logger.info(f"新最高分: {self.high_score}")

    def _draw_background(self):
        """绘制背景"""
        self.screen.fill(COLORS['bg'])

        # 绘制网格
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'], (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'], (0, y), (SCREEN_WIDTH, y), 1)

        # 绘制边框
        pygame.draw.rect(self.screen, COLORS['border'], (5, 5, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10), 2)

    def _draw_snake(self):
        """绘制蛇"""
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                x * GRID_SIZE + 2,
                y * GRID_SIZE + 2,
                GRID_SIZE - 4,
                GRID_SIZE - 4
            )

            if i == 0:
                # 蛇头
                color = COLORS['snake_head']
                # 绘制眼睛
                eye_offset = GRID_SIZE // 4
                eye_size = 4

                # 根据方向绘制眼睛
                if self.direction == 'UP':
                    eye_pos = [(x * GRID_SIZE + eye_offset, y * GRID_SIZE + eye_offset),
                               (x * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y * GRID_SIZE + eye_offset)]
                elif self.direction == 'DOWN':
                    eye_pos = [(x * GRID_SIZE + eye_offset, y * GRID_SIZE + GRID_SIZE - eye_offset - eye_size),
                               (x * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)]
                elif self.direction == 'LEFT':
                    eye_pos = [(x * GRID_SIZE + eye_offset, y * GRID_SIZE + eye_offset),
                               (x * GRID_SIZE + eye_offset, y * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)]
                else:  # RIGHT
                    eye_pos = [(x * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y * GRID_SIZE + eye_offset),
                               (x * GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y * GRID_SIZE + GRID_SIZE - eye_offset - eye_size)]

                # 绘制身体
                pygame.draw.rect(self.screen, color, rect, border_radius=4)

                # 绘制眼睛（黑色）
                for ex, ey in eye_pos:
                    pygame.draw.rect(self.screen, (20, 20, 20), (ex, ey, eye_size, eye_size))
            else:
                # 蛇身 - 渐变色
                ratio = i / len(self.snake)
                r = int(COLORS['snake_body'][0] * (1 - ratio * 0.3))
                g = int(COLORS['snake_body'][1] * (1 - ratio * 0.3))
                b = int(COLORS['snake_body'][2] * (1 - ratio * 0.3))
                color = (r, g, b)
                pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def _draw_food(self):
        """绘制食物"""
        if self.food is None:
            return

        x, y = self.food
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # 呼吸效果
        self.food_pulse = (self.food_pulse + 0.15) % (2 * 3.14159)
        pulse_size = int(3 * abs(math.sin(self.food_pulse)))

        # 绘制发光效果
        glow_radius = GRID_SIZE // 2 + 2 + pulse_size
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*COLORS['food_glow'], 50), (glow_radius, glow_radius), glow_radius - 2)
        self.screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))

        # 绘制食物主体
        food_rect = pygame.Rect(
            x * GRID_SIZE + 4,
            y * GRID_SIZE + 4,
            GRID_SIZE - 8,
            GRID_SIZE - 8
        )
        pygame.draw.rect(self.screen, COLORS['food'], food_rect, border_radius=6)

    def _draw_score(self):
        """绘制分数"""
        # 当前分数
        score_text = self.font_score.render(f'分数: {self.score}', True, COLORS['text'])
        self.screen.blit(score_text, (20, 15))

        # 最高分
        high_score_text = self.font_score.render(f'最高分: {self.high_score}', True, COLORS['text_secondary'])
        high_score_rect = high_score_text.get_rect(topright=(SCREEN_WIDTH - 20, 15))
        self.screen.blit(high_score_text, high_score_rect)

    def _draw_start_screen(self):
        """绘制开始界面"""
        # 标题
        title = self.font_title.render('贪吃蛇', True, COLORS['text'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_text.render('Snake Game', True, COLORS['text_secondary'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(subtitle, subtitle_rect)

        # 提示
        prompt = self.font_text.render('按 回车键 或 空格键 开始游戏', True, COLORS['text_secondary'])
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(prompt, prompt_rect)

        # 操作说明
        controls = [
            '方向键: 控制蛇的移动',
            'P 键: 暂停/继续',
            'ESC: 退出游戏'
        ]

        for i, control in enumerate(controls):
            text = self.font_text.render(control, True, COLORS['text_secondary'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100 + i * 25))
            self.screen.blit(text, text_rect)

    def _draw_paused_screen(self):
        """绘制暂停界面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        paused_text = self.font_title.render('游戏暂停', True, COLORS['text'])
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(paused_text, paused_rect)

        # 提示
        prompt = self.font_text.render('按 P 键继续', True, COLORS['text_secondary'])
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(prompt, prompt_rect)

    def _draw_gameover_screen(self):
        """绘制游戏结束界面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        gameover_text = self.font_title.render('游戏结束', True, COLORS['food'])
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(gameover_text, gameover_rect)

        # 最终分数
        score_text = self.font_score.render(f'最终得分: {self.score}', True, COLORS['text'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # 最高分
        if self.score >= self.high_score:
            new_high_text = self.font_text.render('恭喜打破最高分!', True, COLORS['snake_head'])
            new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
            self.screen.blit(new_high_text, new_high_rect)

        # 提示
        prompt = self.font_text.render('按 回车键 或 空格键 重新开始', True, COLORS['text_secondary'])
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(prompt, prompt_rect)

    def run(self):
        """运行游戏主循环"""
        logger.info("游戏主循环开始")

        running = True
        last_update = pygame.time.get_ticks()

        while running:
            # 处理输入
            running = self._handle_input()

            # 更新游戏状态
            current_time = pygame.time.get_ticks()
            if self.game_state == 'playing':
                if current_time - last_update >= self.current_speed:
                    self._update()
                    last_update = current_time

            # 绘制
            self._draw_background()

            if self.game_state in ('playing', 'paused', 'gameover'):
                self._draw_snake()
                self._draw_food()
                self._draw_score()

            if self.game_state == 'start':
                self._draw_start_screen()
            elif self.game_state == 'paused':
                self._draw_paused_screen()
            elif self.game_state == 'gameover':
                self._draw_gameover_screen()

            # 刷新显示
            pygame.display.flip()

            # 控制帧率
            self.clock.tick(60)

        logger.info("游戏主循环结束")
        pygame.quit()
        sys.exit()


# ============================================
# 程序入口
# ============================================
if __name__ == '__main__':
    try:
        logger.info("=" * 50)
        logger.info("启动贪吃蛇游戏")
        logger.info("=" * 50)

        game = SnakeGame()
        game.run()
    except Exception as e:
        logger.exception(f"游戏发生严重错误: {e}")
        sys.exit(1)