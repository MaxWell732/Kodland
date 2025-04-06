import pygame
import random
import sys
import time

# Inicialización del pygame
pygame.init()

#soundtrack de fondo
pygame.mixer.init()
try:
    pygame.mixer.music.load("sounds/music.ogg")  
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(-1)  
except:
    print("Error")

#creacion de la pantalla de juego
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Burbuja vs Formas")
clock = pygame.time.Clock()

# Colores que se van a usar
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BUTTON_COLOR = (70, 70, 70)
HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = WHITE

# esta funcion crea la forma de los corazones, la implementé para no importar imagenes
def create_heart_surface(size=30):
    heart = pygame.Surface((size, size), pygame.SRCALPHA)
    points = [
        (size // 2, 0),
        (size, size // 3),
        (size, size // 2),
        (size // 2, size),
        (0, size // 2),
        (0, size // 3)
    ]
    pygame.draw.polygon(heart, RED, points)
    return heart

HEART_ICON = create_heart_surface(30)  

#clase que contiene la información del botón

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont(None, 36)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()
#clase que contiene la información del jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (20, 20), 20)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 5
        self.hearts = 5  # 6 vidas iniciales
        self.invincible = False
        self.invincible_timer = 0
    #controles de movimientp
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
#clase que contiene la información del enemigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, shape):
        super().__init__()
        self.shape = shape
        if shape == "triangle":
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, RED, [(15, 0), (0, 30), (30, 30)])
        elif shape == "square":
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.rect(self.image, GREEN, (0, 0, 30, 30))
        else:  
            self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, WHITE, (0, 0, 40, 20))
        
        self.rect = self.image.get_rect(
            center=(random.randint(30, WIDTH-30), random.randint(30, HEIGHT-30)))
        self.speed = random.randint(2, 4)
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction = (-self.direction[0], self.direction[1])
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.direction = (self.direction[0], -self.direction[1])
#clase que contiene la información de los obstáculos
class Spike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(10, 0), (0, 20), (20, 20)])
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)))
#clase que contiene la información del ítem
class ItemX(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.line(self.image, GREEN, (0, 0), (20, 20), 3)
        pygame.draw.line(self.image, GREEN, (20, 0), (0, 20), 3)
        self.rect = self.image.get_rect(
            center=(random.randint(30, WIDTH-30), random.randint(30, HEIGHT-30)))
#pantalla de carga entre niveles
def show_level_transition(level):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    text = font.render(f"NIVEL {level}", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    
    font = pygame.font.SysFont(None, 36)
    text = font.render("Preparate...", True, GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()
    time.sleep(2)
#pantalla de victoria al acabar el nivel 3
def show_victory_screen():
    screen.fill(BLACK)
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    text1 = font_large.render("¡Fin del Juego!", True, GREEN)
    text2 = font_large.render("Felicidades!!", True, GREEN)
    text3 = font_small.render("Presiona R para reiniciar", True, WHITE)
    
    screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 100))
    screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 - 30))
    screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
#menú de pausa
def pause_menu():
    paused = True
    
    resume_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Reanudar")
    quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Salir del juego", 
                         lambda: [pygame.quit(), sys.exit()])
    
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
            
            resume_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                resume_button.handle_event(event)
                quit_button.handle_event(event)
                
                if resume_button.is_hovered:
                    paused = False
        
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        screen.blit(s, (0, 0))
        
        font = pygame.font.SysFont(None, 72)
        title = font.render("JUEGO PAUSADO", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        
        resume_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
#combinamos todo lo anterior...
def game():
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    items = pygame.sprite.Group()
    
    #generacion de enemigos nvl 1
    for _ in range(3):  
        enemy = Enemy("triangle")  
        enemy.speed = random.randint(1, 3)  
        enemies.add(enemy)
        all_sprites.add(enemy)

    level = 1
    x_collected = 0
    x_required = 4
    game_over = False
    
    # obstáculos
    for _ in range(10):
        spike = Spike()
        spikes.add(spike)
        all_sprites.add(spike)
    
    #item
    for _ in range(5):
        item = ItemX()
        items.add(item)
        all_sprites.add(item)
    
    # enemigos según nivel
    def spawn_enemies():
        nonlocal level
        if level == 1:
            enemy_count = 3  
            speed_range = (1, 3)  
        elif level == 2:
            enemy_count = 4  
            speed_range = (2, 4)  
        else:
            enemy_count = 5  
            speed_range = (2, 4)  

        for _ in range(enemy_count):
            if level == 1:
                enemy = Enemy("triangle")
            elif level == 2:
                enemy = Enemy(random.choice(["triangle", "square"]))
            else:
                enemy = Enemy(random.choice(["triangle", "square", "rectangle"]))
        
        # velocidad por nivel
            enemy.speed = random.randint(*speed_range)
            enemies.add(enemy)
            all_sprites.add(enemy)
    
    # Bucle principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_menu()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PAUSE_BUTTON.collidepoint(event.pos):
                    pause_menu()
        
        if not game_over:
            
            all_sprites.update()
            
            # Colisiones con enemigos
            if pygame.sprite.spritecollide(player, enemies, False):
                player.hearts -= 1
                if player.hearts <= 0:
                    game_over = True
                else:
                    player.rect.center = (WIDTH//2, HEIGHT//2)
            
            # Colisiones con obstaculos
            if pygame.sprite.spritecollide(player, spikes, False):
                player.hearts -= 1
                if player.hearts <= 0:
                    game_over = True
                else:
                    player.rect.center = (WIDTH//2, HEIGHT//2)
            
            # Recoleccion de items
            hits = pygame.sprite.spritecollide(player, items, True)
            for hit in hits:
                x_collected += 1
                item = ItemX()
                items.add(item)
                all_sprites.add(item)
                
                if x_collected >= x_required:
                    level += 1
                    x_collected = 0
                    if level == 2:
                        x_required = 6
                    elif level > 3:
                        show_victory_screen()
                        level = 1
                        x_required = 5
                        player.hearts = 5
                        enemies.empty()
                        items.empty()
                        spikes.empty()
                        for _ in range(3):
                            spawn_enemies()
                        for _ in range(5):
                            item = ItemX()
                            items.add(item)
                            all_sprites.add(item)
                        continue
                    show_level_transition(level)
                    enemies.empty()
                    spawn_enemies()

                
            
            
            screen.fill(BLACK)
            all_sprites.draw(screen)
            #ui
            font = pygame.font.SysFont(None, 36)
            level_text = font.render(f"Nivel: {level}", True, WHITE)
            x_text = font.render(f"X: {x_collected}/{x_required}", True, GREEN)
            
            screen.blit(level_text, (10, 10))
            screen.blit(x_text, (10, 90))
            
            # corazones en pantalla
            for i in range(player.hearts):
                screen.blit(HEART_ICON, (10 + i * 35, 50))
            
            #botón de pausa
            pygame.draw.rect(screen, BUTTON_COLOR, PAUSE_BUTTON, border_radius=5)
            pygame.draw.rect(screen, WHITE, PAUSE_BUTTON, 2, border_radius=5)
            font = pygame.font.SysFont(None, 25)
            pause_text = font.render("PAUSA", True, WHITE)
            screen.blit(pause_text, (PAUSE_BUTTON.x + 15, PAUSE_BUTTON.y + 8))
        else:
            # pierde
            font = pygame.font.SysFont(None, 72)
            text = font.render("Perdiste!! QUE NOOB XD", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            
            font = pygame.font.SysFont(None, 36)
            text = font.render("Presiona R para reiniciar", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 20))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                game()
        
        pygame.display.flip()
        clock.tick(60)

# Botón de SALIR
PAUSE_BUTTON = pygame.Rect(WIDTH - 100, 10, 80, 30)

if __name__ == "__main__":
    game()
    pygame.quit()