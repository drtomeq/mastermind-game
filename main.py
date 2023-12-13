''' Mastermind game
    Requires the pygame package
    This time it uses a GUI, sprites and external files
    These include the background image, music, sound effects 
    If you are installing on your own device, 
    it is probably easiest to have all the files in the same folder.

    The idea is to guess the colour sequence.
    After each guess you will be told how many colours were in the sequence
    And how many of them were in the right place
    After several guesses you should be able to deduce the correct sequence
    
    In 1 player mode a random sequence is set
    In 2 player one player chooses the correct sequence
    And the other tries to guess it
    
    The game is customisable.
    If you go to mmconstants you can adjust values such as
    1) How many lives you have at the start
    2) How many colours to choose from
    3) How long the sequence is
    4) The files used for music, sound effects and the background
        (make sure you have the files in the folder first)
    5) The font used (use one that comes with pygame)
    6) The size of different components
    7) The frame rate (fps), 
        (if set high it may be limited by the device performance or display capability)
        
    While I, Tom Quinn, did all the coding I would like to give credit for 
    the sound effects (start.wav, win.wav, lose.wav, blip.wav) and background.jpg
    Unfortunately I can no longer find the details of those that came up with this, sorry.
    If you know, I would like to add credit here
    Credit to Mordechai Meirovitz for coming up with the original Mastermind board game
    (although it is likely based on similar earlier games)
    I accept full responsibility for the truly awful midi tune 
    
    Play to your heart's content
    Would be happy to know if you use this at all
    Get in touch with ideas, comments, suggestions, bugs etc'''

from random import randrange
import pygame as pg
import mmcolours
from mmconstants import *

pg.init()

GAME_FONT = pg.font.SysFont(GAME_FONT, FONTSIZE)
START_FONT = pg.font.SysFont(TITLE_FONT, 30)

pg.mixer.music.load(MUSIC_FILE)
pg.mixer.music.set_volume(0.5)
pg.mixer.music.play(-1) #play non-stop
start_sound=pg.mixer.Sound(START_SOUND_FILE)
lose_sound=pg.mixer.Sound(LOSE_SOUND_FILE)
select_sound=pg.mixer.Sound(SELECT_SOUND_FILE)
win_sound=pg.mixer.Sound(WIN_SOUND_FILE)

myClock = pg.time.Clock()
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BG_IMPORT = pg.image.load(BG_FILE)
BG_IMAGE = pg.transform.scale(BG_IMPORT, (WIN_WIDTH, WIN_HEIGHT))

COUNTER_COLOURS = mmcolours.colour_list()


class Counter:
    def __init__(self, x, y, colour, diameter=CIRCLE_SIZE):
        self.radius = diameter / 2
        self.colour = colour
        self.x = x
        self.y = y

    def draw_counter(self):
        pg.draw.circle(WIN, self.colour, (self.x, self.y), self.radius)

    def in_mouse_pos(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        in_x_range = self.x - self.radius < mouse_x < self.x + self.radius
        in_y_range = self.y - self.radius < mouse_y < self.y + self.radius
        return in_x_range and in_y_range

    def follow_mouse(self):
        self.x, self.y = pg.mouse.get_pos()

    def colour_to_number(self):
        for pos, val in enumerate(COUNTER_COLOURS):
            if val == self.colour:
                return pos


class Row:
    def __init__(self, starting_colours, y):
        circle_number = len(starting_colours)
        self.y = y
        # spacing on left and right ends as well as inbetween
        self.width = (CIRCLE_SIZE + CIRCLE_SPACING) * circle_number + CIRCLE_SPACING
        self.height = CIRCLE_SIZE + 2 * CIRCLE_SPACING
        self.x = (WIN_WIDTH - self.width) / 2
        self.counters = self.init_colours(starting_colours)

    def init_colours(self, colours):
        counter_list = []
        counter_x = self.x + CIRCLE_SPACING + CIRCLE_SIZE/2
        counter_y = self.y + CIRCLE_SPACING + CIRCLE_SIZE/2
        for colour in colours:
            counter_list.append(Counter(counter_x, counter_y, colour))
            counter_x += CIRCLE_SPACING + CIRCLE_SIZE
        return counter_list

    def draw_counters(self):
        pg.draw.rect(WIN, COUNTER_BG, pg.Rect(self.x, self.y, self.width, self.height))
        for i in self.counters:
            i.draw_counter()


class SelectRow(Row):
    def __init__(self):
        starting_y = WIN_HEIGHT - CIRCLE_SIZE + 2 * CIRCLE_SPACING - BOTTOM_MARGIN
        super().__init__(COUNTER_COLOURS, starting_y)
        self.chosen = None

    def select_from_row(self):
        for i in self.counters:
            if i.in_mouse_pos():
                self.chosen = Counter(i.x, i.y, i.colour)
        return self.chosen


my_select_row = SelectRow()


class ChooseRow(Row):
    def __init__(self):
        y = WIN_HEIGHT - BOTTOM_MARGIN - 2 * ROW_HEIGHT - CIRCLE_SPACING
        starting_colours = [BLANK_COLOUR for i in range(ROW_SIZE)]
        super(ChooseRow, self).__init__(starting_colours, y)
        self.selected = [False for i in range(ROW_SIZE)]

    def add_colour(self, new_colour):
        for pos, val in enumerate(self.counters):
            if val.in_mouse_pos():
                val.colour = new_colour
                self.selected[pos] = True

    def chosen_all_colours(self):
        return False not in self.selected

    def colour_to_sequence(self):
        sequence = []
        for i in self.counters:
            sequence.append(i.colour_to_number())
        return sequence


class Sequence:
    def __init__(self, numbers, y, correct = None):
        self.numbers = numbers
        self.row = Row(self.colours_from_numbers(), y)
        if correct:
            self.info = self.get_info(correct)

    def right_number(self, correct):
        count = 0
        for digit in self.numbers:
            if digit in correct:
                count += 1
        return count

    def right_position(self, correct):
        count = 0
        for position in range(len(self.numbers)):
            if self.numbers[position] == correct[position]:
                count += 1
        return count

    def get_info(self, correct):
        return str(self.right_number(correct)) + " counters have the right colour " + \
               str(self.right_position(correct)) + " in the right place"

    def colours_from_numbers(self):
        return [COUNTER_COLOURS[i] for i in self.numbers]

'''   %%%%%%%%%%%%%% Main Game  %%%%%%%%%%%%%%   '''

def select_colours(previous_choices=None, lives=None):
    my_choice = ChooseRow()
    text = "Choose Your Colours"
    chosen: Counter = None
    while True:
        myClock.tick(FPS)
        if chosen:
            chosen.follow_mouse()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                left, middle, right = pg.mouse.get_pressed()
                if left:
                    chosen = my_select_row.select_from_row()
                    if chosen:
                        my_choice.add_colour(chosen.colour)
                        if my_choice.chosen_all_colours():
                            return my_choice.colour_to_sequence()
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if lives:
                text = "you have " + str(lives) + " lives left"
        draw(my_select_row, current_selection=chosen, chosen_row=my_choice, message=text, past_choices=previous_choices)


def draw(select_row: SelectRow = None, chosen_row: ChooseRow = None,
         current_selection: Counter = None, past_choices =None,
         message=None, background=False, title=None, pause=0,
         special_row: Row = None):
    if background:
        WIN.blit(BG_IMAGE, (0, 0))
    else:
        WIN.fill(BG_COLOUR)
    if title:
        title_image = START_FONT.render("MASTERMIND", True, TITLE_COLOUR)
        centre = title_image.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
        WIN.blit(title_image, (centre[0], centre[1] - 50))
    if message:
        text_image = GAME_FONT.render(message, True, FONTCOLOUR)
        centre = text_image.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
        WIN.blit(text_image, (centre[0], TEXT_POSITION))
    if select_row:
        select_row.draw_counters()
    if chosen_row:
        chosen_row.draw_counters()
    if current_selection:
        current_selection.draw_counter()
    if past_choices:
        for i in past_choices:
            i.row.draw_counters()
            text = i.info
            row_text = GAME_FONT.render(text, 1, FONTCOLOUR)
            centre = row_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
            WIN.blit(row_text, (centre[0], i.row.y + ROW_HEIGHT))
    if special_row:
        special_row.draw_counters()
    pg.display.update()
    if pause > 0:
        pg.time.delay(pause)


def main_game(correct_sequence):
    lives = STARTING_LIVES
    guesses_so_far = []
    y_pos = 0
    while True:
        attempt = select_colours(guesses_so_far, lives)
        if attempt == correct_sequence:
            ans = Sequence(correct_sequence, 100)
            pg.mixer.Sound.play(win_sound)
            draw(message="you got it", pause=3000, special_row=ans.row)
            return
        lives -= 1
        if lives < 0:
            ans = Sequence(correct_sequence, 100)
            pg.mixer.Sound.play(lose_sound)
            draw(message="Game over. Correct answer was", pause=3000,
                 special_row=ans.row)
            return
        pg.mixer.Sound.play(select_sound)
        guess = Sequence(attempt, y_pos, correct_sequence)
        guesses_so_far.append(guess)
        y_pos += ROW_HEIGHT + FONTSIZE


''' ####################### start the game ####################### '''


def start_game():
    draw(background=True, title="Mastermind",
         message="Find the right sequence! Press Enter")
    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    pg.mixer.Sound.play(start_sound)
                    draw(background=True, title="Mastermind",
                         message="1 player game", pause=3000)
                    return random_sequence()
                elif event.key == pg.K_2:
                    pg.mixer.Sound.play(start_sound)
                    draw(background=True, title="Mastermind",
                         message="2 player game", pause=3000)
                    draw(message="P1 Choose Colours for P2 to guess, P2 Look Away", pause = 6000)
                    my_sequence = select_colours()
                    pg.mixer.Sound.play(select_sound)
                    draw(message="Swap players", pause=3000)
                    pg.mixer.Sound.play(start_sound)
                    return my_sequence
                else:
                    draw(background=True, title="Mastermind",
                         message="press 1 or 2")
                    pg.mixer.Sound.play(select_sound)
            if event.type == pg.QUIT:
                pg.quit()
                quit()


def random_sequence():
    return [randrange(NUMBER_OPTIONS) for i in range(ROW_SIZE)]



def game():
    while True:
        correct = start_game()
        main_game(correct)
game()

