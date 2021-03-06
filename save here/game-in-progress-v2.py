import pygame

pygame.init()

# Window settings
WIDTH = 960
HEIGHT = 640
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("My Platform Game")
FPS = 60
clock = pygame.time.Clock()

# Colors
SKY_BLUE = (135, 206, 235)

# Fonts
font_small = pygame.font.Font(None, 32)
font_big = pygame.font.Font(None, 64)

# Images
hero_img = pygame.image.load("assets/p1_walk10.png")
hero_img = pygame.transform.scale(hero_img, (64, 64))

block_img = pygame.image.load("assets/snowMid.png")
block_img = pygame.transform.scale(block_img, (64, 64))

coin_img = pygame.image.load("assets/coin.png")
coin_img = pygame.transform.scale(coin_img, (64, 64))

background_img = pygame.image.load("assets/galaxy.png")

monster_img = pygame.image.load("assets/blockerMad.png")
monster_img = pygame.transform.scale(monster_img, (64, 64))


# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = pygame.Surface([64, 64], pygame.SRCALPHA, 32)
        self.image.blit(image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
class Block(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class Character(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.speed = 5
        self.jump_power = 20
        
        self.vx = 0
        self.vy = 0

    def apply_gravity(self):
        self.vy += 1

    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width
        
    def process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            print("Got a coin!")
    
    def move_left(self):
        self.vx = -1 * self.speed
        
    def move_right(self):
        self.vx = self.speed
        
    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power

        self.rect.y -= 1
        
    def update(self, level):
        self.apply_gravity()
        self.check_world_edges(level)
        self.process_blocks(level.blocks)
        self.process_coins(level.coins)



class Coin(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Enemy(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.vx = -2
        self.vy = 0

    def reverse(self):
        self.vx += 1

    def apply_gravity(self):
        self.vy += 1

    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def update(self, level):

        self.apply_gravity()
        self.check_world_edges(level)
        self.process_blocks(level.blocks)

class Level():
    def __init__(self, blocks, coins, enemies):
        self.blocks = blocks
        self.coins = coins
        self.enemies = enemies
        
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(blocks, coins, enemies)

        self.width = 1920
        self.height = 640
        
class Game():

    def __init__(self, hero, level):
        self.hero = hero
        self.level = level

        self.active_layer = pygame.Surface([1920, 640], pygame.SRCALPHA, 32)
        
    def reset(self):
        pass

    def calculate_offset(self):        
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH
            
        return x, 0
    
    def play(self):
        # game loop
        done = False

        while not done:
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == JUMP:
                        self.hero.jump(self.level.blocks)
                        
            pressed = pygame.key.get_pressed()
            
            # game logic
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()

            self.hero.update(self.level)
            self.level.enemies.update(self.level)
            
            #Drawing

            offset_x, offset_y = self.calculate_offset()
            
            self.active_layer.fill(SKY_BLUE)
            self.active_layer.blit(background_img, [0, 0])
            self.level.all_sprites.draw(self.active_layer)
            
            self.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])
            
            window.blit(self.active_layer, [offset_x, offset_y])
   
            # Update window
            pygame.display.update()
            clock.tick(FPS)

        # Close window on quit
        pygame.quit ()

def main():
    # Make sprites
    hero = Character(500, 512, hero_img)

    blocks = pygame.sprite.Group()
     
    for i in range(0, WIDTH * 2, 64):
        b = Block(i, 576, block_img)
        blocks.add(b)

    blocks.add(Block(192, 448, block_img))
    blocks.add(Block(256, 448, block_img))
    blocks.add(Block(320, 448, block_img))

    blocks.add(Block(448, 320, block_img))
    blocks.add(Block(512, 320, block_img))

    coins = pygame.sprite.Group()
    coins.add(Coin(768, 384, coin_img))
    coins.add(Coin(256, 320, coin_img))

    #make enemies
    enemies = pygame.sprite.Group()
    enemies.add(Enemy(640, 256, monster_img))
    # Make a level
    level = Level(blocks, coins, enemies)

    # Start game
    game = Game(hero, level)
    game.reset()
    game.play()

if __name__ == "__main__":
    main()
    
