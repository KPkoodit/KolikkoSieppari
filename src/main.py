import pygame
import random
import math
import os

class Kolikkosade:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kolikkosade")

        self.naytto = pygame.display.set_mode((640, 480))
        self.fontti = pygame.font.SysFont("Arial", 24)

        self.robo = pygame.image.load(os.path.join(os.path.dirname(__file__), 'robo.png'))
        self.kolikko = pygame.image.load(os.path.join(os.path.dirname(__file__), 'kolikko.png'))
        self.morko = pygame.image.load(os.path.join(os.path.dirname(__file__), 'hirvio.png'))

        self.x = 0
        self.y = self.naytto.get_height() - 100 - self.robo.get_height()
        self.alusta_peli()
        
        self.aloitusaika = pygame.time.get_ticks()
        self.kello = pygame.time.Clock()

        self.peli_jatkuu = True
        self.pelin_tila = "ohjeistus"
        self.lopputulos = ""

    def pelaa(self):
        while self.peli_jatkuu:
            if self.pelin_tila == "ohjeistus":
                self.tutki_tapahtumat()
                self.liiku()
                self.hyppy()
                self.nayta_ohjeet()
            if self.pelin_tila == "kaynnissa":
                self.tutki_tapahtumat()
                self.liiku()
                self.hyppy()
                self.piirra_naytto()
                self.seuraa_aikaa()
            if self.pelin_tila == "tulokset":
                self.tutki_tapahtumat()
                self.liiku()
                self.hyppy()
                self.nayta_tulokset()

    def nayta_ohjeet(self):
        self.piirra_tausta()
        self.nayta_pisteet_ja_aika()
        self.naytto.blit((self.fontti.render(f"Liiku nuolinäppäimillä, hyppää välilyönnistä", True, (255,255,255))), (150, 200))
        self.naytto.blit((self.fontti.render(f"Klikkaa näyttöä aloittaaksesi pelin", True, (255,255,255))), (150, 240))
        self.naytto.blit(self.robo, (self.x, self.y))

        pygame.display.flip()
        self.kello.tick(60)

    def tutki_tapahtumat(self):
        for tapahtuma in pygame.event.get():

            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_LEFT:
                    self.vasemmalle = True
                if tapahtuma.key == pygame.K_RIGHT:
                    self.oikealle = True
                if tapahtuma.key == pygame.K_SPACE:
                    self.hyppaa = True

            if tapahtuma.type == pygame.KEYUP:
                if tapahtuma.key == pygame.K_LEFT:
                    self.vasemmalle = False
                if tapahtuma.key == pygame.K_RIGHT:
                    self.oikealle = False

            if tapahtuma.type == pygame.MOUSEBUTTONDOWN and self.pelin_tila == "ohjeistus":
                self.uusi_peli()

            if tapahtuma.type == pygame.MOUSEBUTTONDOWN and self.pelin_tila == "tulokset":
                self.uusi_peli()
                
            if tapahtuma.type == pygame.QUIT:
                exit()

    def liiku(self):
        if self.oikealle and self.x + self.robo.get_width() <= self.naytto.get_width():
            self.x += 3
        if self.vasemmalle and self.x >= 0:
            self.x -= 3

    def hyppy(self):
        if self.hyppaa and self.hypyn_kaari >= -10:
            hypyn_korkeus = 0.5
            if self.hypyn_kaari < 0:
                hypyn_korkeus = -0.5
            self.y -= (self.hypyn_kaari ** 2) * 0.5 * hypyn_korkeus
            self.hypyn_kaari -= 1
        else:
            self.hyppaa = False
            self.hypyn_kaari = 10

    def piirra_naytto(self):
        self.piirra_tausta()
        self.nayta_pisteet_ja_aika()
        self.naytto.blit(self.robo, (self.x, self.y))
        
        self.tuo_kolikko_naytolle()
        self.lisaa_vaikeutta()
        self.kolikot = self.tarkasta_kolikot()
        self.morot = self.tarkasta_morot()
        
        if len(self.kolikot) != 0:
            for kolikko in self.kolikot:
                self.naytto.blit(kolikko["kolikko"], (kolikko["x"], kolikko["y"]))

        if len(self.morot) != 0:
            for morko in self.morot:
                self.naytto.blit(morko["morko"], (morko["x"], morko["y"]))

        pygame.display.flip()
        self.kello.tick(60)

    def seuraa_aikaa(self):
        aika_nyt = pygame.time.get_ticks()
        kulunut_aika = aika_nyt - self.aloitusaika
        self.peliaika = max(0, 3 * 60 * 1000 - kulunut_aika)
        if self.peliaika == 0:
            self.pelin_tila = "tulokset"
            self.laske_tulokset()

    def tarkasta_kolikot(self):
        kolikot_naytolla = []
        for kolikon_tiedot in self.kolikot:
            kolikko = kolikon_tiedot["kolikko"]
            x_kolikko = kolikon_tiedot["x"]
            y_kolikko = kolikon_tiedot["y"]
            y_kolikko += 2
            if y_kolikko < (self.naytto.get_height() - 100 - kolikko.get_height()) and not self.nappaa_kolikko(kolikon_tiedot):
                kolikot_naytolla.append({"kolikko": kolikko, "x": x_kolikko, "y": y_kolikko})
            if y_kolikko >= (self.naytto.get_height() - 100 - kolikko.get_height()) and not self.nappaa_kolikko(kolikon_tiedot):
                self.morko_nappaa_kolikon()
        return kolikot_naytolla

    def tarkasta_morot(self):
        morot_naytolla = []
        x_kaikki_morot = []
        for kolikko in self.kolikot:
            if kolikko["y"] >= (self.naytto.get_height() - 110 - kolikko["kolikko"].get_height()) and not self.nappaa_kolikko(kolikko):
                if kolikko["x"] not in x_kaikki_morot:
                    x_kaikki_morot.append(kolikko["x"])
                    morot_naytolla.append({"morko": self.morko, "x": kolikko["x"], "y": 378})
        return morot_naytolla

    def nappaa_kolikko(self, kolikko):
        tormaysalue = 50
        keskikohta_robo = ((self.x + (self.robo.get_width()/2)), (self.y + (self.robo.get_height()/2)))
        keskikohta_kolikko = ((kolikko["x"] + (kolikko["kolikko"].get_width()/2)), (kolikko["y"] + (kolikko["kolikko"].get_height()/2)))
        if math.sqrt((keskikohta_kolikko[0] - keskikohta_robo[0])**2 + (keskikohta_kolikko[1]-keskikohta_robo[1])**2) < tormaysalue:
            self.omat_pisteet += 1
            return True
        return False

    def morko_nappaa_kolikon(self):
        self.morkojen_pisteet += 1

    def luo_uusi_kolikko(self):
        x_kolikko = random.randint(0, self.naytto.get_width() - self.kolikko.get_width())
        y_kolikko = 0
        return (self.kolikko, x_kolikko, y_kolikko)

    def tuo_kolikko_naytolle(self):
        self.kolikko_laskuri += 1
        if self.kolikko_laskuri >= self.kolikon_ilmestymisvali:
            kolikko, x_kolikko, y_kolikko = self.luo_uusi_kolikko()
            self.kolikot.append({"kolikko": kolikko, "x": x_kolikko, "y": y_kolikko})
            self.vaikeutta_lisaa += 1
            self.kolikko_laskuri = 0

    def lisaa_vaikeutta(self):
        if self.vaikeutta_lisaa > 9:
            if self.kolikon_ilmestymisvali >= 25:
                self.kolikon_ilmestymisvali -= 5
            self.vaikeutta_lisaa = 0

    def laske_tulokset(self):
        if self.omat_pisteet > self.morkojen_pisteet:
            self.lopputulos = "Voitit pelin"
        elif self.omat_pisteet < self.morkojen_pisteet:
            self.lopputulos = "Hävisit pelin"
        else:
            self.lopputulos = "Tasapeli"

    def nayta_tulokset(self):
        self.piirra_tausta()
        self.nayta_pisteet_ja_aika()
        self.naytto.blit((self.fontti.render(f"{self.lopputulos}", True, (255,255,255))), (270, 200))
        self.naytto.blit((self.fontti.render(f"Klikkaa näyttöä pelataksesi uudelleen", True, (255,255,255))), (150, 240))
        self.naytto.blit(self.robo, (self.x, self.y))

        pygame.display.flip()
        self.kello.tick(60)

    def nayta_pisteet_ja_aika(self):
        self.naytto.blit((self.fontti.render(f"Robo: {self.omat_pisteet}", True, (255,255,255))), (20, 20))
        self.naytto.blit((self.fontti.render(f"Möröt: {self.morkojen_pisteet}", True, (255,255,255))), (20, 50))
        self.naytto.blit((self.fontti.render(f"Aikaa jäljellä: {(self.peliaika // 60000):02}:{((self.peliaika % 60000) // 1000):02}", True, (255,255,255))), (455, 20))

    def piirra_tausta(self):
        self.naytto.fill((255, 150, 150))
        pygame.draw.rect(self.naytto, (255, 220, 200), (0, self.naytto.get_height()-100, self.naytto.get_width(), self.naytto.get_height()))

    def alusta_peli(self):
        self.oikealle = False
        self.vasemmalle = False
        self.hyppaa = False
        self.hypyn_kaari = 10

        self.kolikot = []
        self.kolikon_ilmestymisvali = 60
        self.kolikko_laskuri = 0
        self.vaikeutta_lisaa = 0

        self.morot = []

        self.omat_pisteet = 0
        self.morkojen_pisteet = 0

        self.peliaika = 3 * 60 * 1000

    def uusi_peli(self):
        self.alusta_peli()
        self.aloitusaika = pygame.time.get_ticks()

        self.peli_jatkuu = True
        self.pelin_tila = "kaynnissa"
        self.lopputulos = ""
        
if __name__ == "__main__":
    peli = Kolikkosade()
    peli.pelaa()

