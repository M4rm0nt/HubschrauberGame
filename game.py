import pygame
import random

# Initialisierung von Pygame
pygame.init()

# Bildschirmeinstellungen
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Farbdefinitionen
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)

# Spieluhr und FPS
clock = pygame.time.Clock()
FPS = 60

# Sprite-Klassen
class LKW(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 50))
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
            self.rect.x -= self.geschwindigkeit
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.geschwindigkeit
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.geschwindigkeit
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.geschwindigkeit

    def consume_fuel(self):
        if any(pygame.key.get_pressed()):
            self.sprit -= 0.1
            if self.sprit <= 0:
                self.kill()

    def check_collisions(self, erzquelle, ablageplatz, tankstelle, hubschrauber_group):
        if pygame.sprite.spritecollide(self, hubschrauber_group, dokill=False):
            self.erz = 0
        if pygame.sprite.collide_rect(self, erzquelle):
            self.collect_erz(erzquelle)
        if pygame.sprite.collide_rect(self, ablageplatz):
            ablageplatz.erz += self.erz
            self.erz = 0
        if pygame.sprite.collide_rect(self, tankstelle):
            self.sprit = 100

    def collect_erz(self, erzquelle):
        if erzquelle.erz_menge > 0:
            abzubauendes_erz = min(50, erzquelle.erz_menge, self.max_erz - self.erz)
            self.erz += abzubauendes_erz
            erzquelle.erz_menge -= abzubauendes_erz
            if self.erz >= self.max_erz or erzquelle.erz_menge == 0:
                erzquelle.neu_positionieren()


class Hubschrauber(pygame.sprite.Sprite):
    def __init__(self, lkw):
        super().__init__()
        self.image = pygame.Surface((40, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.choice([0, screen_width]), random.randint(0, screen_height)))
        self.geschwindigkeit = 3
        self.lkw = lkw

    def update(self, *args, **kwargs):
        if self.lkw.rect.x < self.rect.x:
            self.rect.x -= self.geschwindigkeit
        else:
            self.rect.x += self.geschwindigkeit
        if self.lkw.rect.y < self.rect.y:
            self.rect.y -= self.geschwindigkeit
        else:
            self.rect.y += self.geschwindigkeit


class Erzquelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 50))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=(random.randint(100, screen_width - 100), random.randint(50, screen_height - 50)))
        self.erz_menge = 1000

    def neu_positionieren(self):
        self.rect = self.image.get_rect(center=(random.randint(100, screen_width - 100), random.randint(50, screen_height - 50)))


class Abladeplatz(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(screen_width - 100, screen_height // 2))
        self.erz = 0
        self.kapazität = 1000


class Tankstelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(random.randint(100, screen_width - 100), random.randint(50, screen_height - 50)))

# Spiellogik
def main():
    running = True
    spiel_gewonnen = False

    lkw = LKW()
    erzquelle = Erzquelle()
    ablageplatz = Abladeplatz()
    tankstelle = Tankstelle()
    hubschrauber = Hubschrauber(lkw)

    alle_sprites = pygame.sprite.Group()
    hubschrauber_group = pygame.sprite.Group()
    alle_sprites.add(lkw, erzquelle, ablageplatz, tankstelle, hubschrauber)
    hubschrauber_group.add(hubschrauber)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        alle_sprites.update(erzquelle, ablageplatz, tankstelle, hubschrauber_group)

        screen.fill(WHITE)
        alle_sprites.draw(screen)

        infos = [
            f'Sprit: {int(lkw.sprit)}',
            f'Erz im LKW: {lkw.erz}',
            f'Erz am Abladeplatz: {ablageplatz.erz}/{ablageplatz.kapazität}'
        ]
        font = pygame.font.SysFont(None, 24)
        for index, info in enumerate(infos):
            text_surface = font.render(info, True, BLACK)
            screen.blit(text_surface, (10, 10 + index * 20))

        pygame.display.flip()
        clock.tick(FPS)

        if ablageplatz.erz >= ablageplatz.kapazität:
            spiel_gewonnen = True
            running = False

    end_game(spiel_gewonnen)


def end_game(gewonnen):
    print("Spiel gewonnen!" if gewonnen else "Spiel beendet.")


if __name__ == '__main__':
    main()
