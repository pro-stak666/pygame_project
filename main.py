import pygame as pg
from os import path
from random import random, choice, randrange


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

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
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

    def die(self):
        score_manipulation(save=True)
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


def menu() -> None:
    global x_bkgd, rel_x_bkgd
    is_menu = True
    cursor.image = load_image("cursor_menu.png")

    but_start = Button(200, 200, 'start_but_0.png', 'start_but_1.png', start_game)
    but_exit = Button(200, 270, 'exit_but_0.png', 'exit_but_1.png', lambda: quit())

    while is_menu:
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

        but_start.draw()
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
                    score_manipulation(save=True)
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
    global WIDTH, HEIGHT, screen, fps, clock, background, x_bkgd, all_sprites, asteroids, player, cursor, PLAYER, SCORE

    PLAYER.rect.x = 100
    PLAYER.rect.y = HEIGHT // 2 - PLAYER.rect.height // 2

    asteroids.empty()
    cursor.image = load_image("cursor.png")

    SCORE = 0

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == SPAWN_ASTEROIDS:
                Asteroid()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)
            if event.type == pg.MOUSEBUTTONDOWN:
                for i in asteroids:
                    i.update(event)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pause()

        PLAYER.update(pg.event.get())

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 1.15
        # отрисовка фона

        for i in asteroids:
            i.update()

        asteroids.draw(screen)
        player.draw(screen)
        all_sprites.draw(screen)

        SCORE += 0.01
        print_text(f"SCORE: {int(SCORE)}", 1550, 10)

        pg.display.flip()
        clock.tick(fps)


def score_manipulation(get: bool = None, save: bool = None):
    if not path.isfile("data/score.txt"):
        with open('data/score.txt', 'w') as f:
            f.write("max_score = 0")
    if get:
        with open("data/score.txt", 'r', encoding="utf-8") as f:
            data = f.read()
            print(data[12:])
    if save:
        with open("data/score.txt", 'r+', encoding="utf-8") as f:
            if int(f.read()[12:]) < SCORE:
                f.seek(0)
                f.truncate()
                f.write(str(f"max_score = {int(SCORE)}"))


if __name__ == "__main__":
    pg.init()
    size = WIDTH, HEIGHT = 1920, 1080
    screen = pg.display.set_mode(size)
    fps = 100
    clock = pg.time.Clock()
    pg.display.set_caption("mdaaa...")

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

    PLAYER = Ship()

    SCORE = 0

    menu()
