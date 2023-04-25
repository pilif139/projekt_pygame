import pygame

pygame.init()
SCREEN_W = 800  # szerokosc
SCREEN_H = 600  # wysokosc

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("gra")  # Nazwa gry

rpgfont = pygame.font.Font("RPGFONT.ttf", 30)  # font

def drawText(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.speed = speed
        self.direction = 1
        self.flip = False
        img = pygame.image.load(f'img/{self.type}/Idle/0.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, movingLeft, movingRight):
        dx = 0
        dy = 0
        if movingLeft:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if movingRight:
            dx = self.speed
            self.flip = False
            self.direction = 1
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


def main():
    run = True
    clock = pygame.time.Clock()
    fps = 60

    player = Player(250, 250, 3, 5, 'player')
    monster = Player(400, 250, 3, 5, 'enemy')

    mouseClick = False
    movingLeft = False
    movingRight = False

    while run:
        clock.tick(fps)

        screen.fill((0, 0, 0))

        # mx, my = pygame.mouse.get_pos()  # pozycja myszki na ekranie
        #
        # StartButton = pygame.Rect(10, 20, 270, 70)
        # pygame.draw.rect(screen, (50, 50, 50), StartButton)
        # drawText("START", rpgfont, (255, 255, 255), screen, 20, 40)
        #
        # ContinueButton = pygame.Rect(10, 110, 270, 70)
        # pygame.draw.rect(screen, (50, 50, 50), ContinueButton)
        # drawText("WCZYTAJ SAVE", rpgfont, (255, 255, 255), screen, 20, 130)
        #
        # OptionsButton = pygame.Rect(10, 200, 270, 70)
        # pygame.draw.rect(screen, (50, 50, 50), OptionsButton)
        # drawText("STEROWANIE", rpgfont, (255, 255, 255), screen, 20, 220)
        #
        # EscapeButton = pygame.Rect(10, 290, 270, 70)
        # pygame.draw.rect(screen, (255, 20, 20), EscapeButton)
        # drawText("QUIT", rpgfont, (255, 255, 255), screen, 20, 310)
        #
        # if StartButton.collidepoint((mx, my)):
        #     if mouseClick:
        #         print("start")
        # if ContinueButton.collidepoint((mx, my)):
        #     if mouseClick:
        #         print("wczytaj save")
        # if OptionsButton.collidepoint((mx, my)):
        #     if mouseClick:
        #         print("opcje")
        # if EscapeButton.collidepoint((mx, my)):
        #     if mouseClick:
        #         run = False

        mouseClick = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # wcisniecie lewego przycisku myszki
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseClick = True

            # ruch klawiaturą
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    movingLeft = True
                if event.key == pygame.K_d:
                    movingRight = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    movingLeft = False
                if event.key == pygame.K_d:
                    movingRight = False

        player.move(movingLeft, movingRight)
        player.draw()

        monster.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
