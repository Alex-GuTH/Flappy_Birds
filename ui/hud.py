"""
游戏内 HUD(抬头显示)
"""

import pygame

class GameHUD:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        
        # 颜色定义
        self.score_color = (255, 255, 255)
        self.time_color = (200, 200, 200)
        self.player1_color = (255, 100, 100)
        self.player2_color = (100, 100, 255)
        self.background_color = (30, 30, 30, 180)
        
        # 字体设置
        try:
            # 尝试使用系统字体
            self.score_font = pygame.font.SysFont("SimHei", 40)
            self.info_font = pygame.font.SysFont("SimHei", 30)
            self.small_font = pygame.font.SysFont("SimHei", 20)
        except:
            # 如果失败，则使用默认字体
            self.score_font=pygame.font.Font(None,40)
            self.info_font=pygame.font.Font(None,30)
            self.small_font = pygame.font.Font(None, 20)
        
        # HUD位置
        self.hud_height = 130
        self.padding = 50
        
    def draw(self, screen, player1_score, player2_score=None, 
             player1_alive=True, player2_alive=True, game_time=0):
        """绘制HUD"""
        # 绘制半透明背景
        hud_bg = pygame.Surface((self.screen_width, self.hud_height), pygame.SRCALPHA)
        hud_bg.fill(self.background_color)
        screen.blit(hud_bg, (0, 0))
        
        # 绘制顶部边框
        pygame.draw.line(screen, (100, 100, 100), 
                        (0, self.hud_height), 
                        (self.screen_width, self.hud_height), 
                        2)
        
        # 绘制玩家1信息
        self.draw_player_info(screen, 1, player1_score, player1_alive, self.player1_color, self.padding)
        
        # 绘制游戏时间
        self.draw_time_info(screen, game_time)
        
        # 绘制玩家2信息（如果存在）
        if player2_score is not None:
            self.draw_player_info(screen, 2, player2_score, player2_alive, self.player2_color, self.screen_width - 100 - self.padding)
        
        # 绘制操作提示
        self.draw_controls_hint(screen)
    
    def draw_player_info(self, screen, player_num, score, alive, color, x_pos):
        """绘制玩家信息"""
        # 玩家标签
        player_text = f"玩家{player_num}"
        player_surface = self.info_font.render(player_text, True, color)
        screen.blit(player_surface, (x_pos, 15))
        
        # 分数
        score_text = f"得分:{score}"
        score_surface = self.score_font.render(score_text, True, self.score_color)
        screen.blit(score_surface, (x_pos, 50))
        
        # 状态指示器
        status_text = "存活" if alive else "阵亡"
        status_color = (100, 255, 100) if alive else (255, 100, 100)
        status_surface = self.small_font.render(status_text, True, status_color)
        screen.blit(status_surface, (x_pos, 95)) # Adjusted y-pos
        
        # 状态图标
        icon_radius = 8
        icon_x = x_pos - 25
        icon_y = 30 # Adjusted y-pos
        
        if alive:
            pygame.draw.circle(screen, status_color, (icon_x, icon_y), icon_radius)
        else:
            pygame.draw.circle(screen, status_color, (icon_x, icon_y), icon_radius, 2)
            # 绘制叉号
            pygame.draw.line(screen, status_color, 
                            (icon_x - 5, icon_y - 5), 
                            (icon_x + 5, icon_y + 5), 2)
            pygame.draw.line(screen, status_color, 
                            (icon_x + 5, icon_y - 5), 
                            (icon_x - 5, icon_y + 5), 2)
    
    def draw_time_info(self, screen, game_time):
        """绘制时间信息"""
        # 计算分钟和秒
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = f"时间: {minutes:02d}:{seconds:02d}"
        
        time_surface = self.info_font.render(time_text, True, self.time_color)
        time_rect = time_surface.get_rect(center=(self.screen_width // 2, 25))
        screen.blit(time_surface, time_rect)
        
        # 绘制进度条
        progress_width = 200
        progress_height = 10
        progress_x = self.screen_width // 2 - progress_width // 2
        progress_y = 55
        
        # 背景条
        pygame.draw.rect(screen, (50, 50, 50), 
                        (progress_x, progress_y, progress_width, progress_height))
        
        # 进度条（随时间增加）
        progress = (game_time % 60) / 60  # 每分钟循环
        fill_width = int(progress_width * progress)
        
        # 颜色渐变（从绿到红）
        color_value = int(255 * (1 - progress))
        progress_color = (color_value, 255 - color_value, 50)
        
        pygame.draw.rect(screen, progress_color, 
                        (progress_x, progress_y, fill_width, progress_height))
        
        # 边框
        pygame.draw.rect(screen, (100, 100, 100), 
                        (progress_x, progress_y, progress_width, progress_height), 1)
        
        # 进度标记
        for i in range(0, 61, 15):  # 每15秒一个标记
            if i <= game_time % 60:
                mark_x = progress_x + int(progress_width * (i / 60))
                pygame.draw.line(screen, (200, 200, 200),
                                (mark_x, progress_y - 5),
                                (mark_x, progress_y + progress_height + 5), 1)
    
    def draw_controls_hint(self, screen):
        """绘制控制提示"""
        controls_text = "控制: 玩家1[空格] 玩家2[↑] 退出[ESC]"
        controls_surface = self.small_font.render(controls_text, True, (150, 150, 200))
        controls_rect = controls_surface.get_rect(center=(self.screen_width // 2, 115))
        screen.blit(controls_surface, controls_rect)
        
        # 绘制小鸟示意图
        self.draw_control_demo(screen)
    
    def draw_control_demo(self, screen):
        """绘制控制演示"""
        demo_x = self.screen_width // 2
        demo_y = 90
        
        # 绘制两个小鸟示意图
        bird1_x = demo_x - 80
        bird2_x = demo_x + 80
        bird_y = demo_y
        
        # 玩家1小鸟（红色）
        pygame.draw.circle(screen, self.player1_color, (bird1_x, bird_y), 10)
        
        # 玩家2小鸟（蓝色）
        pygame.draw.circle(screen, self.player2_color, (bird2_x, bird_y), 10)
        
        # 连接线
        pygame.draw.line(screen, (100, 100, 100), 
                        (bird1_x + 15, bird_y), 
                        (bird2_x - 15, bird_y), 1)
        
        # 提示文本
        vs_text = self.small_font.render("VS", True, (255, 255, 100))
        screen.blit(vs_text, (demo_x - 15, bird_y - 10))