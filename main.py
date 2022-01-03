import pygame as pg
import os
import sys
from random import random, choice, randrange


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

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.destroy()

        if self.rect.x < -100:
            self.kill()
        self.image, self.rect = rotate_image(self.image_original, self.angle)
        self.rect_original = self.rect_original.move(self.vx, self.vy)
        self.rect.center = self.rect_original.center
        self.angle += self.diff_angle

    def destroy(self):
        self.kill()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    return pg.image.load(fullname)


def rotate_image(surface: pg.surface, angle: int):
    rotated_surface = pg.transform.rotozoom(surface, angle, 1)
    rotated_rect = rotated_surface.get_rect(center=surface.get_rect().center)
    return rotated_surface, rotated_rect


def get_probability_asteroid() -> int: return choice([1, 2, 3, 4]) if 0 < random() < 0.96 else choice([5, 6, 7])


def menu():
    global x_bkgd, rel_x_bkgd
    is_menu = True
    cursor.image = load_image("cursor_menu.png")
    while is_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == SPAWN_ASTEROIDS:
                Asteroid()
            if pg.mouse.get_focused():
                pg.mouse.set_visible(False)
                cursor.rect.x, cursor.rect.y = pg.mouse.get_pos()
                cursor.image.set_alpha(255)
            else:
                cursor.image.set_alpha(0)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    is_menu = False
                    asteroids.empty()
                    cursor.image = load_image("cursor.png")
                if event.key == pg.K_ESCAPE:
                    quit()

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 0
        # отрисовка фона

        print_text("TO START PRESS ENTER", 750, 400)
        print_text("TO EXIT PRESS ESCAPE", 750, 500)

        all_sprites.draw(screen)
        pg.display.flip()
        clock.tick(fps)


def print_text(text, x, y, font_color=(255, 255, 255), font="data/Comfortaa.ttf", font_size=30):
    font = pg.font.Font(font, font_size)
    text = font.render(text, True, font_color)
    screen.blit(text, (x, y))


if __name__ == "__main__":
    pg.init()
    size = WIDTH, HEIGHT = 1920, 1080
    screen = pg.display.set_mode(size)
    fps = 100
    clock = pg.time.Clock()
    pg.display.set_caption("flappy")
    running = True

    background = pg.image.load("data/space.png").convert()
    x_bkgd = 0

    all_sprites = pg.sprite.Group()
    asteroids = pg.sprite.Group()

    cursor = pg.sprite.Sprite(all_sprites)
    cursor.image = load_image("cursor.png")
    cursor.rect = cursor.image.get_rect()

    SPAWN_ASTEROIDS = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_ASTEROIDS, 1000)

    ship = load_image("ship.png")

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
                    menu()

        screen.fill('black')

        # отрисовка фона
        rel_x_bkgd = x_bkgd % background.get_rect().width
        screen.blit(background, (rel_x_bkgd - background.get_rect().width, 0))
        if rel_x_bkgd < WIDTH:
            screen.blit(background, (rel_x_bkgd, 0))
        x_bkgd -= 1
        # отрисовка фона

        for i in asteroids:
            i.update()

        all_sprites.draw(screen)
        asteroids.draw(screen)

        screen.blit(ship, (100, 100))

        pg.display.flip()
        clock.tick(fps)
