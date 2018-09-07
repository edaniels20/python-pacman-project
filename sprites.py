import pygame as pg
from settings import *
from enum import Enum
from pathing import Coordinate

pg.mixer.init()

font_name = pg.font.match_font('arial')

class Player(pg.sprite.Sprite): #This is the player class all of the functions for player are in here
    def __init__(self, game, x, y): #Core this assignes the image to player as well as creating the variables for the various functions for the player
        self.groups = game.all_sprites, game.player_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_image()
        self.game = game
        self.radius = 16
        self.moving = False
        self.current_frame = 0
        self.last_update = 0
        self.image = self.right_frames[0]
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.direction = 0
        self.rect = self.image.get_rect()
        self.vx = 0
        self.vy = 0
        self.has_moved = False
        
    def load_image(self): #Loads images as a list to replace the image of the base sprite
        self.right_frames = [pg.image.load('pacbase.png'),
                            pg.image.load('pacright1.png'), 
                            pg.image.load('pacright2.png'),
                            pg.image.load('pacright3.png'),]
        self.left_frames = [pg.image.load('pacbase.png'),
                            pg.image.load('pacleft1.png'),
                            pg.image.load('pacleft2.png'),
                            pg.image.load('pacleft1.png')]
        self.up_frames = [pg.image.load('pacbase.png'),
                        pg.image.load('pacup1.png'),
                        pg.image.load('pacup2.png'),
                        pg.image.load('pacup1.png')]
        self.down_frames = [pg.image.load('pacbase.png'),
                            pg.image.load('pacdown1.png'),
                            pg.image.load('pacdown2.png'),
                            pg.image.load('pacdown1.png')]


    def get_keys(self): #Takes key inputs and moves the player
        # self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -PLAYER_SPEED
            # self.vy = 0
            if self.vx < 0 and self.vy == 0:
                self.direction = Direction.left
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = PLAYER_SPEED
            # self.vy = 0
            if self.vx > 0 and self.vy == 0:
                self.direction = Direction.right
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -PLAYER_SPEED
            # self.vx = 0
            if self.vx == 0 and self.vy < 0:
                self.direction = Direction.up
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = PLAYER_SPEED
            # self.vx = 0
            if self.vx == 0 and self.vy >0:
                self.direction = Direction.down

        if self.vx < 0 or self.vx > 0 or self.vy < 0 or self.vy > 0:
            self.moving = True

    def collide_with_walls(self, dir): #Allows the player to slide on a wall if they colide with it
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self): #Updates the players inputs and sprites with the animation function
        self.animate()
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')
        self.is_moving()

    def is_moving(self):
        if self.moving and not self.has_moved:
            pg.mixer.music.load('pacman_chomp.wav')
            pg.mixer.music.play(-1)
            self.has_moved = True


    def animate(self): #Takes  the direction and assigns a list of sprites and also does the annimation updates for the sprites
        now = pg.time.get_ticks()
        if self.direction == Direction.right:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.right_frames)
                self.image = self.right_frames[self.current_frame]
        if self.direction == Direction.down:
            if now - self.last_update > 100:   
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.down_frames)
                self.image = self.down_frames[self.current_frame]
        if self.direction == Direction.left:
            if now - self.last_update > 100:   
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.left_frames)
                self.image = self.left_frames[self.current_frame]
        if self.direction == Direction.up:
            if now - self.last_update > 100:   
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.up_frames)
                self.image = self.up_frames[self.current_frame]

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.ghosts
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_mob_image()
        self.game = game
        self.current_mob_frame = 0
        self.last_mob_update = 0
        self.image = self.standing_frame[0]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.path = None

    def update(self):
        self.load_mob_image()
        self.animate_mob()
        if not self.path:
            self.path = self.game.pathing.getShortestPath(Coordinate(self.x, self.y), Coordinate(self.game.player.x, self.game.player.y))
            self.path_index = 0

        if not self.path:
            return

        node = self.path[self.path_index]

        vx = 0
        vy = 0

        if self.x < node.x:
            vx = 300
        elif self.x > node.x:
            vx = -300
        elif self.y < node.y:
            vy = 300
        else:
            vy = -300

        self.x += vx * self.game.dt
        self.y += vy * self.game.dt

        if self.x == node.x and self.y == node.y and self.path_index + 1 < len(self.path):
            self.path_index += 1
    def load_mob_image(self):
        self.standing_frame = [pg.image.load('ghost1.png'),
                                pg.image.load('ghost2.png'),
                                pg.image.load('ghost3.png'),
                                pg.image.load('ghost2.png'),
                                pg.image.load('ghost1.png')]
    def animate_mob(self): #Takes  the direction and assigns a list of sprites and also does the annimation updates for the sprites
        now = pg.time.get_ticks()
        if now - self.last_mob_update > 300:
                self.last_mob_update = now
                self.current_mob_frame = (self.current_mob_frame + 1) % len(self.standing_frame)
                self.image = self.standing_frame[self.current_mob_frame]



class Direction(Enum):
    down = 0
    left = 1
    up = 2
    right = 3

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, image):
        self.groups = game.all_sprites, game.walls
        super().__init__(self.groups)
        self.game = game
        self.image = pg.image.load(image)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Wallright(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallright.png')

class Walldown(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallup.png')

class Wallcornerright(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallcornerright.png')

class Wallcornerleft(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallcornerleft.png')

class Wallcornerbottomright(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallcornerbottomright.png')

class Wallcornerbottomleft(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallcornerbottomleft.png')

class Wallendleft(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallendleft.png')

class Wallendright(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallendright.png')

class Wallendtop(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallendtop.png')

class Wallendbottom(Wall):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'wallendbottom.png')

class Ball(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.ball
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.radius = 8
        self.image = pg.image.load('ball.png')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        self.check_collision()

    def check_collision(self):
        # hits = self.hits = pg.sprite.spritecollide(self, self.game.player, True)
        hits = pg.sprite.spritecollideany(self, self.game.player_group, pg.sprite.collide_circle)
        # counter = 1
        # for hit in hits:
        if hits:
            self.game.SCORE += 1
            self.kill()
            # counter -= 1
class DrawText():
    def Draw_Text(surf, text, size, x, y):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE) #True means anti-aliased (smooted edges)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)
