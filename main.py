import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from pathing import Pathfinding, Coordinate

pg.mixer.init()
pg.mixer.music.load('pacman_beginning.wav')
pg.mixer.music.play(0)

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)

        self.SCORE = 0

        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map = Map(path.join(game_folder, 'map.txt'))

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.ball = pg.sprite.Group()
        self.ghosts = pg.sprite.Group()
        self.draw_score = DrawText

        map_items = {
            '1': Wallright,
            '2': Walldown,
            '3': Wallcornerright,
            '4': Wallcornerleft,
            '5': Wallcornerbottomright,
            '6': Wallcornerbottomleft,
            '7': Wallendleft,
            '8': Wallendright,
            '9': Wallendtop,
            'a': Wallendbottom,
            '.': Ball,
            'M': Mob
        }

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                item = map_items.get(tile)
                if item:
                    item(self, col, row)

                if tile == 'P':
                    self.player = Player(self, col, row)

        self.camera = Camera(self.map.width, self.map.height)

        self.pathing = Pathfinding([Coordinate(i.rect.x, i.rect.y) for i in self.walls.sprites()])

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    # def draw_grid(self):
    #     for x in range(0, WIDTH, TILESIZE):
    #         pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
    #     for y in range(0, HEIGHT, TILESIZE):
    #         pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        # self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.draw_score.Draw_Text(self.screen, str(self.SCORE), 18, WIDTH /2, 10)
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# Makes the game
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
