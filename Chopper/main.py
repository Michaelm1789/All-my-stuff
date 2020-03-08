import pygame as pg
import sys
from os import path
vec = pg.math.Vector2

class Ground(pg.sprite.Sprite):
         
    def __init__(self, game):
        self.groups = game.ground, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.layer = 5
        self.game = game
        self.width = 100
        self.height = 50
        self.image = pg.Surface((self.width, self.height))
        self.image.fill((100, 100, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (app.width/2, app.height - 25) 
        self.pos = vec(self.rect.center)
        self.pos_change = vec(0, 0)
       
    def update(self, game, dt):
       
        pass
    def draw(self):
        
        self.screen.blit(self.image, self.rect.center)
        
class Player(pg.sprite.Sprite):
         
    def __init__(self, game):
        self.groups = game.player_group, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.layer = 5
        self.game = game
        self.image = self.game.chopper_anim[0]
        self.rect = self.image.get_rect()
        self.rect.x = app.width / 4
        self.rect.y = 200
        self.pos = vec(self.rect.center)
        self.pos_change = vec(0, 0)
        self.frame = 0
        self.rot = 0
        self.acc = vec(0,0)
    def update(self, game, dt):
        self.frame += 1
        if self.frame > 3:
            self.frame = 0
        self.pos = vec(self.rect.center)
        self.pos_change = self.pos_change + self.acc
        if self.pos_change.x > 3:
            self.pos_change.x = 3
        if self.pos_change.x < -3:
            self.pos_change.x = -3
        if self.pos_change.y > 3:
            self.pos_change.y = 3
        if self.pos_change.y < -3:
            self.pos_change.y = -3
        self.pos = self.pos + self.pos_change
           
       
        self.image = pg.transform.rotate(self.game.chopper_anim[self.frame].copy(), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
    def draw(self):
        
        self.screen.blit(self.image, self.rect.center)




    
class States(object):
    share = 'share'
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
    
class Menu(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'game'
    def cleanup(self):
        print('cleaning up Menu state stuff')
    def startup(self):
        print('starting Menu state stuff')
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                
                self.done = True
        
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        screen.fill((255,0,0))
    
class Game(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'menu'
        self.all_sprites = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.ground = pg.sprite.Group()
        self.load_data()
        self.new()
        
        
    def cleanup(self):
        print('cleaning up Game state stuff')
    def startup(self):
        print('starting Game state stuff')

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_dir = path.join(game_folder, 'img')
        self.snd_dir = path.join(game_folder, 'snd')
       
        self.chopper_anim = []
        
        for i in range(4):
            filename = 'chopper{}.png'.format(i)
            img = pg.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey((255, 255, 255))
            self.chopper_anim.append(img)

            
    def new(self):
        pg.init()
        self.my_joystick = pg.joystick.Joystick(0)
        self.my_joystick.init()
        self.player = Player(self)
        self.gnd = Ground(self)
        

        
    def get_event(self, event):
        #if event.type == pg.KEYDOWN:
        
        self.player.acc = vec(0, 0)
        horiz_axis_pos = self.my_joystick.get_axis(0)
        vert_axis_pos = self.my_joystick.get_axis(1)
 
        if horiz_axis_pos == -1:
            self.player.rot = 5
            self.player.acc += vec(-.25, 0)
        if horiz_axis_pos < 1 and horiz_axis_pos > -1:
            self.player.rot = 0
            self.player.acc.x = 0
        
        if horiz_axis_pos > .5:
            self.player.rot = -5
            self.player.acc += vec(.25, 0)

        if vert_axis_pos < 1 and vert_axis_pos > .9:
            self.player.acc.y = 0
        
        if vert_axis_pos > 0:
            self.player.acc += vec(0, .25)
        if vert_axis_pos < -.8:
            self.player.acc += vec(0, -.25)

          
        
        
        print (vert_axis_pos)        
       
    def update(self, screen, dt):
        self.all_sprites.update(self, dt)
        if self.player.rect.x > app.width / 2:
            self.player.rect.x = app.width / 2 
            for sprite in self.ground:
                sprite.rect.x -= 5
        if self.player.rect.x < app.width / 4:
            self.player.rect.x = app.width / 4  
            for sprite in self.ground:
                sprite.rect.x += 5
        
        
        self.draw(screen)
        
    def draw(self, screen):
        screen.fill((0,0,255))
        self.all_sprites.draw(screen)
    
class Control:
    def __init__(self):
        self.width = 900
        self.height = 500
        self.done = False
        self.screen = pg.display.set_mode((self.width, self.height))
        self.fps = 60
        self.clock = pg.time.Clock()
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
    def flip_state(self):
        self.state.done = False
        previous,self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous
    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, dt)
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_event(event)
    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            self.update(delta_time)
            pg.display.update()
    
    

    
app = Control()
state_dict = {
    'menu': Menu(),
    'game': Game()
}
app.setup_states(state_dict, 'menu')
app.main_game_loop()
pg.quit()
sys.exit()
