import pygame as pg
from os import path, environ
from random import random, choice, randrange
import csv
import datetime as dt
from math import sqrt


class DataManager:
    def __init__(self):
        if not path.isfile("data/data.csv"):
            with open('data/data.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['max_score', 'volume_music', 'volume_sound', 'difficult', 'full_screen', '1_achievement', '2_achievement',
                                 '3_achievement'])
                time = dt.timedelta()
                writer.writerow([0, 1, 1, 1, 1, 0, 0, time])
        self.data = csv.DictReader(open('data/data.csv', encoding='utf-8'), delimiter=';').__next__()
        for i in self.data:
            if ':' not in self.data[i]:
                self.data[i] = float(self.data[i])

    def save(self):
        global ALL_TIME
        self.data['1_achievement'] = round(self.data['1_achievement'])
        t = str(self.data['3_achievement']).split(':')
        t = dt.timedelta(hours=int(t[0]), minutes=int(t[1]), seconds=int(t[2]))
        self.data['3_achievement'] = t + ALL_TIME
        print(ALL_TIME)
        ALL_TIME = dt.timedelta()
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
        r = get_probability_asteroid()
        self.live = 2 if r == 7 else 1
        self.image_original = load_image(f"asteroid{r}.png")
        self.rect_original = self.image_original.get_rect()
        self.rect_original.x = WIDTH + 100
        self.rect_original.y = randrange(HEIGHT)

        self.vx = randrange(-8, -2)
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

        self.boom_count = 5

    def update(self, args):
        if self.live:
            for i in args:
                if i.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint((i.pos[0] + 16, i.pos[1] + 16)):
                    if PLAYER.ammunition > 0 and self.live == 1:
                        sound_shoot.play()
                        Bullet(self, (PLAYER.rect.x, PLAYER.rect.y))
                        PLAYER.ammunition -= 1
                        break

            if self.rect.x < -100:
                self.kill()
            self.image, self.rect = rotate_image(self.image_original, self.angle)
            self.mask = pg.mask.from_surface(self.image)
            self.rect_original = self.rect_original.move(self.vx, self.vy)
            self.rect.center = self.rect_original.center
            self.angle += self.diff_angle

            if pg.sprite.spritecollideany(self, bullets):
                for b in bullets:
                    if pg.sprite.collide_rect(self, b) and self.live == 1:
                        self.destroy()
                        b.die()
                        sound_boom_asteroid.play()
                        break
        elif self.live == 0:
            if self.boom_count == 35:
                self.kill()
            self.image = load_image(f'boom_{self.boom_count // 5}.png')
            self.boom_count += 1
            self.rect_original = self.rect_original.move(self.vx, self.vy)
            self.rect.center = self.rect_original.center
            print_text("+1", self.rect_original.x + 64, self.rect_original.y - self.boom_count)

    def destroy(self):
        global SCORE
        self.live = False
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

        self.ammunition = 5
        self.ammunition_regen = 4
        self.ammunition_regen_count = 0

        self.boom_count = 5
        self.live = True

    def update(self, event_=None):
        if self.live:
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
                    if pg.sprite.collide_mask(self, asteroid) and asteroid.live == 1:
                        asteroid.destroy()
                        self.die()
                        sound_boom_ship.play()
                        break

            if self.ammunition < 5:
                for i in event_:
                    if i.type == TIME_COUNT_EVENT:
                        self.ammunition_regen_count += 1
                if self.ammunition_regen_count == self.ammunition_regen:
                    self.ammunition_regen_count = 0
                    self.ammunition += 1

            MANAGER.data['1_achievement'] += 0.01
        else:
            if self.boom_count == 55:
                menu()
            self.image = load_image(f'boom_ship_{self.boom_count // 5}.png')
            self.boom_count += 1

    def die(self):
        MANAGER.data['max_score'] = int(SCORE) if int(MANAGER.data['max_score']) < int(SCORE) else MANAGER.data[
            'max_score']
        self.live = False


class Bullet(pg.sprite.Sprite):
    def __init__(self, asteroid: Asteroid, ship_pos: tuple):
        super(Bullet, self).__init__(bullets)
        self.target = asteroid
        self.pos = [ship_pos[0] + 64, ship_pos[1] + 20]
        self.image = load_image('bullet.png')
        self.rect = self.image.get_rect()
        self.dvizh = (0, 0)
        self.is_flip = False

    def update(self):
        if self.target.live:
            dx = self.pos[0] - self.target.rect_original.x
            dy = self.pos[1] - self.target.rect_original.y
            dist = sqrt(dx * dx + dy * dy)
            if dist:
                dx /= dist
                dy /= dist
            move_dist = min(-1, dist)

            self.pos[0] += round(move_dist * dx * 10)
            self.pos[1] += round(move_dist * dy * 10)
            self.rect.x, self.rect.y = self.pos
            self.dvizh = round(move_dist * dx * 10), round(move_dist * dy * 10)
        else:
            if self.is_focus():
                if self.dvizh == (0, 0):
                    self.die()
                self.pos[0] += self.dvizh[0]
                self.pos[1] += self.dvizh[1]
                self.rect.x, self.rect.y = self.pos
            else:
                self.die()
        if self.target.rect_original.x < self.rect.x and self.is_flip is False:
            self.image = pg.transform.flip(self.image, True, False)
            self.is_flip = True

    def die(self):
        self.kill()

    def is_focus(self):
        if -30 < self.pos[0] < WIDTH + 30 and -30 < self.pos[1] < HEIGHT + 30:
            return True
        return False


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
    sound_click.play()
    MANAGER.save()
    quit()


def menu() -> None:
    global x_bkgd, rel_x_bkgd, is_soundtrack_playing
    is_menu = True
    cursor.image = load_image("cursor_menu.png")
    h = (HEIGHT + 250) // 5
    but_start = Button(WIDTH // 2 - 125, h, 'start_but_0.png', 'start_but_1.png', start_game)
    but_settings = Button(WIDTH // 2 - 125, h + 70, 'settings_but_0.png', 'settings_but_1.png', show_settings)
    but_progress = Button(WIDTH // 2 - 125, h + 140, 'progress_but_0.png', 'progress_but_1.png', show_progress)
    but_titles = Button(WIDTH // 2 - 125, h + 210, 'titles_but_0.png', 'titles_but_1.png', show_titles)
    but_exit = Button(WIDTH // 2 - 125, h + 280, 'exit_but_0.png', 'exit_but_1.png', exit_app)
    sound_click.play()
    if is_soundtrack_playing is False:
        pg.mixer.music.play(-1)
        is_soundtrack_playing = True
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
        x_bkgd -= 0.3
        # отрисовка фона

        but_start.draw()
        but_settings.draw()
        but_progress.draw()
        but_titles.draw()
        but_exit.draw()

        all_sprites.draw(screen)
        pg.display.flip()
        clock.tick(100)


def continue_game():
    sound_click.play()
    global is_pause
    is_pause = False
    cursor.image = load_image("cursor.png")
    pg.time.set_timer(TIME_COUNT_EVENT, 1000)


def pause() -> None:
    global x_bkgd, rel_x_bkgd, is_pause
    is_pause = True
    cursor.image = load_image("cursor_menu.png")
    pause_img = load_image('pause_screen.png')

    but_menu = Button(WIDTH // 2 - 300, HEIGHT - 300, "menu_but_0.png", "menu_but_1.png", menu)
    but_continue = Button(WIDTH // 2 + 50, HEIGHT - 300, "continue_but_0.png", "continue_but_1.png", continue_game)

    high_score = MANAGER.data['max_score']
    pg.time.set_timer(TIME_COUNT_EVENT, 0)

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

        asteroids.draw(screen)
        player.draw(screen)
        bullets.draw(screen)

        screen.blit(pause_img, ((WIDTH - 800) // 2, (HEIGHT - 700) // 2))

        but_menu.draw()
        but_continue.draw()

        if int(SCORE) > high_score:
            high_score = int(SCORE)

        print_text(f'{int(SCORE)}', (WIDTH - 800) // 2 + 460, (HEIGHT - 700) // 2 + 165, font_size=80, font=FONTS[5])
        print_text(f'{high_score}', (WIDTH - 800) // 2 + 460, (HEIGHT - 700) // 2 + 270, font_size=70, font=FONTS[5])

        all_sprites.draw(screen)

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
    PLAYER.boom_count = 5
    PLAYER.live = True

    asteroids.empty()
    bullets.empty()
    cursor.image = load_image("cursor.png")

    PLAYER.ammunition = 5
    SCORE = 0
    ALL_TIME = dt.timedelta()
    diff = int(MANAGER.data['difficult'])
    score_pluser = float(f'0.0{diff}')
    pg.time.set_timer(SPAWN_ASTEROIDS_EVENT, 900 // diff + 100 * diff)
    pg.time.set_timer(TIME_COUNT_EVENT, 1000)

    running = True

    sound_click.play()

    while running:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            if event.type == SPAWN_ASTEROIDS_EVENT:
                for _ in range(diff):
                    Asteroid()
            if event.type == TIME_COUNT_EVENT:
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

        for i in bullets:
            i.update()

        asteroids.draw(screen)
        player.draw(screen)
        all_sprites.draw(screen)
        bullets.draw(screen)

        SCORE += score_pluser
        print_text(f"SCORE: {int(SCORE)}", WIDTH - 300, 10, font=FONTS[1])
        print_text(f"AMMUNITION: {PLAYER.ammunition}", WIDTH - 700, 10, font=FONTS[1])

        pg.display.flip()
        clock.tick(fps)


def show_titles() -> None:  # game designer, producer, artist, programmer, developer
    global x_bkgd, rel_x_bkgd
    is_titles = True

    but_back = Button(WIDTH - 300, HEIGHT - 100, "back_but_0.png", "back_but_1.png", menu)

    sound_click.play()

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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    menu()

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0.3
        # отрисовка фона

        print_text("GAME STUDIO - RepeekGames", 200, 100, font_size=50, font=FONTS[1])
        print_text("GAME DESIGNER - Mineev Kirill", 200, 250, font_size=50, font=FONTS[1])
        print_text("PRODUCER - Mineev Kirill", 200, 350, font_size=50, font=FONTS[1])
        print_text("PAINTER - Mineev Kirill", 200, 450, font_size=50, font=FONTS[1])
        print_text("PROGRAMMER - Mineev Kirill", 200, 550, font_size=50, font=FONTS[1])
        print_text("DEVELOPER - Mineev Kirill", 200, 650, font_size=50, font=FONTS[1])

        but_back.draw()

        all_sprites.draw(screen)

        pg.display.flip()
        clock.tick(fps)


def show_settings() -> None:
    global x_bkgd, rel_x_bkgd
    is_settings = True
    but_offset = (WIDTH - 950 - 630) // 2
    but_back = Button(WIDTH - 300, HEIGHT - 100, "back_but_0.png", "back_but_1.png", menu)
    but_easy = Button(800, HEIGHT // 6 * 3, "easy_but_0.png", "easy_but_1.png", lambda: set_difficult(1))
    but_medium = Button(1010 + but_offset, HEIGHT // 6 * 3, "medium_but_0.png", "medium_but_1.png",
                        lambda: set_difficult(2))
    but_hard = Button(1220 + but_offset + but_offset, HEIGHT // 6 * 3, "hard_but_0.png", "hard_but_1.png",
                      lambda: set_difficult(3))
    but_1920x1080 = Button(1050 + WIDTH - 950 - 500, HEIGHT // 6 + 530, "1920x1080_but_0.png", "1920x1080_but_1.png",
                           lambda: change_screen_size(1920, 1080))
    but_1600x900 = Button(800, HEIGHT // 6 + 530, "1600x900_but_0.png", "1600x900_but_1.png",
                          lambda: change_screen_size(1600, 900))

    sound_click.play()

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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    menu()
            if event.type == pg.MOUSEBUTTONDOWN:
                music_minus = pg.rect.Rect(780, HEIGHT//6 - 90, 100, 100)
                music_plus = pg.rect.Rect(WIDTH - 160, HEIGHT//6 - 90, 100, 100)
                sound_minus = pg.rect.Rect(780, HEIGHT//6 + 110, 100, 100)
                sound_plus = pg.rect.Rect(WIDTH - 160, HEIGHT//6 + 110, 100, 100)
                if music_minus.collidepoint(event.pos):
                    MANAGER.data['volume_music'] -= 0.1 if MANAGER.data['volume_music'] > 0 else 0
                    pg.mixer.music.set_volume(float(MANAGER.data['volume_music']))
                elif music_plus.collidepoint(event.pos):
                    MANAGER.data['volume_music'] += 0.1 if MANAGER.data['volume_music'] < 1 else 0
                    pg.mixer.music.set_volume(float(MANAGER.data['volume_music']))
                elif sound_minus.collidepoint(event.pos):
                    MANAGER.data['volume_sound'] -= 0.1 if MANAGER.data['volume_sound'] > 0 else 0
                    sound_intro.set_volume(float(MANAGER.data['volume_sound']))
                    sound_click.set_volume(float(MANAGER.data['volume_sound']))
                    sound_click_2.set_volume(float(MANAGER.data['volume_sound']))
                    sound_boom_asteroid.set_volume(float(MANAGER.data['volume_sound']))
                    sound_boom_ship.set_volume(float(MANAGER.data['volume_sound']))
                    sound_shoot.set_volume(float(MANAGER.data['volume_sound']))
                elif sound_plus.collidepoint(event.pos):
                    MANAGER.data['volume_sound'] += 0.1 if MANAGER.data['volume_sound'] < 1 else 0
                    sound_intro.set_volume(float(MANAGER.data['volume_sound']))
                    sound_click.set_volume(float(MANAGER.data['volume_sound']))
                    sound_click_2.set_volume(float(MANAGER.data['volume_sound']))
                    sound_boom_asteroid.set_volume(float(MANAGER.data['volume_sound']))
                    sound_boom_ship.set_volume(float(MANAGER.data['volume_sound']))
                    sound_shoot.set_volume(float(MANAGER.data['volume_sound']))


        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0.3
        # отрисовка фона

        but_back.draw()

        volume_music = float(MANAGER.data['volume_music'])
        volume_sound = float(MANAGER.data['volume_sound'])
        but_back.x, but_back.y = WIDTH - 300, HEIGHT - 100
        but_offset = (WIDTH - 950 - 630) // 2
        but_easy.x, but_easy.y = 800, HEIGHT // 6 * 3
        but_medium.x, but_medium.y = 1010 + but_offset, HEIGHT // 6 * 3
        but_hard.x, but_hard.y = 1220 + but_offset + but_offset, HEIGHT // 6 * 3
        but_1920x1080.x, but_1920x1080.y = 1050 + WIDTH - 950 - 500, HEIGHT // 6 + 530
        but_1600x900.x, but_1600x900.y = 800, HEIGHT // 6 + 530

        print_text("MUSIC", 100, HEIGHT // 6 - 70, font_size=100, font=FONTS[5])
        print_text('+', WIDTH - 150, HEIGHT // 6 - 125, font_size=150, font_color='green')
        print_text('-', 800, HEIGHT // 6 - 125, font_size=150, font_color='red')
        x, y, w, h = 900, HEIGHT // 6, (WIDTH - 1000) // 10 - 20, 10
        for i in range(round(volume_music * 10)):
            pg.draw.rect(screen, 'green', (x, y, w, h))
            x += w + 10
            h += 10
            y -= 10

        print_text("SOUNDS", 100, HEIGHT // 6 + 130, font_size=100, font=FONTS[5])
        print_text('+', WIDTH - 150, HEIGHT // 6 + 75, font_size=150, font_color='green')
        print_text('-', 800, HEIGHT // 6 + 75, font_size=150, font_color='red')
        x, y, w, h = 900, HEIGHT // 6 + 200, (WIDTH - 1000) // 10 - 20, 10
        for i in range(round(volume_sound * 10)):
            pg.draw.rect(screen, 'green', (x, y, w, h))
            x += w + 10
            h += 10
            y -= 10

        print_text("DIFFICULT", 100, HEIGHT // 6 + 330, font_size=100, font=FONTS[5])
        d = MANAGER.data['difficult']
        if d == 1:
            pg.draw.line(screen, 'yellow', (795, HEIGHT // 6 * 3), (795, HEIGHT // 6 * 3 + 60))
            pg.draw.line(screen, 'yellow', (1015, HEIGHT // 6 * 3), (1015, HEIGHT // 6 * 3 + 60))
        elif d == 2:
            pg.draw.line(screen, 'yellow', (1005 + but_offset, HEIGHT // 6 * 3),
                         (1005 + but_offset, HEIGHT // 6 * 3 + 60))
            pg.draw.line(screen, 'yellow', (1225 + but_offset, HEIGHT // 6 * 3),
                         (1225 + but_offset, HEIGHT // 6 * 3 + 60))
        else:
            pg.draw.line(screen, 'yellow', (1215 + but_offset + but_offset, HEIGHT // 6 * 3),
                         (1215 + but_offset + but_offset, HEIGHT // 6 * 3 + 60))
            pg.draw.line(screen, 'yellow', (1435 + but_offset + but_offset, HEIGHT // 6 * 3),
                         (1435 + but_offset + but_offset, HEIGHT // 6 * 3 + 60))

        d = MANAGER.data['full_screen']
        if d == 1:
            pg.draw.line(screen, 'yellow', (WIDTH - 405, HEIGHT // 6 + 530), (WIDTH - 405, HEIGHT // 6 + 580))
            pg.draw.line(screen, 'yellow', (WIDTH - 145, HEIGHT // 6 + 530), (WIDTH - 145, HEIGHT // 6 + 580))
        else:
            pg.draw.line(screen, 'yellow', (795, HEIGHT // 6 + 530), (795, HEIGHT // 6 + 580))
            pg.draw.line(screen, 'yellow', (1055, HEIGHT // 6 + 530), (1055, HEIGHT // 6 + 580))

        but_easy.draw()
        but_medium.draw()
        but_hard.draw()

        print_text("SCREEN SIZE", 100, HEIGHT // 6 + 530, font_size=100, font=FONTS[5])
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

    sound_click.play()

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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    menu()

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0.3
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
            f"{dt.datetime(2022, 1, 1, hour=t // 3600, minute=(t - t // 3600 * 3600) // 60, second=t - (t // 3600 * 3600) - (t - t // 3600 * 3600) // 60 * 60).strftime('%H:%M:%S')}",
            650, 700, font_size=140)
        screen.blit(clock_img, (11, 710))

        but_back.draw()

        all_sprites.draw(screen)

        pg.display.flip()
        clock.tick(fps)


def change_screen_size(w: int, h: int) -> None:
    global WIDTH, HEIGHT, screen
    sound_click_2.play()
    if WIDTH != w:
        WIDTH, HEIGHT = w, h
        if w == 1920:
            MANAGER.data['full_screen'] = 1
            screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        else:
            MANAGER.data['full_screen'] = 0
            screen = pg.display.set_mode((WIDTH, HEIGHT))


def set_difficult(n: int) -> None:
    sound_click_2.play()
    MANAGER.data['difficult'] = n


def preview() -> None:
    is_preview = True
    company = load_image('company_name.png')
    plads = load_image('game_name.png')
    alpha1 = 0
    alpha2 = 0
    m = False
    sound_intro.play()
    while is_preview:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == TIME_COUNT_EVENT:
                if m:
                    alpha2 -= 0.04
                    alpha1 -= 0.04
                    if alpha2 < -1:
                        is_preview = False
                else:
                    alpha1 += 0.07
                    if alpha1 > 1:
                        alpha2 += 0.07
                    if alpha2 > 1.5:
                        alpha2, alpha1, m = 1, 1, True
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)

        screen.fill('#101010')

        plads.set_alpha(255 * alpha2)
        company.set_alpha(255 * alpha1)
        screen.blit(plads, (WIDTH // 3, HEIGHT // 2))
        screen.blit(company, (WIDTH // 3, HEIGHT // 3))

        pg.display.flip()
        clock.tick(fps)
    pg.time.set_timer(TIME_COUNT_EVENT, 0)
    menu()


if __name__ == "__main__":
    environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (100, 100)  # это чтобы окно появлялось на экране в определенных корд.
    pg.mixer.pre_init(44100, -16, 1, 512)
    pg.init()
    MANAGER = DataManager()
    size = WIDTH, HEIGHT = (1920, 1080) if MANAGER.data['full_screen'] else (1600, 900)
    screen = pg.display.set_mode(size, pg.FULLSCREEN) if WIDTH == 1920 else pg.display.set_mode(size)
    fps = 100
    clock = pg.time.Clock()
    pg.display.set_caption("plads")

    background = pg.image.load("data/space.png").convert()
    x_bkgd = 0

    all_sprites = pg.sprite.Group()
    asteroids = pg.sprite.Group()
    player = pg.sprite.Group()
    bullets = pg.sprite.Group()

    cursor = pg.sprite.Sprite(all_sprites)
    cursor.image = load_image("cursor.png")
    cursor.rect = cursor.image.get_rect()

    SPAWN_ASTEROIDS_EVENT = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_ASTEROIDS_EVENT, 1000)

    TIME_COUNT_EVENT = pg.USEREVENT + 1
    pg.time.set_timer(TIME_COUNT_EVENT, 100)

    PLAYER = Ship()

    SCORE = 0
    ALL_TIME = dt.timedelta()
    one_second = dt.timedelta(seconds=1)

    is_pause = False

    FONTS = ['data/Comfortaa.ttf', 'data/Changa.ttf', 'data/Nunito.ttf', 'data/Orbitron.ttf', 'data/Signika.ttf',
             'data/StickNoBills.ttf']

    BULLET_ASTEROID = []

    pg.mixer.music.load('sounds/soundtrack.mp3')
    pg.mixer.music.set_volume(MANAGER.data['volume_music'])
    is_soundtrack_playing = False

    sound_intro = pg.mixer.Sound("sounds/intro.wav")
    sound_click = pg.mixer.Sound("sounds/click.wav")
    sound_click_2 = pg.mixer.Sound("sounds/change.wav")
    sound_boom_asteroid = pg.mixer.Sound("sounds/boom.wav")
    sound_boom_ship = pg.mixer.Sound("sounds/boom2.wav")
    sound_shoot = pg.mixer.Sound("sounds/shoot.wav")

    sound_intro.set_volume(float(MANAGER.data['volume_sound']))
    sound_click.set_volume(float(MANAGER.data['volume_sound']))
    sound_click_2.set_volume(float(MANAGER.data['volume_sound']))
    sound_boom_asteroid.set_volume(float(MANAGER.data['volume_sound']))
    sound_boom_ship.set_volume(float(MANAGER.data['volume_sound']))
    sound_shoot.set_volume(float(MANAGER.data['volume_sound']))

    preview()
