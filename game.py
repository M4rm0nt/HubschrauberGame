import pygame
import random
import os

pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("ErzCollector")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

clock = pygame.time.Clock()
FPS = 60


def load_image(name):
    path = os.path.expanduser(f'~/Dokumente/pics/{name}.png')
    return pygame.image.load(path)


class LKW(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('lastwagen')
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 50))
        self.hitbox = pygame.Rect(self.rect.left + 10, self.rect.top + 10, self.rect.width - 20, self.rect.height - 20)
        self.geschwindigkeit = 5
        self.sprit = 100
        self.erz = 0
        self.max_erz = 50

    def update(self, erzquelle, ablageplatz, tankstelle, hubschrauber_group):
        self.move()
        self.consume_fuel()
        self.check_collisions(erzquelle, ablageplatz, tankstelle, hubschrauber_group)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x = max(0, self.rect.x - self.geschwindigkeit)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x = min(screen_width - self.rect.width, self.rect.x + self.geschwindigkeit)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y = max(0, self.rect.y - self.geschwindigkeit)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y = min(screen_height - self.rect.height, self.rect.y + self.geschwindigkeit)
        self.hitbox.center = self.rect.center

    def consume_fuel(self):
        if any(pygame.key.get_pressed()):
            self.sprit -= 0.1
            if self.sprit <= 0:
                self.kill()

    def check_collisions(self, erzquelle, ablageplatz, tankstelle, hubschrauber_group):
        collided_hubschrauber = pygame.sprite.spritecollideany(self, hubschrauber_group, collided=lambda s1, s2: s1.hitbox.colliderect(s2.rect))
        if collided_hubschrauber and self.erz > 0:
            self.erz = 0
            collided_hubschrauber.zurücksetzen_erforderlich = True
        if self.hitbox.colliderect(erzquelle.rect):
            self.collect_erz(erzquelle)
        if self.hitbox.colliderect(ablageplatz.rect):
            ablageplatz.erz += self.erz
            self.erz = 0
        if self.hitbox.colliderect(tankstelle.rect):
            self.sprit = 100

    def collect_erz(self, erzquelle):
        if self.erz < self.max_erz:
            if erzquelle.erz_menge > 0:
                abzubauendes_erz = min(self.max_erz - self.erz, erzquelle.erz_menge)
                self.erz += abzubauendes_erz
                erzquelle.erz_menge -= abzubauendes_erz
                if self.erz == abzubauendes_erz:
                    erzquelle.neu_positionieren()


class Helipad(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('helipad')
        self.rect = self.image.get_rect(
            center=(random.randint(50, screen_width - 150), random.randint(50, screen_height - 50)))


class Hubschrauber(pygame.sprite.Sprite):
    def __init__(self, lkw, helipad):
        super().__init__()
        self.image = load_image('helicopter')
        self.rect = self.image.get_rect(center=helipad.rect.center)
        self.geschwindigkeit = 2.5
        self.lkw = lkw
        self.helipad = helipad
        self.zurücksetzen_erforderlich = False

    def update(self):
        if self.zurücksetzen_erforderlich:
            self.reset_to_helipad()
        else:
            self.follow_lkw()

    def follow_lkw(self):
        if self.lkw.rect.centerx < self.rect.centerx:
            self.rect.x -= self.geschwindigkeit
        elif self.lkw.rect.centerx > self.rect.centerx:
            self.rect.x += self.geschwindigkeit
        if self.lkw.rect.centery < self.rect.centery:
            self.rect.y -= self.geschwindigkeit
        elif self.lkw.rect.centery > self.rect.centery:
            self.rect.y += self.geschwindigkeit

    def reset_to_helipad(self):
        self.rect.center = self.helipad.rect.center
        self.zurücksetzen_erforderlich = False


class Erzquelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('erz')
        self.rect = self.image.get_rect(center=(random.randint(100, screen_width - 100), random.randint(50, screen_height - 50)))
        self.erz_menge = 1000

    def neu_positionieren(self):
        self.rect.center = (random.randint(100, screen_width - 100), random.randint(50, screen_height - 50))


class Abladeplatz(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('storage')
        self.rect = self.image.get_rect(center=(screen_width - 150, screen_height // 2))
        self.erz = 0
        self.kapazität = 1000


class Tankstelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('fuel')
        self.rect = self.image.get_rect(
            center=(random.randint(50, screen_width - 50), random.randint(50, screen_height - 50)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("ErzCollector")

    running = True

    lkw = LKW()
    erzquelle = Erzquelle()
    ablageplatz = Abladeplatz()
    tankstelle = Tankstelle()
    helipad = Helipad()
    hubschrauber = Hubschrauber(lkw, helipad)

    alle_sprites = pygame.sprite.Group()
    hubschrauber_group = pygame.sprite.Group()
    alle_sprites.add(lkw, erzquelle, ablageplatz, tankstelle, helipad, hubschrauber)
    hubschrauber_group.add(hubschrauber)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        lkw.update(erzquelle, ablageplatz, tankstelle, hubschrauber_group)
        hubschrauber_group.update()

        screen.fill(WHITE)
        alle_sprites.draw(screen)

        font = pygame.font.SysFont(None, 20)
        infos = [
            f'Sprit: {int(lkw.sprit)}',
            f'Erz im LKW: {lkw.erz}',
            f'Erz am Abladeplatz: {ablageplatz.erz}/{ablageplatz.kapazität}'
        ]

        text_width = screen_width / len(infos)
        for index, text in enumerate(infos):
            text_surface = font.render(text, True, BLACK)
            x_position = text_width * index + (text_width - text_surface.get_width()) / 2
            screen.blit(text_surface, (x_position, 10))

        pygame.display.flip()
        clock.tick(FPS)

        if lkw.sprit <= 0 or ablageplatz.erz >= 800:
            running = False
            font = pygame.font.SysFont("arial", 36)
            end_message = "Spiel vorbei! Neu starten? (Y/N)"
            text_surface = font.render(end_message, True, RED)
            text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.fill(WHITE)
            screen.blit(text_surface, text_rect)
            pygame.display.flip()

            wait_for_input = True
            while wait_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            main()
                            wait_for_input = False
                        elif event.key == pygame.K_n:
                            pygame.quit()
                            return
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        return

    pygame.quit()


if __name__ == '__main__':
    main()