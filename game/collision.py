"""
碰撞检测系统
"""

import pygame
import math

class CollisionSystem:
    def __init__(self):
        # 碰撞容差（像素）
        self.tolerance = 2
    
    def check_bird_pipes(self, bird, pipes):
        """检查小鸟与管道的碰撞"""
        if not bird.alive:
            return False
        
        # 检查是否在无敌时间内
        if bird.invincible_timer > 0:
            return False
        
        for pipe in pipes:
            top_rect, bottom_rect = pipe.get_rects()
            
            # 使用圆形与矩形的碰撞检测
            if self.circle_rect_collision(bird.x, bird.y, bird.radius, top_rect) or \
               self.circle_rect_collision(bird.x, bird.y, bird.radius, bottom_rect):
                
                # 如果有护盾，触发护盾碰撞效果
                if bird.shield_active:
                    bird.on_shield_collision()
                    return False  # 护盾保护，不算碰撞
                else:
                    return True  # 真正的碰撞
        
        return False
    
    def check_bird_bounds(self, bird, screen_height):
        """检查小鸟是否超出边界"""
        if not bird.alive:
            return False
        
        # 检查上下边界（留出一点缓冲）
        top_limit = 50
        bottom_limit = screen_height - 50
        
        hit_boundary = False
        
        if bird.y - bird.radius < top_limit:
            bird.y = top_limit + bird.radius
            hit_boundary = True
        
        if bird.y + bird.radius > bottom_limit:
            bird.y = bottom_limit - bird.radius
            hit_boundary = True
        
        # 如果碰到边界且在无敌时间内，不算碰撞
        if hit_boundary and bird.invincible_timer > 0:
            return False
        
        # 如果有护盾，触发护盾碰撞效果
        if hit_boundary and bird.shield_active:
            bird.on_shield_collision()
            return False
        
        return hit_boundary
    
    def circle_rect_collision(self, circle_x, circle_y, circle_radius, rect):
        """检测圆形与矩形的碰撞"""
        # 找到矩形上离圆心最近的点
        closest_x = max(rect.left, min(circle_x, rect.right))
        closest_y = max(rect.top, min(circle_y, rect.bottom))
        
        # 计算最近点到圆心的距离
        distance_x = circle_x - closest_x
        distance_y = circle_y - closest_y
        
        # 检查距离是否小于半径
        distance_squared = distance_x ** 2 + distance_y ** 2
        return distance_squared <= (circle_radius ** 2)
    
    def check_powerup_collision(self, bird, powerups):
        """检查小鸟与道具的碰撞"""
        if not bird.alive:
            return []

        collected = []
        
        for powerup in powerups:
            if not powerup.active:
                continue
            
            # 简单距离检测
            distance = math.sqrt((bird.x - powerup.x) ** 2 + (bird.y - powerup.y) ** 2)
            
            if distance < (bird.radius + powerup.radius):
                # 确保只有一个玩家可以拾取
                if powerup.active:
                    collected.append(powerup)
                    powerup.active = False  # 标记为非活跃，防止其他玩家拾取
        
        return collected