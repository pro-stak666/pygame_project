import pygame as pg
from os import path
from random import random, choice, randrange
import csv
import datetime as dt


class DataManager:
    def __init__(self):
        if not path.isfile("data/data.csv"):
            with open('data/data.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['max_score', 'volume', 'difficult', 'full_screen', '1_achievement', '2_achievement',
                                 '3_achievement'])
                time = dt.timedelta()
                writer.writerow([0, 1, 0, 1, 0, 0, time])
        self.data = csv.DictReader(open('data/data.csv', encoding='utf-8'), delimiter=';').__next__()
        for i in self.data:
            if ':' not in self.data[i]:
                self.data[i] = int(self.data[i])

    def save(self):
        self.data['1_achievement'] = round(self.data['1_achievement'])
        t = str(self.data['3_achievement']).split(':')
        t = dt.timedelta(hours=int(t[0]), minutes=int(t[1]), seconds=int(t[2]))
        self.data['3_achievement'] = t + ALL_TIME

        with open('data/data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(self.data.keys()), delimiter=';')
            writer.writeheader()
            writer.writerow(self.data)


class Button(pg.sprite.Sprite):
    def __init__(self, x, y, active_image, inactive_image, action=None):
        super(Button, self).__init__()
        self.images = [load_image(inactive_image), load_image(active_image)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.x, self.rect.y = x, y
        self.action = action

    def draw(self):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        if self.x < mouse[0] < self.x + self.rect.width and self.y < mouse[1] < self.y + self.rect.height:
            screen.blit(self.images[0], (self.x, self.y))

            if click[0] == 1 and self.action is not None:
                pass  # звук нажатия
                self.action()
                clock.tick(10)
        else:
            screen.blit(self.images[1], (self.x, self.y))


class Asteroid(pg.sprite.Sprite):
    def __init__(self):
        super(Asteroid, self).__init__(asteroids)
        self.image_original = load_image(f"asteroid{get_probability_asteroid()}.png")
        self.rect_original = self.image_original.get_rect()
        self.rect_original.x = WIDTH + 100
        self.rect_original.y = randrange(HEIGHT)

        self.vx = randrange(-5, -1)
        self.vy = 0 if 0 < random() < 0.91 else choice([1, -1])

        if self.vy == 1:
            self.rect_original.y = randrange(HEIGHT // 2)
        elif self.vy == -1:
            self.rect_original.y = randrange(HEIGHT - HEIGHT // 2)

        self.angle = 0
        self.diff_angle = randrange(-2, 3)

        self.image, self.rect = rotate_image(self.image_original, self.angle)
        self.rect.center = self.rect_original.center

        self.mask = pg.mask.from_surface(self.image)

    def update(self, args):
        for i in args:
            if i.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(i.pos):
                self.destroy()

        if self.rect.x < -100:
            self.kill()
        self.image, self.rect = rotate_image(self.image_original, self.angle)
        self.mask = pg.mask.from_surface(self.image)
        self.rect_original = self.rect_original.move(self.vx, self.vy)
        self.rect.center = self.rect_original.center
        self.angle += self.diff_angle

    def destroy(self):
        global SCORE
        self.kill()
        MANAGER.data['2_achievement'] += 1
        SCORE += 1


class Ship(pg.sprite.Sprite):
    def __init__(self):
        super(Ship, self).__init__(player)
        self.images_idle = [load_image('ship_idle_0.png'), load_image('ship_idle_1.png')]
        self.images_down = [load_image('ship_down_0.png'), load_image('ship_down_1.png'),
                            load_image('ship_down_2.png'), load_image('ship_down_3.png')]
        self.images_up = [load_image('ship_up_0.png'), load_image('ship_up_1.png'),
                          load_image('ship_up_2.png'), load_image('ship_up_3.png')]
        self.k_idle = 0
        self.k_down = 0
        self.k_up = 0

        self.image = self.images_idle[self.k_idle]
        self.rect = self.image.get_rect()
        self.rect.height = 44

        self.rect.x = 100
        self.rect.y = HEIGHT // 2 - self.rect.height // 2

        self.mask = pg.mask.from_surface(self.image)

        self.time = dt.timedelta(hours=0, minutes=0, seconds=0)

    def update(self, event_=None):
        if self.k_idle == 100:
            self.k_idle = 0
        self.image = self.images_idle[self.k_idle // 50]
        self.k_idle += 1

        keys = pg.key.get_pressed()

        if keys[pg.K_w] and not keys[pg.K_s]:
            self.rect = self.rect.move(0, -1) if 0 < self.rect.y - 1 else self.rect
            if self.k_up != 200:
                self.image = self.images_up[self.k_up // 50]
                self.k_up = self.k_up + 1 if self.k_up < 198 else 100
        else:
            if self.k_up:
                self.image = self.images_up[0]
            self.k_up = 0

        if keys[pg.K_s] and not keys[pg.K_w]:
            self.rect = self.rect.move(0, 1) if self.rect.y + 1 < HEIGHT - 44 else self.rect
            if self.k_down != 200:
                self.image = self.images_down[self.k_down // 50]
                self.k_down = self.k_down + 1 if self.k_down < 198 else 100
        else:
            if self.k_down:
                self.image = self.images_down[0]
            self.k_down = 0

        if keys[pg.K_a] and not keys[pg.K_d]:
            self.rect = self.rect.move(-1, 0) if self.rect.x > 0 else self.rect

        if keys[pg.K_d] and not keys[pg.K_a]:
            self.rect = self.rect.move(1, 0) if self.rect.x < WIDTH // 2 else self.rect

        if pg.sprite.spritecollideany(self, asteroids):
            for asteroid in asteroids:
                if pg.sprite.collide_mask(self, asteroid):
                    self.die()
                    break

        MANAGER.data['1_achievement'] += 0.01

    def die(self):
        MANAGER.data['max_score'] = int(SCORE) if int(MANAGER.data['max_score']) < int(SCORE) else MANAGER.data[
            'max_score']
        menu()


def load_image(name: str) -> pg.image:
    fullname = path.join('data', name)
    if not path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        quit()
    return pg.image.load(fullname)


def rotate_image(surface: pg.surface, angle: int) -> pg.surface:
    rotated_surface = pg.transform.rotozoom(surface, angle, 1)
    rotated_rect = rotated_surface.get_rect(center=surface.get_rect().center)
    return rotated_surface, rotated_rect


def get_probability_asteroid() -> int:
    r = random()
    if 0.999 < r < 1:
        return 7
    elif 0.93 < r < 1:
        return choice([5, 6])
    else:
        return choice([1, 2, 3, 4])


def exit_app():
    MANAGER.save()
    quit()


def menu() -> None:
    global x_bkgd, rel_x_bkgd
    is_menu = True
    cursor.image = load_image("cursor_menu.png")
    h = (HEIGHT + 250) // 5
    but_start = Button(WIDTH // 2 - 125, h, 'start_but_0.png', 'start_but_1.png', start_game)
    but_settings = Button(WIDTH // 2 - 125, h + 70, 'settings_but_0.png', 'settings_but_1.png', show_settings)
    but_progress = Button(WIDTH // 2 - 125, h + 140, 'progress_but_0.png', 'progress_but_1.png', show_progress)
    but_titles = Button(WIDTH // 2 - 125, h + 210, 'titles_but_0.png', 'titles_but_1.png', show_titles)
    but_exit = Button(WIDTH // 2 - 125, h + 280, 'exit_but_0.png', 'exit_but_1.png', exit_app)

    while is_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                MANAGER.save()
                quit()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        but_start.draw()
        but_settings.draw()
        but_progress.draw()
        but_titles.draw()
        but_exit.draw()

        all_sprites.draw(screen)
        pg.display.flip()
        clock.tick(fps)


def pause() -> None:
    global x_bkgd, rel_x_bkgd
    is_pause = True
    cursor.image = load_image("cursor_menu.png")
    while is_pause:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    cursor.image = load_image("cursor.png")
                    is_pause = False
                if event.key == pg.K_ESCAPE:
                    menu()

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        print_text("TO CONTINUE PRESS ENTER", 750, 400)
        print_text("TO EXIT PRESS ESCAPE", 750, 500)

        all_sprites.draw(screen)
        asteroids.draw(screen)
        player.draw(screen)

        print_text(f"SCORE: {int(SCORE)}", 1550, 10)

        pg.display.flip()
        clock.tick(fps)


def print_text(text, x, y, font_color=(255, 255, 255), font="data/Comfortaa.ttf", font_size=30) -> None:
    font = pg.font.Font(font, font_size)
    text = font.render(text, True, font_color)
    screen.blit(text, (x, y))


def start_game() -> None:
    global WIDTH, HEIGHT, screen, fps, clock, background, x_bkgd, all_sprites, asteroids, player, cursor, PLAYER, \
        SCORE, ALL_TIME, one_second

    PLAYER.rect.x = 100
    PLAYER.rect.y = HEIGHT // 2 - PLAYER.rect.height // 2

    asteroids.empty()
    cursor.image = load_image("cursor.png")

    SCORE = 0

    running = True

    while running:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            if event.type == SPAWN_ASTEROIDS:
                Asteroid()
            if event.type == TIME_COUNT:
                ALL_TIME += one_second
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pause()

        PLAYER.update(events)

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 1.15
        # отрисовка фона

        for i in asteroids:
            i.update(events)

        asteroids.draw(screen)
        player.draw(screen)
        all_sprites.draw(screen)

        SCORE += 0.01
        print_text(f"SCORE: {int(SCORE)}", WIDTH - 300, 10)

        pg.display.flip()
        clock.tick(fps)


def show_titles() -> None:  # game designer, producer, artist, programmer, developer
    global x_bkgd, rel_x_bkgd
    is_titles = True

    but_back = Button(WIDTH - 300, HEIGHT - 100, "back_but_0.png", "back_but_1.png", menu)

    while is_titles:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        print_text("COMPANY - RepeekGames", 200, 100, font_size=50)
        print_text("GAME DESIGNER - Mineev Kirill", 200, 250, font_size=50)
        print_text("PRODUCER - Mineev Kirill", 200, 350, font_size=50)
        print_text("PAINTER - Mineev Kirill", 200, 450, font_size=50)
        print_text("PROGRAMMER - Mineev Kirill", 200, 550, font_size=50)
        print_text("DEVELOPER - Mineev Kirill", 200, 650, font_size=50)

        but_back.draw()

        all_sprites.draw(screen)

        pg.display.flip()
        clock.tick(fps)


def show_settings() -> None:
    global x_bkgd, rel_x_bkgd
    is_settings = True

    but_back = Button(WIDTH - 300, HEIGHT - 100, "back_but_0.png", "back_but_1.png", menu)
    but_easy = Button(900, HEIGHT // 6 + 330, "easy_but_0.png", "easy_but_1.png")
    but_medium = Button(1120, HEIGHT // 6 + 330, "medium_but_0.png", "medium_but_1.png")
    but_hard = Button(1340, HEIGHT // 6 + 330, "hard_but_0.png", "hard_but_1.png")
    but_1920x1080 = Button(1100, HEIGHT // 6 + 530, "1920x1080_but_0.png", "1920x1080_but_1.png")
    but_1600x900 = Button(800, HEIGHT // 6 + 530, "1600x900_but_0.png", "1600x900_but_1.png")

    while is_settings:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        but_back.draw()

        volume = 1  # MANAGER.data['volume']
        but_offset = (WIDTH - 950 - 630) // 2
        but_easy.x = 800
        but_medium.x = 800 + 210 + but_offset
        but_hard.x = 800 + 210 + 210 + but_offset + but_offset

        but_1920x1080.x = 1050 + WIDTH - 950 - 500

        print_text("MUSIC", 100, HEIGHT // 6 - 70, font_size=80)
        print_text('+', WIDTH - 150, HEIGHT // 6 - 125, font_size=150, font_color='green')
        print_text('-', 800, HEIGHT // 6 - 125, font_size=150, font_color='red')
        x, y, w, h = 900, HEIGHT // 6, (WIDTH - 1000) // 10 - 20, 10
        for i in range(round(volume * 10)):
            pg.draw.rect(screen, 'green', (x, y, w, h))
            x += w + 10
            h += 10
            y -= 10

        print_text("SOUNDS", 100, HEIGHT // 6 + 130, font_size=80)
        print_text('+', WIDTH - 150, HEIGHT // 6 + 75, font_size=150, font_color='green')
        print_text('-', 800, HEIGHT // 6 + 75, font_size=150, font_color='red')
        x, y, w, h = 900, HEIGHT // 6 + 200, (WIDTH - 1000) // 10 - 20, 10
        for i in range(round(volume * 10)):
            pg.draw.rect(screen, 'green', (x, y, w, h))
            x += w + 10
            h += 10
            y -= 10

        print_text("DIFFICULT", 100, HEIGHT // 6 + 330, font_size=80)
        but_easy.draw()
        but_medium.draw()
        but_hard.draw()

        print_text("SCREEN SIZE", 100, HEIGHT // 6 + 530, font_size=80)
        but_1600x900.draw()
        but_1920x1080.draw()

        all_sprites.draw(screen)
        pg.display.flip()
        clock.tick(fps)


def show_progress() -> None:
    global x_bkgd, rel_x_bkgd
    is_progress = True

    but_back = Button(WIDTH - 300, HEIGHT - 100, "back_but_0.png", "back_but_1.png", menu)
    trophy_img = load_image('trophy.png')
    ship_img = load_image('ship_down_3.png')
    asteroid_img = pg.transform.scale(load_image('asteroid3.png'), (128, 128))
    clock_img = load_image('clock.png')

    MANAGER.save()

    while is_progress:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        print_text(f"BEST", 150, 100, font_size=70)
        print_text(f"SCORE", 150, 170, font_size=70)
        print_text(f"{MANAGER.data['max_score']}", 650, 100, font_size=140)
        screen.blit(trophy_img, (38, 80))

        print_text(f"DISTANCE", 150, 300, font_size=70)
        print_text(f"TRAVELED", 150, 370, font_size=70)
        print_text(f"{round(MANAGER.data['1_achievement'] / 1000, 2)}", 650, 300, font_size=140)
        screen.blit(ship_img, (11, 350))

        print_text(f"ASTEROIDS", 150, 500, font_size=70)
        print_text(f"DESTROYED", 150, 570, font_size=70)
        print_text(f"{MANAGER.data['2_achievement']}", 650, 500, font_size=140)
        screen.blit(asteroid_img, (11, 510))

        print_text(f"TOTAL", 150, 700, font_size=70)
        print_text(f"FLIGHT TIME", 150, 770, font_size=70)
        t = int(MANAGER.data['3_achievement'].total_seconds())
        print_text(
            f"{dt.datetime(2022, 1, 1, hour=t // 3600, minute=t // 60, second=t - t // 3600 * 3600 - t // 60 * 60).strftime('%H:%M:%S')}",
            650, 700, font_size=140)
        screen.blit(clock_img, (11, 710))

        but_back.draw()

        all_sprites.draw(screen)

        pg.display.flip()
        clock.tick(fps)


if __name__ == "__main__":
    pg.init()
    size = WIDTH, HEIGHT = 1600, 900
    screen = pg.display.set_mode(size)
    fps = 100
    clock = pg.time.Clock()
    pg.display.set_caption("plads")

    background = pg.image.load("data/space.png").convert()
    x_bkgd = 0

    all_sprites = pg.sprite.Group()
    asteroids = pg.sprite.Group()
    player = pg.sprite.Group()

    cursor = pg.sprite.Sprite(all_sprites)
    cursor.image = load_image("cursor.png")
    cursor.rect = cursor.image.get_rect()

    SPAWN_ASTEROIDS = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_ASTEROIDS, 1000)

    TIME_COUNT = pg.USEREVENT + 1
    pg.time.set_timer(TIME_COUNT, 1000)

    PLAYER = Ship()

    SCORE = 0
    ALL_TIME = dt.timedelta()
    one_second = dt.timedelta(seconds=1)

    MANAGER = DataManager()

    menu()
