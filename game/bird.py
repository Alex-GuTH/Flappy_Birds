"""
小鸟类：控制玩家角色
"""

import pygame
import math

class Bird:
    def __init__(self, x, y, color, control_key, player_name="玩家"):
        # 位置和速度
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.radius = 15
        
        # 外观
        self.color = color
        self.original_color = color
        self.eye_color = (255, 255, 255)
        self.pupil_color = (0, 0, 0)
        self.beak_color = (255, 165, 0)  # 橙色
        
        # 状态
        self.alive = True
        self.score = 0
        self.rotation = 0  # 用于旋转效果
        self.flap_power = 0
        
        # 控制
        self.control_key = control_key
        self.player_name = player_name
        self.passed_pipes = set() # 用于记录已通过的管道ID
        
        # 物理参数
        self.gravity = 9.8 * 80  # 像素/秒²
        self.flap_strength = -400  # 向上速度
        self.max_fall_speed = 600
        
        # 特效
        self.trail_points = []  # 轨迹点
        self.max_trail_length = 10
        self.flap_effect_timer = 0
        
        # 道具效果
        self.powerup_active = None
        self.powerup_timer = 0
        self.shield_active = False
        self.double_score_active = False
        self.invincible_timer = 0  # 无敌时间（护盾碰撞后）
    
    def reset(self):
        """重置小鸟状态"""
        self.y = 300
        self.velocity_y = 0
        self.alive = True
        self.score = 0
        self.rotation = 0
        self.trail_points = []
        self.shield_active = False
        self.double_score_active = False
        self.invincible_timer = 0
        self.color = self.original_color
        self.passed_pipes.clear()
    
    def flap(self):
        """扇动翅膀"""
        if self.alive:
            self.velocity_y = self.flap_strength
            self.flap_power = 15  # 翅膀扇动幅度
            
            # 添加轨迹点
            self.trail_points.append((self.x, self.y))
            if len(self.trail_points) > self.max_trail_length:
                self.trail_points.pop(0)
    
    def update(self, dt):
        """更新小鸟状态"""
        if not self.alive:
            return
        
        # 应用重力
        self.velocity_y += self.gravity * dt
        self.velocity_y = min(self.velocity_y, self.max_fall_speed)
        
        # 更新位置
        self.y += self.velocity_y * dt
        
        # 更新旋转（基于速度）
        # target_rotation = -self.velocity_y * 0.1
        # self.rotation += (target_rotation - self.rotation) * 0.1
        
        # 限制旋转角度
        # self.rotation = max(-30, min(30, self.rotation))
        
        # 更新翅膀扇动效果
        if self.flap_power > 0:
            self.flap_power -= 30 * dt
            self.flap_power = max(0, self.flap_power)
        
        # 更新轨迹点
        if self.trail_points:
            # 让轨迹点逐渐消失
            self.trail_points = [(px, py + 2) for px, py in self.trail_points]
            self.trail_points = [p for p in self.trail_points if p[1] < 600]
        
        # 更新道具效果计时器
        if self.powerup_timer > 0:
            self.powerup_timer -= dt
            if self.powerup_timer <= 0:
                self.deactivate_powerup()
        
        # 更新无敌时间
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
    
    def apply_powerup(self, powerup_type, duration):
        """应用道具效果"""
        self.powerup_active = powerup_type
        self.powerup_timer = duration
        
        if powerup_type == "invincible":
            self.shield_active = True
        elif powerup_type == "double_score":
            self.double_score_active = True
            # 拾取翻倍道具后，颜色保持不变
            self.color = self.original_color
    
    def activate_powerup(self, powerup_type):
        """激活道具效果"""
        self.powerup_active = powerup_type
        if powerup_type == "invincible":
            self.shield_active = True
        elif powerup_type == "double_score":
            self.double_score_active = True
            self.powerup_timer = 5  # 双倍得分持续5秒

    def deactivate_powerup(self):
        """停用道具效果"""
        if self.powerup_active == "double_score":
            self.double_score_active = False
        # 护盾的停用在碰撞时处理
        self.powerup_active = None

    def activate_shield(self):
        """激活护盾效果"""
        self.shield_active = True
    
    def on_shield_collision(self):
        """护盾碰撞后的处理：移除护盾并进入无敌状态"""
        self.shield_active = False
        self.invincible_timer = 1.0  # 1秒无敌时间
        self.color = self.original_color
    
    def draw(self, screen):
        """绘制小鸟"""
        if not self.alive:
            return
        
        # 绘制轨迹 
        for i, (px, py) in enumerate(self.trail_points):
            alpha = i / len(self.trail_points) * 100
            trail_radius = self.radius * (i / len(self.trail_points)) * 0.5
            trail_color = (*self.color, int(alpha))
            trail_surf = pygame.Surface((int(trail_radius * 2), int(trail_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, trail_color, (int(trail_radius), int(trail_radius)), int(trail_radius))
            screen.blit(trail_surf, (int(px - trail_radius), int(py - trail_radius)))
        
        # 创建一个更宽的表面以容纳鸟喙
        surface_width = self.radius * 2 + 30
        bird_surf = pygame.Surface((surface_width, self.radius * 2), pygame.SRCALPHA)
        
        # 在新表面上绘制身体，中心位于 (self.radius, self.radius)
        body_center_x = self.radius+10
        body_center_y = self.radius
        pygame.draw.circle(bird_surf, self.color, (body_center_x, body_center_y), self.radius)
        
        # 绘制眼睛和瞳孔 (坐标相对于身体中心)
        eye_x = body_center_x + self.radius // 4
        eye_y = body_center_y - self.radius // 3
        pygame.draw.circle(bird_surf, self.eye_color, (int(eye_x), int(eye_y)), self.radius // 3)
        pygame.draw.circle(bird_surf, self.pupil_color, (int(eye_x + self.radius // 6), int(eye_y)), self.radius // 6)
        
        # 重新计算并绘制鸟喙，确保在 surface_width (50px) 内
        base_x_offset = math.sqrt(self.radius**2 - 5**2)
        base_x = body_center_x + base_x_offset
        apex_x = base_x + 10  # 尖端x坐标
        apex_y = body_center_y
        beak_points = [
            (base_x, body_center_y - 5),
            (apex_x, apex_y),
            (base_x, body_center_y + 5)
        ]
        pygame.draw.polygon(bird_surf, self.beak_color, beak_points)
        
        # 绘制翅膀 (坐标相对于身体中心)
        wing_width = self.radius * 1.2
        wing_height = self.radius * 0.8
        wing_flap = math.sin(self.flap_power) * 5
        wing_rect = pygame.Rect(body_center_x - wing_width - 5, body_center_y - wing_height / 2, wing_width, wing_height)
        wing_rect.y += wing_flap # 应用扇动效果
        pygame.draw.ellipse(bird_surf, self.color, wing_rect)
        # 添加深色描边
        border_color = (max(0, self.color[0] - 100), max(0, self.color[1] - 100), max(0, self.color[2] - 100))
        pygame.draw.ellipse(bird_surf, border_color, wing_rect, 1)
        
        # 旋转并绘制小鸟
        rotated_surf = pygame.transform.rotate(bird_surf, self.rotation)
        rotated_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_surf, rotated_rect)

        # 绘制护盾效果
        if self.shield_active:
            self.draw_shield_effect(screen)
        
        # 绘制翻倍得分效果
        if self.double_score_active:
            self.draw_double_score_effect(screen)

    def draw_shield_effect(self, screen):
        """绘制护盾视觉效果"""
        shield_radius = self.radius + 5
        pygame.draw.circle(screen, (100, 100, 255, 100), 
                         (int(self.x), int(self.y)), 
                         shield_radius, 2)
        
        # 绘制护盾光晕
        for i in range(3):
            pulse_radius = shield_radius + i * 2 + (pygame.time.get_ticks() % 1000) / 1000 * 4
            alpha = 100 - i * 20
            shield_surf = pygame.Surface((int(pulse_radius * 2), int(pulse_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 100, 255, alpha), 
                             (int(pulse_radius), int(pulse_radius)), 
                             int(pulse_radius), 1)
            screen.blit(shield_surf, (int(self.x - pulse_radius), int(self.y - pulse_radius)))

    def draw_double_score_effect(self, screen):
        """绘制翻倍得分视觉效果 - 金色发散光线"""
        effect_radius = self.radius + 8
        num_lines = 12  # 光线数量
        angle_step = 360 / num_lines
        
        # 动态旋转光线
        rotation_angle = (pygame.time.get_ticks() / 20) % 360
        
        for i in range(num_lines):
            angle = math.radians(i * angle_step + rotation_angle)
            
            # 光线从中心向外发散
            start_x = self.x + math.cos(angle) * (self.radius + 2)
            start_y = self.y + math.sin(angle) * (self.radius + 2)
            end_x = self.x + math.cos(angle) * effect_radius
            end_y = self.y + math.sin(angle) * effect_radius
            
            # 动态长度和透明度
            pulse = (math.sin(pygame.time.get_ticks() / 200 + i) + 1) / 2
            alpha = int(150 * pulse)
            line_width = int(2 * pulse) + 1
            
            if line_width > 0:
                pygame.draw.line(screen, (255, 215, 0, alpha), 
                                 (start_x, start_y), (end_x, end_y), line_width)
