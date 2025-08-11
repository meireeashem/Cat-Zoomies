import pygame
from sys import exit
import random

pygame.init()

# Screen setup
GAME_WIDTH = 500
GAME_HEIGHT = 800
PIPE_START_X = GAME_WIDTH + 100
PIPE_SPACING_Y = 300

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption('Catto')
clock = pygame.time.Clock()

# Cat setup
cat_x = GAME_WIDTH / 12
cat_y_start = GAME_HEIGHT / 2
cat_width = 100
cat_height = 145

class Cat(pygame.Rect):
    def __init__(self, image):
        pygame.Rect.__init__(self, cat_x, cat_y_start, cat_width, cat_height)
        collision_margin = 5
        self.inflate_ip(-collision_margin*2, -collision_margin*2)  # shrink collision rect
        self.image = image

pipe_width = 80
pipe_height = 400
velocity_x = -3       

class Pipe:
    def __init__(self, x, y, image):
        self.image = image
        # rect for drawing the pipe
        self.rect = image.get_rect(topleft=(x, y))
        collision_margin = 10
        # smaller rect for collision detection
        self.collision_rect = pygame.Rect(
            self.rect.x + collision_margin,
            self.rect.y,
            self.rect.width - 2 * collision_margin,
            self.rect.height
        )
        self.passed = False

    def move(self, velocity_x):
        self.rect.x += velocity_x
        self.collision_rect.x += velocity_x

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# Load images and scales 
sky_surface = pygame.image.load('sky.png').convert()
cat_surface = pygame.image.load('cat.png').convert_alpha()
cat_surface = pygame.transform.scale(cat_surface, (cat_width, cat_height))
toppipe_surface = pygame.image.load('toppipe.png').convert_alpha()
toppipe_surface = pygame.transform.scale(toppipe_surface, (pipe_width, pipe_height))
bottompipe_surface = pygame.image.load('bottompipe.png').convert_alpha()
bottompipe_surface = pygame.transform.scale(bottompipe_surface, (pipe_width, pipe_height))

cat = Cat(cat_surface)
cat_pos_y = cat_y_start 

pipes = []
velocity_y = 0
gravity = 0.4
score = 0
game_over = False

PIPE_SPAWN_TIME = 1500 
create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, PIPE_SPAWN_TIME)

def create_pipes():
    random_pipe_y = random.randint(-pipe_height + 100, -100)

    toppipe = Pipe(PIPE_START_X, random_pipe_y, toppipe_surface)
    bottompipe = Pipe(PIPE_START_X, random_pipe_y + pipe_height + PIPE_SPACING_Y, bottompipe_surface)

    pipes.append(toppipe)
    pipes.append(bottompipe)


def reset_game():
    global velocity_y, score, game_over, cat_pos_y
    pipes.clear()
    score = 0
    velocity_y = 0
    game_over = False
    cat_pos_y = cat_y_start
    cat.y = int(cat_pos_y)
    create_pipes()
   

def draw():
    screen.blit(sky_surface, (0, 0))
    screen.blit(cat.image, (cat.x, cat.y))

    for pipe in pipes:
        pipe.draw(screen)

    # Draw score
    text_font = pygame.font.SysFont("Sans Ms", 40)
    text_string = str(int(score))
    text_render = text_font.render(text_string, True, "white")
    screen.blit(text_render, (10, 10))

    

    if game_over:
        over_font = pygame.font.SysFont("Sans Ms", 50)
        over_text = over_font.render("Uh Oh! Catto Died :(", True, "white")
        screen.blit(over_text, (GAME_WIDTH // 2 - over_text.get_width() // 2, GAME_HEIGHT // 2))

def move():
    global velocity_y, score, game_over, cat_pos_y
    velocity_y += gravity
    cat_pos_y += velocity_y
    cat.y = int(cat_pos_y)

    # Keep cat inside vertical bounds
    if cat.y < 0:
        cat_pos_y = 0
        cat.y = 0
        velocity_y = 0

    if cat.y > GAME_HEIGHT - cat.height:
        print("[GAMEOVER] Cat fell below screen")
        game_over = True
        return

    # Move pipes and check collisions
    for pipe in pipes:
        pipe.move(velocity_x)

        # Increase score when cat passes pipe (using pipe rect.x for fairness)
        if not pipe.passed and cat.x > pipe.rect.x + pipe.rect.width:
            score += 0.5  # 0.5 per pipe, top+bottom = 1 point
            pipe.passed = True

        # Use smaller collision rect for collision detection
        if cat.colliderect(pipe.collision_rect):
            game_over = True
            return

    # Remove offscreen pipes in pairs
    while len(pipes) >= 2 and pipes[0].rect.x < -pipe_width:
        pipes.pop(0)
        pipes.pop(0)

# Spawn pipes once at start so game is ready
create_pipes()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer and not game_over:
            print("[EVENT] Timer triggered - creating pipes")
            create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                if game_over:
                    reset_game()
                velocity_y = -6  # jump speed
                print("[INPUT] Jump!")

    if not game_over:
        move()

    draw()
    pygame.display.update()
    clock.tick(60)
