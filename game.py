import pygame
import random
import os
from enum import Enum

pygame.init()

# Definiere Konstanten
BILDSCHIRM_BREITE, BILDSCHIRM_HOEHE = 800, 600
WEISS = (255, 255, 255)
SCHWARZ = (0, 0, 0)
ROT = (255, 0, 0)
FPS = 60

# Schriften
SCHRIFT_KLEIN = pygame.font.SysFont("arial", 25)
SCHRIFT_GROSS = pygame.font.SysFont("arial", 36)

# Verzeichnis für Bilder
BILDER_VERZEICHNIS = "bilder"


# Aufzählung für Tasten
class Tasten(Enum):
    LINKS = pygame.K_LEFT
    RECHTS = pygame.K_RIGHT
    OBEN = pygame.K_UP
    UNTEN = pygame.K_DOWN
    A = pygame.K_a
    D = pygame.K_d
    W = pygame.K_w
    S = pygame.K_s
    PAUSE = pygame.K_p


# Laden von Bildern
def bild_laden(name):
    pfad = os.path.join(BILDER_VERZEICHNIS, f'{name}.png')
    return pygame.image.load(pfad)


# Startbildschirm
def start_bildschirm():
    start = True
    while start:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                quit()
            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == pygame.K_SPACE:
                    start = False

        BILDSCHIRM.fill(WEISS)
        titel_text = SCHRIFT_KLEIN.render("ErzCollector", True, SCHWARZ)
        BILDSCHIRM.blit(titel_text, (100, 200))
        info_text = SCHRIFT_KLEIN.render("Sammle Erz, meide Hubschrauber.", True, SCHWARZ)
        BILDSCHIRM.blit(info_text, (100, 300))
        info_text = SCHRIFT_KLEIN.render("Starte mit Leertaste.", True, SCHWARZ)
        BILDSCHIRM.blit(info_text, (100, 400))
        info_text = SCHRIFT_KLEIN.render("Für die Optionen zu sehen, drücke 'P' im Spiel.", True, SCHWARZ)
        BILDSCHIRM.blit(info_text, (100, 500))
        pygame.display.flip()
        UHR.tick(15)


# Pause-Funktion
def pause():
    pausiert = True
    while pausiert:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                quit()
            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == pygame.K_c:
                    pausiert = False
                elif ereignis.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif ereignis.key == pygame.K_p:
                    pausiert = False

        BILDSCHIRM.fill(WEISS)
        pause_text = SCHRIFT_GROSS.render("Pause", True, SCHWARZ)
        BILDSCHIRM.blit(pause_text, (BILDSCHIRM_BREITE // 2 - pause_text.get_width() // 2, 100))

        # Steuerung anzeigen
        steuerung = [
            "Steuerung",
            "Pfeiltasten oder WASD"
        ]
        for index, element in enumerate(steuerung):
            zeige_infos([element], 200 + index * 30)

        # Ziele anzeigen
        ziele_start_y = 300
        ziele = [
            "Spielziele",
            "- Sammle Erz von der Erzquelle",
            "- Bringe das Erz zum Abladeplatz",
            "- Vermeide Kollisionen mit Hubschraubern",
            "- Du verlierst wenn der Hubschrauber 20% des Erzes besitzt",
            "- Halte den Kraftstoffvorrat im Auge"
        ]
        for index, ziel in enumerate(ziele):
            zeige_infos([ziel], ziele_start_y + index * 30)

        # Optionen anzeigen
        options_start_y = 500
        options = [
            "- Drücke 2 mal 'P' zum weiterspielen oder 'Q' zum beenden"
        ]
        zeige_infos(options, options_start_y)

        pygame.display.flip()
        UHR.tick(5)



# Funktion zum Zeichnen von Informationen
def zeige_infos(info_liste, y_start, separate_info=None):
    x_offset = BILDSCHIRM_BREITE // 2 - sum(
        [SCHRIFT_KLEIN.render(info, True, SCHWARZ).get_width() for info in info_liste]) // 2
    for info in info_liste:
        text_surface = SCHRIFT_KLEIN.render(info, True, SCHWARZ)
        BILDSCHIRM.blit(text_surface, (x_offset, y_start))
        x_offset += text_surface.get_width() + 20

    if separate_info is not None:
        separate_text_surface = SCHRIFT_KLEIN.render(separate_info, True, SCHWARZ)
        separate_text_rect = separate_text_surface.get_rect(midbottom=(BILDSCHIRM_BREITE // 2, BILDSCHIRM_HOEHE - 10))
        BILDSCHIRM.blit(separate_text_surface, separate_text_rect)


# LKW-Klasse
class LKW(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bild_laden('lastwagen')
        self.rect = self.image.get_rect(center=(BILDSCHIRM_BREITE // 2, BILDSCHIRM_HOEHE - 50))
        self.hitbox = pygame.Rect(self.rect.left + 10, self.rect.top + 10, self.rect.width - 20, self.rect.height - 20)
        self.geschwindigkeit = 5
        self.kraftstoff = 100
        self.erz = 0
        self.max_erz = 50
        self.gestohlenes_erz = 0

    def update(self, tasten, erz_quelle, lager, tankstelle, hubschrauber_gruppe):
        self.bewegen(tasten)
        self.kraftstoff_verbrauchen(tasten)
        self.kollision_pruefen(erz_quelle, lager, tankstelle, hubschrauber_gruppe)

    def bewegen(self, tasten):
        if tasten[Tasten.LINKS.value] or tasten[Tasten.A.value]:
            self.rect.x = max(0, self.rect.x - self.geschwindigkeit)
        if tasten[Tasten.RECHTS.value] or tasten[Tasten.D.value]:
            self.rect.x = min(BILDSCHIRM_BREITE - self.rect.width, self.rect.x + self.geschwindigkeit)
        if tasten[Tasten.OBEN.value] or tasten[Tasten.W.value]:
            self.rect.y = max(0, self.rect.y - self.geschwindigkeit)
        if tasten[Tasten.UNTEN.value] or tasten[Tasten.S.value]:
            self.rect.y = min(BILDSCHIRM_HOEHE - self.rect.height, self.rect.y + self.geschwindigkeit)
        self.hitbox.center = self.rect.center

    def kraftstoff_verbrauchen(self, tasten):
        if tasten[Tasten.LINKS.value] or tasten[Tasten.RECHTS.value] or tasten[Tasten.OBEN.value] or tasten[
            Tasten.UNTEN.value] or tasten[Tasten.W.value] or tasten[Tasten.A.value] or tasten[Tasten.S.value] or tasten[
            Tasten.D.value]:
            self.kraftstoff -= 0.15
            if self.kraftstoff <= 0:
                self.kill()

    def kollision_pruefen(self, erz_quelle, lager, tankstelle, hubschrauber_gruppe):
        kollidierter_hubschrauber = pygame.sprite.spritecollideany(self, hubschrauber_gruppe,
                                                                   collided=lambda s1, s2: s1.hitbox.colliderect(
                                                                       s2.rect))
        if kollidierter_hubschrauber and self.erz > 0:
            self.gestohlenes_erz += self.erz  # Erz stehlen
            self.erz = 0
            kollidierter_hubschrauber.reset_required = True
        if self.hitbox.colliderect(erz_quelle.rect):
            self.erz_sammeln(erz_quelle)
        if self.hitbox.colliderect(lager.rect):
            lager.erz += self.erz
            self.erz = 0
        if self.hitbox.colliderect(tankstelle.rect):
            self.kraftstoff = 100

    def erz_sammeln(self, erz_quelle):
        if self.erz < self.max_erz:
            if erz_quelle.erz_menge > 0:
                zu_bergendes_erz = min(self.max_erz - self.erz, erz_quelle.erz_menge)
                self.erz += zu_bergendes_erz
                erz_quelle.erz_menge -= zu_bergendes_erz
                if self.erz == zu_bergendes_erz:
                    erz_quelle.neupositionieren()


# Hubschrauberlandeplatz-Klasse
class Hubschrauberlandeplatz(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bild_laden('hubschrauberlandeplatz')
        self.rect = self.image.get_rect(
            center=(random.randint(50, BILDSCHIRM_BREITE - 150), random.randint(50, BILDSCHIRM_HOEHE - 50)))


# Hubschrauber-Klasse
class Hubschrauber(pygame.sprite.Sprite):
    def __init__(self, lkw, hubschrauberlandeplatz):
        super().__init__()
        self.image = bild_laden('hubschrauber')
        self.rect = self.image.get_rect(center=hubschrauberlandeplatz.rect.center)
        self.geschwindigkeit = 2.5
        self.lkw = lkw
        self.hubschrauberlandeplatz = hubschrauberlandeplatz
        self.reset_required = False

    def update(self):
        if self.reset_required:
            self.zuruecksetzen_zu_hubschrauberlandeplatz()
        else:
            self.lkw_verfolgen()

    def lkw_verfolgen(self):
        if self.lkw.rect.centerx < self.rect.centerx:
            self.rect.x -= self.geschwindigkeit
        elif self.lkw.rect.centerx > self.rect.centerx:
            self.rect.x += self.geschwindigkeit
        if self.lkw.rect.centery < self.rect.centery:
            self.rect.y -= self.geschwindigkeit
        elif self.lkw.rect.centery > self.rect.centery:
            self.rect.y += self.geschwindigkeit

    def zuruecksetzen_zu_hubschrauberlandeplatz(self):
        self.rect.center = self.hubschrauberlandeplatz.rect.center
        self.reset_required = False


# Erzquelle-Klasse
class Erzquelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bild_laden('erz')
        self.rect = self.image.get_rect(
            center=(random.randint(100, BILDSCHIRM_BREITE - 100), random.randint(50, BILDSCHIRM_HOEHE - 50)))
        self.erz_menge = 1000

    def neupositionieren(self):
        self.rect.center = (random.randint(100, BILDSCHIRM_BREITE - 100), random.randint(50, BILDSCHIRM_HOEHE - 50))


# Lager-Klasse
class Lager(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bild_laden('lager')
        self.rect = self.image.get_rect(center=(BILDSCHIRM_BREITE - 150, BILDSCHIRM_HOEHE // 2))
        self.erz = 0
        self.kapazitaet = 1000


# Tankstelle-Klasse
class Tankstelle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bild_laden('tankstelle')
        self.rect = self.image.get_rect(
            center=(random.randint(50, BILDSCHIRM_BREITE - 50), random.randint(50, BILDSCHIRM_HOEHE - 50)))


# Hauptfunktion
def main():
    global BILDSCHIRM
    laufend = True
    pausiert = False

    # Spielobjekte erstellen
    lkw = LKW()
    erz_quelle = Erzquelle()
    lager = Lager()
    tankstelle = Tankstelle()
    hubschrauberlandeplatz = Hubschrauberlandeplatz()
    hubschrauber = Hubschrauber(lkw, hubschrauberlandeplatz)

    # Sprite-Gruppen
    alle_sprites = pygame.sprite.Group()
    hubschrauber_gruppe = pygame.sprite.Group()
    alle_sprites.add(lkw, erz_quelle, lager, tankstelle, hubschrauberlandeplatz, hubschrauber)
    hubschrauber_gruppe.add(hubschrauber)

    while laufend:
        tasten = pygame.key.get_pressed()
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                laufend = False
            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == Tasten.PAUSE.value:
                    pausiert = not pausiert

        if not pausiert:
            lkw.update(tasten, erz_quelle, lager, tankstelle, hubschrauber_gruppe)
            hubschrauber_gruppe.update()

            BILDSCHIRM.fill(WEISS)
            alle_sprites.draw(BILDSCHIRM)

            info_liste = [
                f'Sprit: {int(lkw.kraftstoff)}',
                f'Erz im LKW: {lkw.erz}',
                f'Erz am Lager: {lager.erz}/{lager.kapazitaet}'
            ]
            zeige_infos(info_liste, 10, separate_info=f'Erz gestohlen: {lkw.gestohlenes_erz}')

        else:
            pause()

        pygame.display.flip()
        UHR.tick(FPS)

        if lkw.kraftstoff <= 0 or lager.erz >= lager.kapazitaet or lkw.gestohlenes_erz > 200:
            laufend = False
            endnachricht = "Spiel vorbei! Neu starten? (J/N)"
            text_surface = SCHRIFT_GROSS.render(endnachricht, True, ROT)
            text_rect = text_surface.get_rect(center=(BILDSCHIRM_BREITE / 2, BILDSCHIRM_HOEHE / 2))
            BILDSCHIRM.fill(WEISS)
            BILDSCHIRM.blit(text_surface, text_rect)
            pygame.display.flip()

            auf_eingabe_warten = True
            while auf_eingabe_warten:
                for ereignis in pygame.event.get():
                    if ereignis.type == pygame.KEYDOWN:
                        if ereignis.key == pygame.K_j:
                            main()
                            auf_eingabe_warten = False
                        elif ereignis.key == pygame.K_n:
                            pygame.quit()
                            return
                    elif ereignis.type == pygame.QUIT:
                        pygame.quit()
                        return

    pygame.quit()


if __name__ == '__main__':
    # Bildschirm einrichten
    BILDSCHIRM = pygame.display.set_mode((BILDSCHIRM_BREITE, BILDSCHIRM_HOEHE))
    pygame.display.set_caption("ErzCollector")
    UHR = pygame.time.Clock()

    # Spiel starten
    start_bildschirm()
    main()
