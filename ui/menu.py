import pygame

# 主菜单
class MainMenu:
    def __init__(self, screen_width, screen_height):
        # 窗口长宽
        self.screen_width = screen_width
        self.screen_height = screen_height
        # 颜色设置
        self.background_color=(30,30,60)
        self.title_color=(255,215,0)
        self.menu_color=(200,200,255)
        self.highlight_color=(255,100,100)
        # 字体设置
        self.title_font=None
        self.menu_font=None
        self.info_font=None
        self.tips_font=None
        self.load_fonts()
        # 菜单选项
        self.options=[{"text":"单人游戏","key":"1","action":"single_player","rect":None},
                      {"text":"双人竞技","key":"2","action":"two_player","rect":None},
                      #{"text":"积分榜单","key":"S","action":"scores","rect":None},
                      {"text":"退出游戏","key":"Q","action":"quit_game","rect":None}]
        # 小鸟动画
        self.bird_x=-50
        self.bird_y=screen_height//3
        self.bird_direction=1
        self.bird_speed=100
        self.animation_time=0

    def load_fonts(self):
        """加载字体"""
        try:
            # 尝试使用系统字体
            self.title_font = pygame.font.SysFont("SimHei", 72)
            self.menu_font = pygame.font.SysFont("SimHei", 48)
            self.info_font = pygame.font.SysFont("SimHei", 32)
            self.tips_font = pygame.font.SysFont("SimHei", 20)
        except:
            # 如果失败，则使用默认字体
            self.title_font=pygame.font.Font(None,72)
            self.menu_font=pygame.font.Font(None,48)
            self.info_font=pygame.font.Font(None,32)
            self.tips_font = pygame.font.Font(None, 20)

    def update(self,dt):
        """更新小鸟动画位置"""
        self.animation_time+=dt
        self.bird_x+=self.bird_direction*self.bird_speed*dt
        if self.bird_x>self.screen_width+50:
            self.bird_x=-50
        elif self.bird_x<-50:
            self.bird_x=self.screen_width+50
    
    def draw(self,screen):
        """绘制菜单"""
        # 绘制背景
        screen.fill(self.background_color)
        # 绘制星空背景
        self.draw_stars(screen)
        # 绘制标题
        title=self.title_font.render("Flappy Birds",True,self.title_color)
        title_rect=title.get_rect(center=(self.screen_width//2,80))
        screen.blit(title,title_rect)
        # 绘制副标题
        subtitle=self.info_font.render("经典像素鸟小游戏",True,(200,200,255))
        subtitle_rect=subtitle.get_rect(center=(self.screen_width//2,140))
        screen.blit(subtitle,subtitle_rect)
        # 绘制飞行的小鸟
        self.draw_animated_bird(screen)
        # 绘制菜单选项
        menu_y_start=self.screen_height//2 - 50
        option_spacing=70
        for i,option in enumerate(self.options):
            # 检查鼠标悬停
            mouse_pos=pygame.mouse.get_pos()
            option_y=menu_y_start+i*option_spacing
            # 渲染文本
            text_color=self.highlight_color if self.is_mouse_over_option(mouse_pos,option_y) else self.menu_color
            option_text=f"{option['text']} [{option['key']}]"
            option_surface=self.menu_font.render(option_text,True,text_color)
            option_rect=option_surface.get_rect(center=(self.screen_width//2,option_y))
            # 存储矩阵用于点击检测
            option['rect']=option_rect
            # 绘制选项
            screen.blit(option_surface,option_rect)
            # 绘制选中指示器
            if self.is_mouse_over_option(mouse_pos,option_y):
                indicator_left=self.menu_font.render(">",True,self.highlight_color)
                indicator_right=self.menu_font.render("<",True,self.highlight_color)
                screen.blit(indicator_left,(option_rect.left-40,option_y-24))
                screen.blit(indicator_right,(option_rect.right+10,option_y-24))
        # 绘制操作提示
        tips=["使用鼠标点击或键盘数字键选择","游戏中: 玩家1[空格] 玩家2[上箭头]","按ESC键返回菜单"]
        for i ,tip in enumerate(tips):
            tip_surface=self.tips_font.render(tip,True,(150,150,200))
            tip_rect=tip_surface.get_rect(center=(self.screen_width//2,self.screen_height-60+20*i))
            screen.blit(tip_surface,tip_rect)
    def draw_stars(self,screen):
        """绘制星空背景"""
        import random
        import math
        random.seed(42)
        for _ in range(100):
            x=random.randint(0,self.screen_width)
            y=random.randint(0,self.screen_height-200)
            size=random.randint(1,3)
            brightness=random.randint(150,255)

            # 闪烁效果
            pulse = (pygame.time.get_ticks() % 2000) / 2000.0
            # 使用sin函数创建一个从0到1再回到0的平滑循环
            brightness_multiplier = (math.sin(pulse * 2 * math.pi) + 1) / 2
            # 将亮度范围从0.5调整到1.0
            final_brightness = 0.5 + 0.5 * brightness_multiplier
            alpha = brightness * final_brightness
            star_surf=pygame.Surface((size*2,size*2),pygame.SRCALPHA)
            pygame.draw.circle(star_surf,(255,255,255,alpha),(size,size),size)
            screen.blit(star_surf,(x-size,y-size))

    def draw_animated_bird(self,screen):
        """绘制飞行中的小鸟"""
        # 绘制鸟身
        bird_radius=20
        bird_color=(255,100,100)
        # 翅膀扇动动画
        wing_offset=10*abs(pygame.math.Vector2(1,0).rotate(self.animation_time*360).y)
        # 绘制小鸟
        pygame.draw.circle(screen,bird_color,(int(self.bird_x),int(self.bird_y)),bird_radius)
        # 绘制翅膀
        wing_points=[(self.bird_x-15,self.bird_y),
                     (self.bird_x-30,self.bird_y+wing_offset),
                     (self.bird_x-15,self.bird_y+5)]
        pygame.draw.polygon(screen,bird_color,wing_points)
        # 绘制眼睛
        pygame.draw.circle(screen, (255, 255, 255), (int(self.bird_x + 10), int(self.bird_y - 5)), 6)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.bird_x + 12), int(self.bird_y - 5)), 3)
         # 绘制鸟喙
        beak_points = [(self.bird_x + 30, self.bird_y),
                       (self.bird_x + 20, self.bird_y - 3),
                       (self.bird_x + 20, self.bird_y + 3)]
        pygame.draw.polygon(screen, (255, 200, 50), beak_points)
        # 绘制轨迹
        for i in range(5):
            trail_x = self.bird_x - 20 - i * 8
            trail_y = self.bird_y
            trail_radius = bird_radius * (1 - i * 0.2) * 0.5
            trail_alpha = 100 - i * 20
            trail_surf = pygame.Surface((int(trail_radius * 2), int(trail_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf,(*bird_color[:3],trail_alpha),(int(trail_radius),int(trail_radius)),int(trail_radius))
            screen.blit(trail_surf, (int(trail_x - trail_radius), int(trail_y - trail_radius)))

    def is_mouse_over_option(self,mouse_pos,option_y):
        """检查鼠标是否悬停在选项上"""
        option_width = 200
        option_height = 40
        option_rect = pygame.Rect(self.screen_width // 2 - option_width // 2,option_y - option_height // 2,option_width,option_height)
        return option_rect.collidepoint(mouse_pos)
    
    def get_clicked_option(self, mouse_pos):
        """获取被点击的选项"""
        for option in self.options:
            if option['rect'] and option['rect'].collidepoint(mouse_pos):
                return option['action']
        return None