"""
管道管理器：生成和管理管道障碍物
"""

import pygame
import random
import math
import time

class Pipe:
    def __init__(self, x, screen_height, difficulty_settings, pipe_id, gap_y=None):
        self.id = pipe_id
        self.x = x
        self.screen_height = screen_height
        self.width = 70
        
        # 管道缺口参数
        self.gap_height = difficulty_settings.get("gap_height", 200)  # 缺口高度
        self.min_gap_y = 150
        self.max_gap_y = screen_height - 150
        
        # 随机生成或使用指定的缺口位置
        if gap_y:
            self.gap_y = gap_y
        else:
            random.seed(time.time())
            self.gap_y = random.randint(self.min_gap_y, self.max_gap_y)
        
        # 管道颜色
        self.color = (76, 175, 80)  # 绿色
        self.highlight_color = (56, 142, 60)  # 深绿色边框
        
        # 状态
        self.passed = False
        self.scored = False
    
    def update(self, scroll_speed):
        """更新管道位置"""
        self.x -= scroll_speed
    
    def is_offscreen(self):
        """检查管道是否离开屏幕"""
        return self.x < -self.width
    
    def get_rects(self):
        """获取管道的碰撞矩形"""
        # 上管道
        top_rect = pygame.Rect(
            self.x, 
            0, 
            self.width, 
            self.gap_y - self.gap_height // 2
        )
        
        # 下管道
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + self.gap_height // 2,
            self.width,
            self.screen_height - (self.gap_y + self.gap_height // 2)
        )
        
        return top_rect, bottom_rect
    
    def draw(self, screen):
        """绘制管道"""
        top_rect, bottom_rect = self.get_rects()
        
        # 绘制管道主体
        pygame.draw.rect(screen, self.color, top_rect)
        pygame.draw.rect(screen, self.color, bottom_rect)
        
        # 绘制管道边框
        pygame.draw.rect(screen, self.highlight_color, top_rect, 3)
        pygame.draw.rect(screen, self.highlight_color, bottom_rect, 3)
        
        # 绘制管道顶部/底部装饰
        top_cap = pygame.Rect(self.x - 5, top_rect.bottom - 15, self.width + 10, 15)
        bottom_cap = pygame.Rect(self.x - 5, bottom_rect.top, self.width + 10, 15)
        
        pygame.draw.rect(screen, self.highlight_color, top_cap)
        pygame.draw.rect(screen, self.highlight_color, bottom_cap)
        
        # 绘制管道内部阴影
        top_inner = top_rect.inflate(-6, -6)
        bottom_inner = bottom_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (66, 155, 70), top_inner)
        pygame.draw.rect(screen, (66, 155, 70), bottom_inner)


class PipeManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pipes = []
        self.pipe_spacing = 300
        self.scroll_speed = 2.0
        self.initial_scroll_speed = 2.0
        self.initial_gap_height = 200
        self.pipe_spawn_timer = 0
        self.next_pipe_id = 0

    def get_current_gap_height(self):
        """根据分数计算当前的管道缺口高度"""
        score = self.next_pipe_id
        if score > 10:
            k = -math.log(0.75) / 20
            p = score
            gap_multiplier = 3/5 + (2/5) * math.exp(-k * (p - 10))
            return self.initial_gap_height * gap_multiplier
        else:
            return self.initial_gap_height

    def reset(self):
        self.pipes = []
        self.next_pipe_id = 0
        self.scroll_speed = self.initial_scroll_speed

    def add_pipe(self, settings):
        """根据提供的设置添加一个新管道"""
        pipe_x = settings.get("x", self.screen_width)
        gap_y = settings.get("gap_y") # 可以是 None
        
        difficulty = {"gap_height": settings.get("gap_height", self.get_current_gap_height())}

        new_pipe = Pipe(pipe_x, self.screen_height, difficulty, self.next_pipe_id, gap_y=gap_y)
        self.pipes.append(new_pipe)
        self.next_pipe_id += 1

    def update(self, dt):
        """更新所有管道，并根据时间生成新管道"""
        # 根据滚动速度和间距计算生成新管道的时间
        # time = distance / speed
        # 避免除以零的错误
        if self.scroll_speed > 0:
            pipe_spawn_interval = self.pipe_spacing / self.scroll_speed
        else:
            pipe_spawn_interval = float('inf') # 如果速度为0，则不生成管道

        # 使用计时器来决定何时生成新管道
        self.pipe_spawn_timer += dt
        if self.pipe_spawn_timer > pipe_spawn_interval:
            # 返回需要生成新管道的信号，并重置计时器
            self.pipe_spawn_timer = 0
            current_gap_height = self.get_current_gap_height()
            self.add_pipe({"gap_height": current_gap_height})

        for pipe in self.pipes[:]:
            pipe.update(self.scroll_speed)
            if pipe.is_offscreen():
                self.pipes.remove(pipe)

    def draw(self, screen):
        for pipe in self.pipes:
            pipe.draw(screen)

    def get_next_pipe(self, bird_x):
        for pipe in self.pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None