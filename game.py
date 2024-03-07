import pygame
import random

pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
ORANGE = (255, 165, 0)

clock = pygame.time.Clock()
FPS = 60


class LKW(pygame.sprite.Sprite):
    def __init__(self):
        super(LKW, self).__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 50))
        self.velocity = 5
        self.ertz = 0
        self.sprit = 100
        self.max_ertz = 50
        self.gesamt_abgebautes_ertz = 0

    def update(self, erzquelle, ablageplatz, tankstelle, hubschrauber_group):
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.velocity
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.velocity
            moving = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.velocity
            moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.velocity
            moving = True
        if moving:
            self.sprit -= 0.1
        if self.sprit <= 0:
            self.kill()

        self.check_collisions(erzquelle, ablageplatz, tankstelle, hubschrauber_group)

    def check_collisions(self, erzquelle, ablageplatz, tankstelle, hubschrauber_group):
        if pygame.sprite.spritecollide(self, hubschrauber_group, dokill=False):
            self.ertz = 0

        if pygame.sprite.collide_rect(self, erzquelle):
            if erzquelle.ertz_menge > 0:
                abzubauendes_ertz = min(50, erzquelle.ertz_menge, self.max_ertz - self.ertz)
                self.ertz += abzubauendes_ertz
                erzquelle.ertz_menge -= abzubauendes_ertz
                if self.ertz >= 50 or erzquelle.ertz_menge == 0:
                    erzquelle.neu_positionieren()
                    if erzquelle.ertz_menge == 0:
                        erzquelle.ertz_menge = 1000

        if pygame.sprite.collide_rect(self, ablageplatz):
            ablageplatz.ertz += self.ertz
            self.gesamt_abgebautes_ertz += self.ertz
            self.ertz = 0

        if pygame.sprite.collide_rect(self, tankstelle):
            self.sprit = 100


class Hubschrauber(pygame.sprite.Sprite):
    def __init__(self):
        super(Hubschrauber, self).__init__()
        self.image = pygame.Surface((40, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.choice([0, screen_width]), random.randint(0, screen_height)))
        self.velocity = random.choice([random.randint(4, 7), -random.randint(4, 7)])

    def update(self):
        self.rect.x += self.velocity
        if self.rect.right < 0:
            self.rect.left = screen_width
        elif self.rect.left > screen_width:
            self.rect.right = 0


class Erzquelle(pygame.sprite.Sprite):
    def __init__(self):
        super(Erzquelle, self).__init__()
        self.rect = None
        self.image = pygame.Surface((100, 50))
        self.image.fill(PURPLE)
        self.ertz_menge = 1000
        self.neu_positionieren()

    def neu_positionieren(self):
        self.rect = self.image.get_rect(
            center=(random.randint(100, screen_width - 100), random.randint(50, screen_height - 50)))


class Abladeplatz(pygame.sprite.Sprite):
    def __init__(self):
        super(Abladeplatz, self).__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(screen_width - 100, screen_height // 2))
        self.ertz = 0
        self.kapazität = 1000


class Tankstelle(pygame.sprite.Sprite):
    def __init__(self):
        super(Tankstelle, self).__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(
            center=(random.randint(100, screen_width - 100), random.randint(100, screen_height - 100)))


def create_hubschrauber(group):
    for _ in range(6):
        hubschrauber = Hubschrauber()
        group.add(hubschrauber)


def main():
    running = True
    spiel_gewonnen = False
    lkw = LKW()
    erzquelle = Erzquelle()
    ablageplatz = Abladeplatz()
    tankstelle = Tankstelle()

    alle_sprites = pygame.sprite.Group()
    hubschrauber_group = pygame.sprite.Group()
    alle_sprites.add(lkw, erzquelle, ablageplatz, tankstelle)
    create_hubschrauber(hubschrauber_group)
    alle_sprites.add(hubschrauber_group)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        lkw.update(erzquelle, ablageplatz, tankstelle, hubschrauber_group)
        hubschrauber_group.update()
        erzquelle.update()
        tankstelle.update()

        screen.fill(WHITE)
        alle_sprites.draw(screen)

        font = pygame.font.SysFont(None, 24)
        infos = [
            f'Sprit: {int(lkw.sprit)}',
            f'Erz im LKW: {lkw.ertz}',
            f'Gesamt abgebautes Erz: {lkw.gesamt_abgebautes_ertz}',
            f'Erz am Abladeplatz: {ablageplatz.ertz}/{ablageplatz.kapazität}'
        ]
        for index, text in enumerate(infos):
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (10, 10 + index * 20))

        pygame.display.flip()
        clock.tick(FPS)

        if ablageplatz.ertz >= ablageplatz.kapazität:
            spiel_gewonnen = True
            running = False

    if spiel_gewonnen:
        print("Spiel gewonnen! Du hast erfolgreich 800 Erz transportiert.")
    else:
        print("Spiel beendet.")

    pygame.quit()


if __name__ == '__main__':
    main()
