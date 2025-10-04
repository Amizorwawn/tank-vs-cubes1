import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 650, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank versus cubes")
FPS = 60
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
LIGHT_GRAY = (170, 170, 170)
HOVER = (220, 220, 220)

PLAYER_SIZE = 50
PLAYER_SPEED = 7
ENEMY_SIZE = 50
ENEMY_SPEED = 2
BULLET_SIZE = 8
BULLET_SPEED = -10
SHOT_DELAY = 300


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, keys):
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

    def draw(self):
        pygame.draw.rect(WIN, GREEN, self.rect)


class Enemy:
    def __init__(self, health=1):
        self.rect = pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), -ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE)
        self.health = health
        self.max_health = health
        self.speed = ENEMY_SPEED

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(WIN, RED, self.rect)
        if self.max_health > 1:
            hp_bar_width = self.rect.width
            hp_ratio = self.health / self.max_health
            hp_fill = int(hp_bar_width * hp_ratio)
            hp_y = self.rect.top - 10
            pygame.draw.rect(WIN, RED, (self.rect.x, hp_y, hp_bar_width, 5))
            pygame.draw.rect(WIN, GREEN, (self.rect.x, hp_y, hp_fill, 5))
            font = pygame.font.SysFont(None, 18)
            hp_text = font.render(f"{self.health}/{self.max_health}", True, WHITE)
            WIN.blit(hp_text, (self.rect.centerx - hp_text.get_width() // 2, hp_y - 15))


class Bullet:
    def __init__(self, x, y, speed, color=WHITE, size=BULLET_SIZE, damage=1, direction=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.color = color
        self.damage = damage
        self.direction = direction if direction else (0, -1)

    def move(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)


class Boss:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 100, -200, 200, 200)
        self.health = 80
        self.max_health = 80
        self.speed = 1
        self.active = False
        self.spawn_timer = 0
        self.shoot_timer = 0

    def move(self):
        if self.rect.top < 100:
            self.rect.y += self.speed

    def shoot(self, target_pos):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        direction = (dx / dist, dy / dist)
        return Bullet(
            self.rect.centerx - 12,
            self.rect.bottom,
            speed=5,
            color=(255, 100, 0),
            size=20,
            damage=2,
            direction=direction
        )

    def draw(self):
        pygame.draw.rect(WIN, (150, 0, 0), self.rect)
        hp_bar_width = WIDTH - 200
        hp_fill = int(hp_bar_width * (self.health / self.max_health))
        pygame.draw.rect(WIN, RED, (100, HEIGHT - 40, hp_bar_width, 20))
        pygame.draw.rect(WIN, GREEN, (100, HEIGHT - 40, hp_fill, 20))
        font = pygame.font.SysFont(None, 28)
        hp_text = font.render(f"Босс HP: {int(self.health)}/{self.max_health}", True, WHITE)
        WIN.blit(hp_text, (WIDTH // 2 - hp_text.get_width() // 2, HEIGHT - 70))


class Minion:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 1
        self.damage = 1
        self.health = 3
        self.shoot_timer = random.randint(0, FPS * 2)

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(WIN, BLUE, self.rect)
        hp_ratio = self.health / 3
        hp_bar_width = self.rect.width
        hp_fill = int(hp_bar_width * hp_ratio)
        hp_y = self.rect.top - 5
        pygame.draw.rect(WIN, RED, (self.rect.x, hp_y, hp_bar_width, 3))
        pygame.draw.rect(WIN, GREEN, (self.rect.x, hp_y, hp_fill, 3))


def end_screen(text, score):
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.SysFont(None, 40)
    end_text = font_big.render(text, True, WHITE)
    score_text = font_small.render(f"Рахунок: {score}", True, WHITE)
    restart_text = font_small.render("Натисни R щоб почати знову та ESC щоб вийти", True, WHITE)

    while True:
        WIN.fill(BLACK)
        WIN.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 100))
        WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    menu()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def game(mode="infinite", target_score=20):
    player = Player()
    enemies = []
    bullets = []
    enemy_bullets = []
    minions = []
    score = 0
    lives = 5
    last_shot = 0
    boss = Boss()
    boss_spawned = False
    enemy_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_timer, 1000)

    if mode == "extreme":
        enemy_health = 3
        bullet_speed = -15
        shot_delay = 100
    else:
        enemy_health = 1
        bullet_speed = BULLET_SPEED
        shot_delay = SHOT_DELAY

    running = True
    while running:
        clock.tick(FPS)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == enemy_timer and not boss.active:
                enemies.append(Enemy(health=enemy_health))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    now = pygame.time.get_ticks()
                    if now - last_shot >= shot_delay:
                        bullets.append(Bullet(player.rect.centerx - BULLET_SIZE // 2, player.rect.top, abs(bullet_speed)))
                        last_shot = now

        keys = pygame.key.get_pressed()
        player.move(keys)

        if mode != "infinite" and not boss_spawned and score == target_score - 1:
            boss.active = True
            boss_spawned = True
            enemies.clear()

        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.colliderect(player.rect):
                enemies.remove(enemy)
                lives -= 1
            elif enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                lives -= 1

        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        if not boss.active:
            for enemy in enemies[:]:
                for bullet in bullets[:]:
                    if enemy.rect.colliderect(bullet.rect):
                        bullets.remove(bullet)
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            score += 1
                        break
        else:
            boss.move()
            boss.spawn_timer += 1
            boss.shoot_timer += 1
            if boss.spawn_timer >= FPS * 5:
                minions.append(Minion(random.randint(50, WIDTH - 50), boss.rect.bottom))
                boss.spawn_timer = 0
            if boss.shoot_timer >= FPS * 2:
                enemy_bullets.append(boss.shoot(player.rect.center))
                boss.shoot_timer = 0

        for bullet in bullets[:]:
            if boss.active and boss.rect.colliderect(bullet.rect):
                bullets.remove(bullet)
                boss.health -= 1
                if boss.health <= 0:
                    boss.active = False
                    score += 1
                    if mode != "infinite" and score >= target_score:
                        end_screen("Ти переміг", score)
                break

        for minion in minions[:]:
            minion.move()
            minion.shoot_timer += 1
            if minion.shoot_timer >= FPS * 3:
                dx = player.rect.centerx - minion.rect.centerx
                dy = player.rect.centery - minion.rect.centery
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                direction = (dx / dist, dy / dist)
                enemy_bullets.append(Bullet(minion.rect.centerx, minion.rect.bottom, 5, (255, 255, 0), 6, 1, direction))
                minion.shoot_timer = 0

            for bullet in bullets[:]:
                if minion.rect.colliderect(bullet.rect):
                    bullets.remove(bullet)
                    minion.health -= 1
                    if minion.health <= 0:
                        minions.remove(minion)
                        score += 1
                    break

            if minion.rect.colliderect(player.rect) or minion.rect.bottom >= HEIGHT:
                lives -= 1
                minions.remove(minion)

        for eb in enemy_bullets[:]:
            eb.move()
            if eb.rect.colliderect(player.rect):
                enemy_bullets.remove(eb)
                lives -= eb.damage
            elif eb.rect.top > HEIGHT or eb.rect.bottom < 0 or eb.rect.left < 0 or eb.rect.right > WIDTH:
                enemy_bullets.remove(eb)

        if lives <= 0:
            end_screen("Ти програв", score)

        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for eb in enemy_bullets:
            eb.draw()
        for minion in minions:
            minion.draw()
        if boss.active:
            boss.draw()

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Рахунок: {score}", True, WHITE)
        lives_text = font.render(f"Життя: {lives}", True, WHITE)
        WIN.blit(score_text, (10, 10))
        WIN.blit(lives_text, (WIDTH - 120, 10))
        if mode == "score" or mode == "extreme":
            target_text = font.render(f"Мета: {target_score}", True, WHITE)
            WIN.blit(target_text, (WIDTH // 2 - target_text.get_width() // 2, 10))

        pygame.display.flip()


def menu():
    font_big = pygame.font.SysFont(None, 70)
    font_small = pygame.font.SysFont(None, 40)
    slider_value = 20
    dragging = False

    while True:
        WIN.fill(BLACK)
        title = font_big.render("ТАНК ПРОТИ КУБИКІВ", True, WHITE)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        btn_width, btn_height = 300, 80
        infinite_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 200, btn_width, btn_height)
        score_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 310, btn_width, btn_height)
        extreme_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 420, btn_width, btn_height)

        mouse_pos = pygame.mouse.get_pos()
        infinite_color = HOVER if infinite_btn.collidepoint(mouse_pos) else LIGHT_GRAY
        score_color = HOVER if score_btn.collidepoint(mouse_pos) else LIGHT_GRAY
        extreme_color = HOVER if extreme_btn.collidepoint(mouse_pos) else LIGHT_GRAY

        pygame.draw.rect(WIN, infinite_color, infinite_btn, border_radius=12)
        pygame.draw.rect(WIN, score_color, score_btn, border_radius=12)
        pygame.draw.rect(WIN, extreme_color, extreme_btn, border_radius=12)

        infinite_text = font_small.render("Нескінченний режим", True, BLACK)
        score_text = font_small.render("Режим з рахунком", True, BLACK)
        extreme_text = font_small.render("Екстремальний режим", True, BLACK)

        WIN.blit(infinite_text, (infinite_btn.centerx - infinite_text.get_width() // 2,
                                 infinite_btn.centery - infinite_text.get_height() // 2))
        WIN.blit(score_text, (score_btn.centerx - score_text.get_width() // 2,
                              score_btn.centery - score_text.get_height() // 2))
        WIN.blit(extreme_text, (extreme_btn.centerx - extreme_text.get_width() // 2,
                                extreme_btn.centery - extreme_text.get_height() // 2))

        slider_text = font_small.render(f"Макс. рахунок (10–75): {slider_value}", True, WHITE)
        slider_text_y = 530
        WIN.blit(slider_text, (WIDTH // 2 - slider_text.get_width() // 2, slider_text_y))

        slider_line_width = 300
        slider_line_x = WIDTH // 2 - slider_line_width // 2
        slider_line_y = 580
        pygame.draw.rect(WIN, WHITE, (slider_line_x, slider_line_y, slider_line_width, 5))

        knob_x = slider_line_x + int((slider_value - 10) / 65 * slider_line_width)
        knob = pygame.Rect(knob_x - 10, slider_line_y - 5, 20, 20)
        knob_color = BLUE if dragging else LIGHT_GRAY
        pygame.draw.rect(WIN, knob_color, knob, border_radius=5)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if infinite_btn.collidepoint(event.pos):
                    game("infinite")
                if score_btn.collidepoint(event.pos):
                    game("score", target_score=slider_value)
                if extreme_btn.collidepoint(event.pos):
                    game("extreme", target_score=slider_value)
                if knob.collidepoint(event.pos):
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                mouse_x = max(slider_line_x, min(slider_line_x + slider_line_width, event.pos[0]))
                slider_value = 10 + int((mouse_x - slider_line_x) / slider_line_width * 65)


menu()