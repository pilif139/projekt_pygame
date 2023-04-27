import pygame
import os

pygame.init()
SCREEN_W = 800  # szerokosc
SCREEN_H = 600  # wysokosc

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("gra")  # Nazwa gry

rpgfont = pygame.font.Font("RPGFONT.ttf", 30)  # font

bulletImg = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenadeImg = pygame.image.load("img/icons/grenade.png").convert_alpha()

gravity = 0.75
fps = 60


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, type, ammunition, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.alive = True
        self.hp = 100
        self.maxHp = self.hp
        self.type = type
        self.speed = speed
        self.jumpSpeed = 0
        self.direction = 1
        self.shootCooldown = 0
        self.grenades = grenades
        self.ammunition = ammunition
        self.startAmmo = ammunition
        self.jump = False
        self.inAir = False
        self.flip = False

        # animacje
        self.animation = []
        self.AnimationIndex = 0
        self.action = 0
        self.updateTime = pygame.time.get_ticks()
        animationType = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animationType:
            temp_list = []
            framesNumber = len(os.listdir(f'img/{self.type}/{animation}'))
            for i in range(framesNumber):
                img = pygame.image.load(f'img/{self.type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation.append(temp_list)

        self.image = self.animation[self.action][self.AnimationIndex]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.animate()
        self.checkAlive()
        if self.shootCooldown > 0:
            self.shootCooldown -= 1

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

        if self.jump == True and self.inAir == False:
            self.jumpSpeed = - 10
            self.jump = False
            self.inAir = True

        self.jumpSpeed += gravity
        if self.jumpSpeed > 9:
            self.jumpSpeed = 9
        dy += self.jumpSpeed

        if self.rect.bottom + dy > 320:
            dy = 320 - self.rect.bottom
            self.inAir = False

        self.rect.x += dx
        self.rect.y += dy

    def animate(self):
        self.image = self.animation[self.action][self.AnimationIndex]

        if pygame.time.get_ticks() - self.updateTime > 100:
            self.AnimationIndex += 1
            self.updateTime = pygame.time.get_ticks()
        if self.AnimationIndex >= len(self.animation[self.action]):
            if self.action == 3:
                self.AnimationIndex = len(self.animation[self.action]) - 1
            else:
                self.AnimationIndex = 0

    def shoot(self):
        if self.shootCooldown == 0 and self.ammunition > 0:
            self.shootCooldown = 30
            bullet = Bullet(int(self.rect.centerx + (self.rect.size[0] * 0.65 * self.direction)),
                            self.rect.centery, self.direction)
            bulletGroup.add(bullet)
            self.ammunition -= 1

    def updateAction(self, newAction):
        if newAction != self.action:
            self.action = newAction
            self.AnimationIndex = 0
            self.updateTime = pygame.time.get_ticks()

    def checkAlive(self):
        if self.hp <= 0:
            self.alive = False
            self.hp = 0
            self.speed = 0
            self.updateAction(3)

    def draw(self):
        self.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bulletImg
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_W:
            self.kill()
        if pygame.sprite.spritecollide(player, bulletGroup, False):
            if player.alive:
                player.hp -= 5
                self.kill()
        if pygame.sprite.spritecollide(monster, bulletGroup, False):
            if monster.alive:
                monster.hp -= 20
                self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.speed_y = -8
        self.speed = 12
        self.image = grenadeImg
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.speed_y += gravity
        dx = self.direction * self.speed
        dy = self.speed_y

        # kolizja z podłogą
        if self.rect.bottom + dy > 320:
            dy = 320 - self.rect.bottom
            self.speed = 0

        # kolizja z koncem ekranu
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_W:
            self.direction *= -0.5
            dx = self.direction * self.speed

        self.rect.x += dx
        self.rect.y += dy


def drawBackground():
    screen.fill((10, 10, 10))
    pygame.draw.line(screen, (255, 0, 0), (0, 320), (SCREEN_W, 320))


def drawText(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


run = True
clock = pygame.time.Clock()

grenadeGroup = pygame.sprite.Group()
bulletGroup = pygame.sprite.Group()

player = Player(250, 250, 3, 5, 'player', 20, 3)
monster = Player(400, 250, 3, 5, 'enemy', 20, 0)

GrenadeThrown = False
grenade = False
shoot = False
mouseClick = False
movingLeft = False
movingRight = False

while run:
    clock.tick(fps)

    drawBackground()

    player.update()
    player.draw()

    monster.update()
    monster.draw()

    bulletGroup.update()
    bulletGroup.draw(screen)

    grenadeGroup.update()
    grenadeGroup.draw(screen)

    mouseClick = False

    if player.alive:
        if shoot:
            player.shoot()
        elif grenade and GrenadeThrown == False and player.grenades > 0:
            grenade1 = Grenade(player.rect.centerx + player.rect.size[0] * 0.5 * player.direction,
                               player.rect.top, player.direction)
            grenadeGroup.add(grenade1)
            GrenadeThrown = True
            player.grenades -= 1
        if player.inAir:
            player.updateAction(2)
        elif movingLeft or movingRight:
            player.updateAction(1)  # 1: porusza sie -- 0:nie porusza sie -- 2:W powietrzu (zmiana animacji)
        else:
            player.updateAction(0)
        player.move(movingLeft, movingRight)

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
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                movingLeft = False
            if event.key == pygame.K_d:
                movingRight = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_g:
                grenade = False
                GrenadeThrown = False

    pygame.display.update()
