import pygame
import pygame.freetype
import random
import csv
import sys
from pygame import mixer


class SimpleScene:
    FONT = None

    def __init__(self, next_scene, *text):
        # Load background image
        pygame.mixer.init()
        pygame.display.set_caption("MeoWord")
        icon = pygame.image.load("boba/ram.png")
        pygame.display.set_icon(icon)
        click_sound = pygame.mixer.Sound('boba/click.wav')
        mixer.music.load("boba/cats.mp3")
        mixer.music.play(-1)
        pygame.mixer.music.set_volume(1.0)
        self.exit_button = Button(pygame.Rect(290, 520, 175, 40), 'Exit')
        self.background = pygame.image.load("boba/meow.png")  # Replace 'background_image.jpg' with your image file path
        self.background = pygame.transform.scale(self.background, (800, 600))

        if text:
            if SimpleScene.FONT == None:
                # Load custom font
                SimpleScene.FONT = pygame.freetype.Font("boba/orrr.ttf", 30)  # Replace 'your_font.ttf' with your font file path
            y = 80
            for line in text:
                if "Welcome to the quiz" in line:
                    # Render larger font for "Welcome to the quiz"
                    SimpleScene.FONT.render_to(self.background, (90, 50), line, pygame.Color(255, 163, 39), size=64)
                else:
                    # Render regular font for other text
                    SimpleScene.FONT.render_to(self.background, (230, y), line, pygame.Color(255, 163, 39))
                y += 100

        self.next_scene = next_scene
        self.additional_text = None

    def start(self, text):
        self.additional_text = text

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        if self.additional_text:
            # Calculate the position to center the text vertically and horizontally
            text_height = len(self.additional_text) * 100
            center_y = (600 - text_height) / 2
            for i, line in enumerate(self.additional_text):
                # Calculate position for each line
                line_y = center_y + i * 100
                SimpleScene.FONT.render_to(screen, (50, line_y), line, pygame.Color(255, 163, 39))
        self.exit_button.draw(screen, SimpleScene.FONT)

    def update(self, events, dt):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return (self.next_scene, None)
        self.exit_button.update(events)
        if self.exit_button.clicked:
            pygame.quit()
            sys.exit()


class SettingScene:
    LEVELS = ['Beginner', 'Intermediate', 'Advanced']

    def __init__(self):
        self.background = pygame.Surface((800, 600))
        self.background = pygame.image.load("boba/meow.png")

        if SimpleScene.FONT == None:
            SimpleScene.FONT = pygame.freetype.SysFont('boba/orrr.ttf', 40)

        # Load the click sound for buttons
        self.click_sound = pygame.mixer.Sound('boba/click.wav')

        SimpleScene.FONT.render_to(self.background, (99, 49), 'Select your difficulty level',
                                   pygame.Color(255, 163, 39), size=50)

        self.rects = []
        x = 200
        y = 150
        for level in SettingScene.LEVELS:
            rect = pygame.Rect(x, y, 400, 70)
            self.rects.append((rect, level))
            y += 100

        # Add return to main menu button
        self.return_to_menu_button = Button(pygame.Rect(275, 500, 250, 40), 'Return to Main Menu')

    def start(self, *args):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        for rect, level in self.rects:
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, pygame.Color(255, 163, 39), rect, border_radius=80)
            pygame.draw.rect(screen, pygame.Color(255, 163, 39), rect, 5, border_radius=80)
            SimpleScene.FONT.render_to(screen, (rect.x + 29, rect.y + 29), level, pygame.Color('white'))

        # Draw return to main menu button
        self.return_to_menu_button.draw(screen, SimpleScene.FONT)

    def update(self, events, dt):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, level in self.rects:
                    if rect.collidepoint(event.pos):
                        self.click_sound.play()  # Play the click sound when a difficulty level button is clicked
                        return ('GAME', GameState(level))
                if self.return_to_menu_button.rect.collidepoint(event.pos):
                    self.click_sound.play()
                    return ('TITLE', None)  # Return to main menu if the button is clicked


class GameState:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.questions = self.load_questions(difficulty)
        self.current_question = None
        self.right = 0
        self.wrong = 0
        self.coins = 0
        self.current_question_number = 1  # Initialize current question number to 1
        self.total_questions = len(self.questions)  # Initialize total questions to the number of questions

    def load_questions(self, difficulty):
        questions = []
        with open(f'boba/{difficulty.lower()}_questions.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                question = row[0]
                options = row[1:5]
                correct_answer_index = int(row[5]) - 1
                questions.append((question, options, correct_answer_index))
        return questions

    def pop_question(self):
        if self.questions:
            q = random.choice(self.questions)
            self.questions.remove(q)
            self.current_question = q
            return q
        else:
            return None

    def answer(self, answer_index):
        if answer_index - 1 == self.current_question[2]:
            self.right += 1
            self.coins += 1  # Increment coin count for correct answer
        else:
            self.wrong += 1

    def get_current_question_number(self):
        return self.current_question_number

    def increment_question_number(self):
        self.current_question_number += 1

    def next_question(self):
        # Move to the next question
        self.current_question_number += 1
        if self.current_question_number > self.total_questions:
            # If all questions for the level are finished, reset the current question number to 1
            self.current_question_number = 1


    def get_result(self):
        return f'{self.right} answers correct', f'{self.wrong} answers wrong', 'Good!' if self.right > self.wrong else 'You can do better!'


class Button:
    def __init__(self, rect, text):
        self.rect = rect
        self.text = text
        self.hovered = False
        self.clicked = False
        self.click_sound = pygame.mixer.Sound('boba/click.wav')
        self.text_color = pygame.Color('white')  # Default text color
        self.hovered_text_color = pygame.Color(255, 244, 142)  # Text color when hovered

    def draw(self, screen, font):
        if self.hovered:
            color = pygame.Color(255, 244, 142)
            text_color = (255, 163, 39)  # Use hovered text color
        else:
            color = pygame.Color(255, 163, 39)
            text_color = self.text_color  # Use default text color

        pygame.draw.rect(screen, color, self.rect,  border_radius=80)
        pygame.draw.rect(screen, pygame.Color(255, 163, 39), self.rect, 5,  border_radius=80)
        font.render_to(screen, (self.rect.x + 20, self.rect.y + 20), self.text, text_color, size=20)

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.hovered:
                    self.clicked = True
                    self.click_sound.play()



class GameScene:
    ANIMATION_DURATION = 1000  # milliseconds

    def __init__(self):
        self.buttons = []
        x = 200
        y = 200
        for n in range(4):
            rect = pygame.Rect(x, y, 350, 50)  # Adjusted rect size for buttons
            self.buttons.append(Button(rect, ""))
            y += 60

        self.selected_answer = None
        self.animation_timer = 0
        self.show_correct = False
        self.show_wrong = False
        # Add return to main menu button
        self.return_to_menu_button = Button(pygame.Rect(275, 500, 250, 40), 'Return to Main Menu')

    def start(self, gamestate):
        self.background = pygame.Surface((800, 600))
        self.background = pygame.image.load("boba/meow.png")
        self.gamestate = gamestate
        self.total_questions = len(gamestate.questions)  # Set the total number of questions
        self.current_question_number = 1  # Initialize the current question number

        question_info = gamestate.pop_question()
        question = question_info[0]
        options = question_info[1]

        # Set button texts
        for i in range(min(len(self.buttons), len(options))):
            self.buttons[i].text = options[i]
        SimpleScene.FONT.render_to(self.background, (130, 70), question, pygame.Color(255, 163, 39), size=34)

        # Increment current question number if there are remaining questions
        if len(gamestate.questions) < self.total_questions:
            self.current_question_number += 1  # self.total_questions # - len(gamestate.questions)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        # Display question progress
        progress_text = f"{self.total_questions}"
        SimpleScene.FONT.render_to(screen, (710, 30), progress_text, pygame.Color(255, 163, 39), size=50)

        for button in self.buttons:
            button.draw(screen, SimpleScene.FONT)

        # Draw return to main menu button
        self.return_to_menu_button.draw(screen, SimpleScene.FONT)

    def update(self, events, dt):
        if self.animation_timer > 0:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                self.show_correct = False
                self.show_wrong = False

        for button in self.buttons:
            button.update(events)
            if button.clicked:
                self.selected_answer = self.buttons.index(button)
                self.gamestate.answer(self.selected_answer + 1)
                if self.selected_answer + 1 == self.gamestate.current_question[2]:
                    self.show_correct = True
                else:
                    self.show_wrong = True
                self.animation_timer = GameScene.ANIMATION_DURATION
                if self.gamestate.questions:
                    self.current_question_number += 1  # Increment current question number
                    return ('GAME', self.gamestate)
                else:
                    return ('RESULT', self.gamestate.get_result())

        # Check if return to main menu button is clicked
        self.return_to_menu_button.update(events)
        if self.return_to_menu_button.clicked:
            return ('TITLE', None)  # Return to main menu if the button is clicked

        return None






class ResultScene(SimpleScene):
    def __init__(self):
        super().__init__('TITLE', 'Here is your result:')
        self.play_again_button = Button(pygame.Rect(290, 450, 175, 40), 'Play Again')

    def draw(self, screen):
        super().draw(screen)
        self.play_again_button.draw(screen, SimpleScene.FONT)

    def update(self, events, dt):
        super().update(events, dt)
        self.play_again_button.update(events)
        if self.play_again_button.clicked:
            return ('TITLE', None)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    dt = 0
    scenes = {
        'TITLE': SimpleScene('SETTING', 'Welcome to the quiz', '', '', '', '   press [SPACE] to start'),
        'SETTING': SettingScene(),
        'GAME': GameScene(),
        'RESULT': ResultScene(),
    }
    scene = scenes['TITLE']

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return

        result = scene.update(events, dt)  # Pass 'dt' as an argument
        if result:
            next_scene, state = result
            if next_scene:
                scene = scenes[next_scene]
                scene.start(state)

        # Pass 'screen' to the draw() method
        scene.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60)


if __name__ == "__main__":
    main()
