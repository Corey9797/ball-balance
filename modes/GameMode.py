import time

import math

import pygame

import tools

import rod

import config as c



# --------------------------------------------------------------------
# Custom Events and Timers
# --------------------------------------------------------------------

GENERIC_TIMER       = pygame.USEREVENT + 1
BONUS_REDUCE_TIMER  = pygame.USEREVENT + 2
INCREMENT_ROD_TIMER = pygame.USEREVENT + 3



class GameMode(tools.ModeBase):

    def __init__(self, assets):
        super(GameMode, self).__init__(assets)

        self.reset_settings()

        self.start_time = time.time()



    def reset_settings(self):
        self.score = 0
        self.current_bonus = 0

        self.balls_left = 3
        self.star_lit = False

        self.extra_ball_earned = False

        self.current_hole = 1

        self.state = 'starting round'
        self.state_just_changed = True

        self.succeeded_hole = False

        self.skip_music = False

        self.start_time = time.time()



    def process(self, events, pressed_keys):

        if self.state == 'starting round' and self.state_just_changed:
            self.state_just_changed = False

            print('Starting round')

            if not self.balls_left:
                self.state = 'game over'
                self.state_just_changed = True

            if self.current_hole > 10:
                self.state = 'win'
                self.state_just_changed = True

            self.current_bonus = self.current_hole * 100

            if not self.skip_music:
                tools.play_song(self.settings['Audio']['Theme'])

            self.rod.allowed_to_move = False


        elif self.state == 'starting round':
            self.rod.move(-1, -1)


        elif self.state == 'ball on rod' and self.state_just_changed:
            self.state_just_changed = False

            print('Ball loaded onto rod')

            pygame.time.delay(500)
            pygame.time.set_timer(GENERIC_TIMER, 1000)


        elif self.state == 'ball on rod':
            self.rod.move(1, 1)


        elif self.state == 'ball at origin' and self.state_just_changed:
            self.state_just_changed = False

            print('Ball at origin point')

            self.rod.allowed_to_move = True

            pygame.time.set_timer(BONUS_REDUCE_TIMER, 4000)
            pygame.time.set_timer(INCREMENT_ROD_TIMER, 4000)

            self.state = 'game in progress'
            self.state_just_changed = True


        elif self.state == 'game in progress' and self.state_just_changed:
            self.state_just_changed = False

            print('Game is in progress')


        elif self.state == 'end level' and self.state_just_changed:
            self.state_just_changed = False

            print('Level has ended')

            self.rod.allowed_to_move = False

            pygame.mixer.music.stop()

            pygame.time.set_timer(BONUS_REDUCE_TIMER, 0)
            pygame.time.set_timer(INCREMENT_ROD_TIMER, 0)

            if self.succeeded_hole:
                self.state = 'hole success'
            else:
                self.state = 'hole failure'


        elif self.state == 'hole success':

            print('Player was successful')

            tools.play_song(self.settings['Audio']['Success'])

            pygame.time.delay(2000)

            self.current_hole += 1

            self.state = 'count down bonus'


        elif self.state == 'count down bonus' and self.state_just_changed:
            self.state_just_changed = False
            self.extra_is_fresh = True


        elif self.state == 'count down bonus':
            if self.current_bonus > 0:
                self.current_bonus -= 10
                self.score        += 10
                tools.play_sound(self.settings['Audio']['Bonus'])
                pygame.time.delay(150)
            else:
                pygame.time.delay(500)

                self.state = 'starting round'
                self.state_just_changed = True

            if self.score >= 4000 and not self.extra_ball_earned:
                self.extra_ball_earned = True

                print('Extra ball earned')

                tools.play_song(self.settings['Audio']['ExtraBall'])

                self.balls_left += 1
                self.skip_music = True


        elif self.state == 'hole failure':

            print('Player failed')

            tools.play_song(self.settings['Audio']['Failure'])

            pygame.time.delay(2500)

            self.balls_left -= 1

            self.state = 'starting round'
            self.state_just_changed = True


        elif self.state == 'game over' and self.state_just_changed:
            self.state_just_changed = False

            print('Game over')

            self.rod.allowed_to_move = False

            pygame.time.set_timer(BONUS_REDUCE_TIMER, 0)
            pygame.time.set_timer(INCREMENT_ROD_TIMER, 0)

            pygame.mixer.music.stop()
            tools.play_song(self.settings['Audio']['GameOver'])

            pygame.time.delay(10500)

            self.reset_settings()

            self.switch_to_mode(c.ATTRACT_MODE)


        elif self.state == 'win' and self.state_just_changed:
            self.state_just_changed = False

            print('Player won')

            self.rod.allowed_to_move = False

            pygame.time.set_timer(BONUS_REDUCE_TIMER, 0)
            pygame.time.set_timer(INCREMENT_ROD_TIMER, 0)

            pygame.mixer.music.stop()
            tools.play_song(self.settings['Audio']['Win'])

            self.star_lit = True

            pygame.time.delay(9500)

            self.reset_settings()

            self.switch_to_mode(c.ATTRACT_MODE)


        # ------------------------------------------------------------


        for event in events:

            # If a button is pressed down...
            if event.type == pygame.KEYDOWN:
                if event.key == self.settings['Controls']['HoleSwitch'+str(self.current_hole)]:
                    self.state = 'hole success'
                    self.state_just_changed = True
                elif event.key == self.settings['Controls']['HoleSwitchFailure']:
                    if self.state == 'game in progress':
                        self.state = 'end level'
                        self.state_just_changed = True


            # If button is being released...
            elif event.type == pygame.KEYUP:
                if event.key == self.settings['Controls']['HoleSwitchFailure']:
                    if self.state == 'starting round':
                        self.state = 'ball on rod'
                        self.state_just_changed = True


            elif event.type == BONUS_REDUCE_TIMER:
                if self.state == 'game in progress':
                    pygame.time.set_timer(BONUS_REDUCE_TIMER, 4000)
                    tools.play_sound(self.settings['Audio']['Tick'])

                    if self.current_bonus > 0:
                        self.current_bonus -= 10


            elif event.type == INCREMENT_ROD_TIMER:
                if self.state == 'game in progress':
                    pygame.time.set_timer(INCREMENT_ROD_TIMER, 4000)
                    self.rod.move(1, 1)


            elif event.type == GENERIC_TIMER and self.state == 'ball on rod':
                pygame.time.set_timer(GENERIC_TIMER, 0)
                self.state = 'ball at origin'
                self.state_just_changed = True


        # ------------------------------------------------------------


        self.rod.activate_joysticks(pressed_keys)



    def render(self, screen):

        # Fill the screen with black
        screen.fill((0, 0, 0))


        pixels = []

        show_hole_led = False

        valid_states = ['starting round', 'ball on rod', 'ball at origin', 'game in progress']

        self.is_valid_state = False
        for valid_state in valid_states:
            if self.state == valid_state:
                self.is_valid_state = True


        if self.is_valid_state:
            t = (time.time() - self.start_time) * 22

            for ii in range(self.leds.number_of_leds - 1):

                if ii == self.settings['LEDs']['Hole' + str(self.current_hole)]:
                    c = math.sin(t) * 127 + 128
                else:
                    c = 64

                pixels.append((c, c, c))
                self.leds.generate_led_graphic(screen, ii, (c, c, c))

        else:
            for ii in range(self.leds.number_of_leds):
                pixels.append((0, 64, 0))
                self.leds.generate_led_graphic(screen, ii, (64, 64, 64))

        # Send the new pixels to the actual LEDs
        self.leds.put_pixels(pixels)


        font = pygame.font.Font(None, 36)

        # Score UI
        rendered_score = font.render('Score: ' + str(self.score), 1, (255, 127, 127))
        screen.blit(rendered_score, (150, 20))

        # Bonus UI
        rendered_bonus = font.render('Bonus: ' + str(self.current_bonus), 1, (0, 255, 0))
        screen.blit(rendered_bonus, (150, 60))

        # Balls left UI
        rendered_lives = font.render('Balls left: ' + str(self.balls_left), 1, (0, 255, 255))
        screen.blit(rendered_lives, (150, 100))

        # Generate the carriage and rod graphics
        self.rod.generate_graphics(screen)

        #Checks if Debugging is on
        if tools.DEBUG_TOGGLE:

            #increments debug timer and adds blank to print buffer
            #this would eventually clear the buffer if no other print commands are sent
            tools.DEBUG_TIMER+=1
            if tools.DEBUG_TIMER > tools.DEBUG_TIMER_MAX:
                tools.DEBUG_TIMER = 0
                tools.Debug_Print("")
            debug_y=350
            # Prints Debug Buffer
            for line in tools.DEBUG_PRINT_BUFFER:
                debug_y+=10
                debug_caption = ""
                if line:
                    debug_caption = "-" + line
                self.add_text(caption=debug_caption, size=20, color=(255, 255, 255), y=debug_y, x=14)
        
