############################## DEPENDENCIES ##########################
# KIVY modules:
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ReferenceListProperty, \
                            ListProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget

# KV file:
Builder.load_file('screens/game/targetstart.kv')

# Generic:
import math
import random

# Project's:
from SampleManager import *
from standards import *
from approach import Approach
######################################################################

class TargetStart(Screen):

    inst_prob_left = NumericProperty(0)
    accum_prob_left = NumericProperty(0)
    accum_color_left = ListProperty([0,0,1,1])

    inst_prob_right = NumericProperty(0)
    accum_prob_right = NumericProperty(0)
    accum_color_right = ListProperty([0,0,1,1])

    label_on_toggle_button = StringProperty('Start')

    game = ObjectProperty(None)

    def __init__ (self, session_header,**kwargs):
        super (TargetStart, self).__init__(**kwargs)
        self.sh = session_header

        self.U = 0.0

        self.stream_flag = False
    # BUTTON CALLBACKS    
    # ----------------------
    def change_to_game(self,*args):

        self.manager.current = 'GameMenu'
        self.manager.transition.direction = 'right'

    def toogle_stream(self,*args):
        if self.stream_flag:
            self.stream_stop()
        else:
            self.stream_start()

    # ----------------------

    def stream_stop(self):
        self.sm.stop_flag = True
        self.stream_flag = False
        self.sm.join()
        self.label_on_toggle_button = 'Start'
        self.clock_unscheduler()
        self.set_bar_default()
        self.game.stop()

    def stream_start(self):
        self.load_approach()
        self.sm = SampleManager(self.sh.com_port, self.sh.baud_rate, self.sh.channels,
            self.sh.buf_len, daisy=self.sh.daisy, mode = self.sh.mode, path = self.sh.path_to_file,
            labels_path = self.sh.path_to_labels_file)
        self.sm.daemon = True  
        self.sm.stop_flag = False
        self.sm.start()
        self.label_on_toggle_button = 'Stop'
        self.stream_flag = True
        self.clock_scheduler()
        self.game.set_player_speed(self.sh.forward_speed)
        self.game.start(None)


    def clock_scheduler(self):
        Clock.schedule_interval(self.get_probs, self.sh.window_overlap)

    def clock_unscheduler(self):
        Clock.unschedule(self.get_probs)

    def get_probs(self, dt):

        t, buf = self.sm.GetBuffData()

        if buf.shape[0] == self.sh.buf_len:

            p = self.ap.applyModelOnEpoch(buf.T, 'prob')[0]

            u = p[0] - p[1]

            self.U += u
 
            U1 = 100 * (self.U + self.sh.game_threshold) / (2. * self.sh.game_threshold)

            U2 = 100 - U1

            U1, U2 = self.map_probs(U1, U2)

            self.update_accum_bars(U1, U2)

            self.update_inst_bars(u)

            # print 'U: ', self.U
            # print 'U1: ', U1
            # print 'U2: ', U2
            # print 'u: ', u

    def update_inst_bars(self, u):
        if u > 0:
            self.inst_prob_left = int(math.floor(u * 100))
            self.inst_prob_right = 0
        else:
            self.inst_prob_right = int(math.floor(abs(u) * 100))
            self.inst_prob_left = 0

    def update_accum_bars(self,U1, U2):

        U1_n = int(math.floor(U1))
        U2_n = int(math.floor(U2))

        if U1_n > self.sh.warning_threshold:
            self.accum_color_left = [1,1,0,1]
        elif U2_n > self.sh.warning_threshold:
            self.accum_color_right = [1,1,0,1]
        else:
            self.accum_color_left = [1,0,0,1]
            self.accum_color_right = [0,0,1,1]

        self.accum_prob_left = U1_n
        self.accum_prob_right = U2_n

    def map_probs(self, U1, U2):

        if U1 > 100:
            self.game.set_direction(-1)
            self.set_bar_default()
            return 0,0

        elif  U2 > 100:
            self.game.set_direction(1)
            self.set_bar_default()
            return 0,0

        else:
            return U1, U2
            # dont send any cmd

    def set_bar_default(self):

        self.accum_prob_left = 0
        self.accum_prob_right = 0

        self.inst_prob_left = 0
        self.inst_prob_right = 0

        self.U = 0.0

    def load_approach(self):

        self.ap = Approach()
        self.ap.loadFromPkl(PATH_TO_SESSION + self.sh.name)



from kivy.uix.image import Image
from kivy.core.window import Window


class Game(Widget):

    player = ObjectProperty(None)
    target = ObjectProperty(None)

    vel = NumericProperty(1)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self)
        if not self._keyboard:
            return

        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.direction = 'up'

        self.direction_list = ['left', 'up', 'right', 'down']
        self.direction_idx = 1

        self.on_flag = False

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        
        if ~self.on_flag:
            return
        if keycode[1] == 'left':
            self.set_direction(-1)
        elif keycode[1] == 'right':
            self.set_direction(1)
        else:
            return False

    def set_player_speed(self, speed):

        self.forward_speed = speed

    def set_positions(self):

        max_width = int(self.parent.width)
        max_height = int(self.parent.height)

        self.target.pos = (random.randint(0,max_width), \
                               random.randint(0,max_height))

        self.player.pos = self.center

    def start(self, dt):

        self.target.t_color = [1,1,0,1]

        self.set_positions()

        self.on_flag = True

        Clock.schedule_interval(self.check_if_won, 1./5.)
        Clock.schedule_interval(self.move_player, self.forward_speed)

    def stop(self):
        self.on_flag = False
        Clock.unschedule(self.check_if_won)
        Clock.unschedule(self.move_player)

    def check_if_won(self, dt):
        if self.player.collide_widget(self.target):
            self.target.t_color = [0,1,0,1]
            Clock.schedule_once(self.start, 2)
            self.stop()


    def set_direction(self, direction):

        # print 'changing by:', direction

        if (self.direction_idx == 0) and (direction == -1):
            self.direction_idx = 3
        elif (self.direction_idx == 3) and (direction == 1):
            self.direction_idx = 0
        else:
            self.direction_idx += direction
        
        self.direction = self.direction_list[self.direction_idx]

        Clock.unschedule(self.move_player)
        self.move_player(None)
        Clock.schedule_interval(self.move_player, self.forward_speed)

    def move_player(self, dt):
        l = self.player.width
        p0 = self.player.pos[0]
        p1 = self.player.pos[1]

        # print 'moving to:', self.direction

        if self.direction == 'right':
            if self.player.center_x < int(self.parent.width):
                x0 = p0
                y0 = p1 + l
                x1 = p0 + l
                y1 = p1 + l/2
                x2 = p0
                y2 = p1

                self.player.pos[0] += self.vel
            else:
                return False

        elif self.direction == 'left':
            if self.player.center_x > 0:
                x0 = p0 + l
                y0 = p1
                x1 = p0
                y1 = p1 + l/2
                x2 = p0 + l
                y2 = p1 + l

                self.player.pos[0] -= self.vel
            else:
                return False

        elif self.direction == 'up':
            if self.player.center_y < int(self.parent.height):

                x0 = p0
                y0 = p1
                x1 = p0 + l/2
                y1 = p1 + l
                x2 = p0 + l
                y2 = p1

                self.player.pos[1] += self.vel
            else:
                return False

        elif self.direction == 'down':
            if self.player.center_y > 0:

                x0 = p0 + l
                y0 = p1 + l
                x1 = p0 + l/2
                y1 = p1
                x2 = p0
                y2 = p1 + l

                self.player.pos[1] -= self.vel
            else:
                return False

        self.player.points = [x0, y0, x1, y1, x2, y2]


class GamePlayer(Widget):
    points = ListProperty([0] * 6)


class GameTarget(Widget):

    t_color = ListProperty([1,1,0,1])

        


    


        