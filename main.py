import pygame
import random
import time
import asyncio
from game.bird import Bird
from game.pipe import PipeManager
from game.powerup import PowerupManager
from ui.hud import GameHUD
from ui.menu import MainMenu
from game.collision import CollisionSystem

# 使用当前时间作为随机数种子，确保每次运行的随机性
random.seed(time.time())

async def game_loop(screen, screen_width, screen_height, game_mode):
    """游戏主循环"""
    pygame.display.set_caption("Flappy Bird - 游戏中")

    # 创建小鸟实例
    birds = []
    if game_mode == "single_player":
        bird1 = Bird(screen_width // 2 - 150, screen_height // 2, (255, 0, 0), pygame.K_SPACE, "玩家1")
        birds.append(bird1)
    elif game_mode == "two_player":
        bird1 = Bird(screen_width // 2 - 150, screen_height // 2, (255, 0, 0), pygame.K_SPACE, "玩家1")
        bird2 = Bird(screen_width // 2 - 150, screen_height // 2, (0, 0, 255), pygame.K_UP, "玩家2")
        birds.extend([bird1, bird2])

    # 创建游戏组件
    pipe_manager = PipeManager(screen_width, screen_height)
    powerup_manager = PowerupManager(screen_width, screen_height)

    # 在第一个管道前生成无敌和翻倍道具
    powerup_x = screen_width - 5
    powerup_manager.add_powerup(powerup_x, screen_height // 2 - 100, 'invincible')
    powerup_manager.add_powerup(powerup_x, screen_height // 2 + 100, 'double_score')

    hud = GameHUD(screen_width)
    collision_system = CollisionSystem()

    # 游戏变量
    pipe_spawn_timer = 0
    pipe_spawn_interval = 2.0  # 管道生成间隔
    all_dead_start_time = None
    game_over_delay = 3.0

    clock = pygame.time.Clock()
    running = True
    start_time = time.time()

    while running:
        dt = clock.tick(60) / 1000.0
        game_time = time.time() - start_time

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # 返回主菜单
                for bird in birds:
                    if event.key == bird.control_key:
                        bird.flap()

        # 更新游戏状态
        all_players_dead = True
        for bird in birds:
            if bird.alive:
                all_players_dead = False
                bird.update(dt)
                # 碰撞检测
                if collision_system.check_bird_pipes(bird, pipe_manager.pipes) or \
                   collision_system.check_bird_bounds(bird, screen_height):
                    bird.alive = False
                
                # 计分
                score_increment = 2 if bird.double_score_active else 1
                # 找到所有未通过的管道
                upcoming_pipes = [p for p in pipe_manager.pipes if p.id not in bird.passed_pipes]
                for pipe in upcoming_pipes:
                    # 当小鸟中心超过管道中心时计分
                    if bird.x > pipe.x + pipe.width / 2:
                        bird.score += score_increment
                        bird.passed_pipes.add(pipe.id)
                        break # 每次只为一个管道计分

        if all_players_dead:
            if all_dead_start_time is None:
                all_dead_start_time = time.time()
            elif time.time() - all_dead_start_time >= game_over_delay:
                running = False
        else:
            all_dead_start_time = None

        # 更新管道
        pipe_spawn_timer += dt
        if pipe_spawn_timer > pipe_spawn_interval:
            current_gap_height = pipe_manager.get_current_gap_height()
            pipe_manager.add_pipe({"gap_height": current_gap_height})
            pipe_spawn_timer = 0
            
            # 检查是否需要生成道具
            if powerup_manager.should_spawn_powerup(pipe_manager.next_pipe_id):
                # 获取最新生成的管道
                if pipe_manager.pipes:
                    latest_pipe = pipe_manager.pipes[-1]
                    powerup_manager.spawn_powerup(latest_pipe)
        
        pipe_manager.update(dt)
        
        # 更新道具
        powerup_manager.update(dt, pipe_manager.scroll_speed)
        
        # 检查道具拾取
        active_powerups = powerup_manager.get_active_powerups()
        for powerup in active_powerups:
            for bird in birds:
                if bird.alive:
                    # 使用一个只包含当前道具的列表进行碰撞检测
                    collected_powerups = collision_system.check_powerup_collision(bird, [powerup])
                    if collected_powerups:
                        # 应用道具效果，持续5秒
                        bird.apply_powerup(powerup.powerup_type, 8.0)
                        # 因为道具已经被拾取，跳出内层循环
                        break

        # 绘制屏幕
        screen.fill((135, 206, 235))  # 天蓝色背景
        pipe_manager.draw(screen)
        powerup_manager.draw(screen)
        
        for bird in birds:
            if bird.alive:
                bird.draw(screen)

        # 绘制HUD
        player1_score = birds[0].score if len(birds) > 0 else 0
        player1_alive = birds[0].alive if len(birds) > 0 else False
        player2_score = birds[1].score if len(birds) > 1 else None
        player2_alive = birds[1].alive if len(birds) > 1 else False
        hud.draw(screen, player1_score, player2_score, player1_alive, player2_alive, game_time)

        pygame.display.flip()
        await asyncio.sleep(0)

    return True

async def main():
    pygame.init()
    random.seed(time.time())
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    main_menu = MainMenu(screen_width, screen_height)
    game_state = "menu"
    game_mode = "single_player" # Default game mode

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if game_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_action = main_menu.get_clicked_option(event.pos)
                    if clicked_action in ["single_player", "two_player"]:
                        game_state = "playing"
                        game_mode = clicked_action
                    elif clicked_action == "quit_game":
                        running = False
                        break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game_state = "playing"
                        game_mode = "single_player"
                    elif event.key == pygame.K_2:
                        game_state = "playing"
                        game_mode = "two_player"
                    elif event.key == pygame.K_q:
                        running = False
                        break

        if not running:
            break

        if game_state == "menu":
            pygame.display.set_caption("Flappy Bird - 主菜单")
            main_menu.update(dt)
            main_menu.draw(screen)
            pygame.display.flip()
            await asyncio.sleep(0)

        elif game_state == "playing":
            continue_running = await game_loop(screen, screen_width, screen_height, game_mode)
            if continue_running:
                game_state = "menu" # 游戏结束后返回菜单
            else:
                running = False

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())

