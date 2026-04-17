"""
道具系统：护盾道具、翻倍道具
"""

import pygame
import random
import math


class Powerup:
    def __init__(self, x, y, powerup_type="invincible"):
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.radius = 20
        self.active = True
        
        # 动画效果
        self.rotation = 0
        self.pulse_offset = 0
        self.glow_intensity = 0
        
        # 道具样式
        if powerup_type == "invincible":
            self.color = (100, 200, 255)  # 浅蓝色
            self.border_color = (50, 150, 255)  # 深蓝色
        elif powerup_type == "double_score":
            self.color = (255, 215, 0)  # 金色
            self.border_color = (255, 165, 0)  # 橙色
            self.font = pygame.font.Font(None, 24)
            self.text = self.font.render("x2", True, (255, 255, 255))
    
    def update(self, dt):
        """更新道具动画效果"""
        if self.active:
            self.rotation += 100 * dt  # 旋转速度
            self.pulse_offset = math.sin(pygame.time.get_ticks() / 200) * 3
            self.glow_intensity = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2
    
    def draw(self, screen):
        """绘制道具"""
        if not self.active:
            return

        if self.powerup_type == "invincible":
            self.draw_shield(screen)
        elif self.powerup_type == "double_score":
            self.draw_double_score(screen)

    def draw_shield(self, screen):
        """绘制护盾道具"""
        current_radius = self.radius + self.pulse_offset
        
        # 绘制外层光晕
        for i in range(3):
            glow_radius = current_radius + 8 + i * 4
            alpha = int(50 * self.glow_intensity * (1 - i / 3))
            glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha), 
                             (int(glow_radius), int(glow_radius)), 
                             int(glow_radius))
            screen.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))
        
        # 绘制主体护盾圆形
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(current_radius))
        pygame.draw.circle(screen, self.border_color, (int(self.x), int(self.y)), int(current_radius), 3)
        
        # 绘制护盾图案 - 六边形
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            px = self.x + math.cos(angle) * (current_radius - 5)
            py = self.y + math.sin(angle) * (current_radius - 5)
            points.append((px, py))
        
        pygame.draw.polygon(screen, self.border_color, points, 2)
        
        # 绘制内部交叉线条
        for i in range(3):
            angle = math.radians(self.rotation + i * 60)
            start_x = self.x + math.cos(angle) * (current_radius - 8)
            start_y = self.y + math.sin(angle) * (current_radius - 8)
            end_x = self.x + math.cos(angle + math.pi) * (current_radius - 8)
            end_y = self.y + math.sin(angle + math.pi) * (current_radius - 8)
            pygame.draw.line(screen, self.border_color, (start_x, start_y), (end_x, end_y), 1)
        
        # 绘制中心小圆
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(screen, self.border_color, (int(self.x), int(self.y)), 4, 1)

    def draw_double_score(self, screen):
        """绘制翻倍得分道具"""
        current_radius = self.radius + self.pulse_offset

        # 绘制外层光晕
        for i in range(3):
            glow_radius = current_radius + 5 + i * 3
            alpha = int(60 * self.glow_intensity * (1 - i / 3))
            glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha),
                             (int(glow_radius), int(glow_radius)),
                             int(glow_radius))
            screen.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))

        # 绘制金币主体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(current_radius))
        pygame.draw.circle(screen, self.border_color, (int(self.x), int(self.y)), int(current_radius), 3)

        # 绘制金币上的 "x2"
        text_rect = self.text.get_rect(center=(self.x, self.y))
        screen.blit(self.text, text_rect)



class PowerupManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.powerups = []
        
        # 道具生成参数
        self.pipes_since_last_spawn = 0
        self.pipes_until_next_spawn = random.randint(7, 10)  # 7-10个管道之间生成一次
        self.last_pipe_count = 0
    
    def reset(self):
        """重置道具管理器"""
        self.powerups = []
        self.pipes_since_last_spawn = 0
        self.pipes_until_next_spawn = random.randint(10, 15)
        self.last_pipe_count = 0
    
    def should_spawn_powerup(self, current_pipe_count):
        """检查是否应该生成道具"""
        # 检测新管道生成
        if current_pipe_count > self.last_pipe_count:
            self.pipes_since_last_spawn += 1
            self.last_pipe_count = current_pipe_count
            
            # 达到生成条件
            if self.pipes_since_last_spawn >= self.pipes_until_next_spawn:
                self.pipes_since_last_spawn = 0
                self.pipes_until_next_spawn = random.randint(10, 15)
                return True
        
        return False
    
    def spawn_powerup(self, pipe):
        """在管道缺口中生成随机道具"""
        # 在管道缺口的中心位置生成
        powerup_x = pipe.x + pipe.width // 2
        powerup_y = pipe.gap_y
        
        # 确保没有重复的活跃道具
        if any(p.active for p in self.powerups):
            return  # 如果已有活跃道具，不生成新的
        
        # 随机选择道具类型
        powerup_type = random.choice(["invincible", "double_score"])
        
        powerup = Powerup(powerup_x, powerup_y, powerup_type)
        self.powerups.append(powerup)
    
    def add_powerup(self, x, y, powerup_type):
        """在指定位置添加道具"""
        powerup = Powerup(x, y, powerup_type)
        self.powerups.append(powerup)
    
    def update(self, dt, scroll_speed):
        """更新所有道具"""
        for powerup in self.powerups[:]:
            # 道具跟随管道移动
            powerup.x -= scroll_speed
            powerup.update(dt)
            
            # 移除离开屏幕的道具
            if powerup.x < -50:
                self.powerups.remove(powerup)
    
    def draw(self, screen):
        """绘制所有道具"""
        for powerup in self.powerups:
            powerup.draw(screen)
    
    def get_active_powerups(self):
        """获取所有活跃的道具"""
        return [p for p in self.powerups if p.active]
