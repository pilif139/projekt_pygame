import pygame
from pygame import mixer
import random
import os
import csv
import button

pygame.mixer.pre_init(22050, -16, 2, 1024)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(22050, -16, 2, 1024)

SCREEN_W = 1000  # szerokosc
SCREEN_H = 800  # wysokosc

ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_H // ROWS
TILE_TYPES = 21
MapLevel = 0
MaxLevel = 4  # ilość leveli dostępnych -1
SCROLL_VALUE = 100
screen_scroll = 0
bg_scroll = 0

startGame = False
startIntro = False

gravity = 0.75
fps = 63

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Shooting Stickman")  # Nazwa gry

rpgfont = pygame.font.Font("RPGFONT.ttf", 30)  # font

# dźwięki
pygame.mixer.music.load("audio/soundtrack.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0)
jumpSound = pygame.mixer.Sound('audio/jump.wav')
jumpSound.set_volume(0.5)
shotSound = pygame.mixer.Sound('audio/shot.wav')
shotSound.set_volume(0.2)
grenadeSound = pygame.mixer.Sound('audio/grenade.wav')
grenadeSound.set_volume(0.5)

tlo1 = pygame.image.load("img/Background/pine1.png").convert_alpha()
tlo2 = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountainImg = pygame.image.load("img/Background/mountain.png").convert_alpha()
skyImg = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()

startImg = pygame.image.load("img/start_btn.png").convert_alpha()
restartImg = pygame.image.load("img/restart_btn.png").convert_alpha()
exitImg = pygame.image.load("img/exit_btn.png").convert_alpha()

TilesList = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{i}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    TilesList.append(img)

bulletImg = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenadeImg = pygame.image.load("img/icons/grenade.png").convert_alpha()

hpBoxImg = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammoBoxImg = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenadeBoxImg = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
itemList = {
    'Health': hpBoxImg,
    'Ammo': ammoBoxImg,
    'Grenade': grenadeBoxImg,
}


def drawBackground():
    screen.fill((10, 192, 192))
    width = skyImg.get_width()
    for j in range(5):
        screen.blit(skyImg, ((j * width) - bg_scroll * 0.5, 0))
        screen.blit(mountainImg, ((j * width) - bg_scroll * 0.6, SCREEN_H - mountainImg.get_height() - 300))
        screen.blit(tlo1, ((j * width) - bg_scroll * 0.7, SCREEN_H - tlo1.get_height() - 150))
        screen.blit(tlo2, ((j * width) - bg_scroll * 0.8, SCREEN_H - tlo2.get_height()))


def drawText(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def reset():
    monsterGroup.empty()
    bulletGroup.empty()
    grenadeGroup.empty()
    explosionGroup.empty()
    itemBoxGroup.empty()
    decorationGroup.empty()
    waterGroup.empty()
    exitGroup.empty()

    data = []
    for i in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


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
        self.drownCooldown = 250
        self.grenades = grenades
        self.ammunition = ammunition
        self.startAmmo = ammunition
        self.jump = False
        self.inAir = False
        self.flip = False

        # AI
        self.moveCounter = 0
        self.resting = False
        self.restingCounter = 0
        self.vision = pygame.Rect(0, 0, 250, 50)

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
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.animate()
        self.checkAlive()
        if self.shootCooldown > 0:
            self.shootCooldown -= 1

    def move(self, movingLeft, movingRight):
        screenScroll = 0
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
            self.jumpSpeed = - 13
            self.jump = False
            self.inAir = True

        # grawitacja
        self.jumpSpeed += gravity
        dy += self.jumpSpeed

        # kolizje
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # AI
                if self.type == 'enemy':
                    self.direction *= -1
                    self.moveCounter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.jumpSpeed < 0:
                    self.jumpSpeed = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.jumpSpeed >= 0:
                    self.jumpSpeed = 0
                    self.inAir = False
                    dy = tile[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, waterGroup, False):
            self.drownCooldown -= 1

        if pygame.sprite.spritecollide(self, waterGroup, False) and self.drownCooldown == 0:
            self.hp -= 5
            self.drownCooldown = 100

        levelComplete = False
        if pygame.sprite.spritecollide(self, exitGroup, False):
            levelComplete = True

        if self.rect.bottom > SCREEN_H:
            self.hp = 0

        if self.type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_W:
                dx = 0

        # update
        self.rect.x += dx
        self.rect.y += dy

        if self.type == 'player':
            if (self.rect.right > SCREEN_W - SCROLL_VALUE and bg_scroll < (world.levelLenght * TILE_SIZE) - SCREEN_W) \
                    or (self.rect.left < SCROLL_VALUE and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screenScroll = -dx

        return screenScroll, levelComplete

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
            bullet = Bullet(int(self.rect.centerx + (self.rect.size[0] * 0.75 * self.direction)),
                            self.rect.centery, self.direction)
            bulletGroup.add(bullet)
            self.ammunition -= 1
            shotSound.play(1, 0)

    def AI(self):
        if self.alive and player.alive:
            if self.resting == False and random.randint(1, 300) == 1:
                self.resting = True
                self.restingCounter = 70
                self.updateAction(0)
            if self.vision.colliderect(player.rect):
                self.updateAction(0)
                self.shoot()
            else:
                if self.resting == False:
                    if self.direction == 1:
                        AI_moveRight = True
                    else:
                        AI_moveRight = False
                    AI_moveLeft = not AI_moveRight
                    self.move(AI_moveLeft, AI_moveRight)
                    self.updateAction(1)
                    self.moveCounter += 1
                    self.vision.center = (self.rect.centerx + 125 * self.direction, self.rect.centery)

                    if self.moveCounter > TILE_SIZE:
                        self.direction *= -1
                        self.moveCounter *= -1
                else:
                    self.restingCounter -= 1
                    if self.restingCounter <= 0:
                        self.resting = False

        self.rect.x += screen_scroll

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


class World:
    def __init__(self):
        self.obstacle_list = []
        self.levelLenght = 0

    def process_data(self, data):
        global player, hpBar
        self.levelLenght = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = TilesList[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(x * TILE_SIZE, y * TILE_SIZE, img)
                        waterGroup.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(x * TILE_SIZE, y * TILE_SIZE, img)
                        decorationGroup.add(decoration)
                    elif tile == 15:
                        player = Player(x * TILE_SIZE, y * TILE_SIZE, 2.3, 5, 'player', 20, 3)
                        hpBar = HpBar(65, 14, player.hp, player.maxHp)
                    elif tile == 16:
                        monster = Player(x * TILE_SIZE, y * TILE_SIZE, 2.3, 3, 'enemy', 20, 0)
                        monsterGroup.add(monster)
                    elif tile == 17:
                        item_box = ItemBox(x * TILE_SIZE, y * TILE_SIZE, 'Ammo')
                        itemBoxGroup.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox(x * TILE_SIZE, y * TILE_SIZE, 'Grenade')
                        itemBoxGroup.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox(x * TILE_SIZE, y * TILE_SIZE, 'Health')
                        itemBoxGroup.add(item_box)
                    elif tile == 20:
                        exit = Exit(x * TILE_SIZE, y * TILE_SIZE, img)
                        exitGroup.add(exit)

        return player, hpBar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, x, y, itemType):
        pygame.sprite.Sprite.__init__(self)
        self.itemType = itemType
        self.image = itemList[self.itemType]
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.itemType == 'Health':
                player.hp += 25
                if player.hp >= player.maxHp:
                    player.hp = player.maxHp
            elif self.itemType == 'Ammo':
                player.ammunition += 12
            elif self.itemType == 'Grenade':
                player.grenades += 2
            self.kill()
        self.rect.x += screen_scroll


class HpBar():
    def __init__(self, x, y, hp, maxHp):
        self.x = x
        self.y = y
        self.hp = hp
        self.maxHp = maxHp

    def draw(self, hp):
        self.hp = hp
        pygame.draw.rect(screen, (255, 255, 255), (self.x - 2, self.y - 2, 154, 34))
        pygame.draw.rect(screen, (10, 10, 10), (self.x, self.y, 150, 30))
        if player.hp > 0:
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150 * self.hp / self.maxHp, 30))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bulletImg
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_W:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bulletGroup, False):
            if player.alive:
                player.hp -= 5
                self.kill()
        for enemy in monsterGroup:
            if pygame.sprite.spritecollide(enemy, bulletGroup, False):
                if enemy.alive:
                    enemy.hp -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.speed_y = -10
        self.speed = 8
        self.image = grenadeImg
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.height = self.image.get_height()
        self.width = self.image.get_width()

    def update(self):
        self.speed_y += gravity
        dx = self.direction * self.speed
        dy = self.speed_y

        # kolizja z podłogą
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -0.8
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.speed_y < 0:
                    self.speed_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.speed_y >= 0:
                    self.speed_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenadeSound.play()
            explode = Explosion(self.rect.x, self.rect.y, 2)
            explosionGroup.add(explode)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.hp -= 70
            for enemy in monsterGroup:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.hp -= 70


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.animations = []
        for i in range(1, 6):
            img = pygame.image.load(f"img/explosion/exp{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.animations.append(img)
        self.AnimationIndex = 0
        self.image = self.animations[self.AnimationIndex]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        explosionSpeed = 7
        self.counter += 1
        if self.counter >= explosionSpeed:
            self.counter = 0
            self.AnimationIndex += 1
            if self.AnimationIndex >= len(self.animations):
                self.kill()
            else:
                self.image = self.animations[self.AnimationIndex]


class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fadeCounter = 0

    def fade(self):
        fadeComplete = False
        self.fadeCounter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fadeCounter, 0, SCREEN_W // 2, SCREEN_H))
            pygame.draw.rect(screen, self.color, (SCREEN_W // 2 + self.fadeCounter, 0, SCREEN_W, SCREEN_H))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fadeCounter, SCREEN_W, SCREEN_H // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_H // 2 + self.fadeCounter, SCREEN_W, SCREEN_H))
        if self.direction == 2:
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_W, 0 + self.fadeCounter))
        if self.fadeCounter >= SCREEN_W:
            fadeComplete = True

        return fadeComplete


introFade = ScreenFade(1, (0, 0, 0), 5)
deathFade = ScreenFade(2, (28, 0, 0), 12)

startButton = button.Button(20, 30, startImg, 1)
restartButton = button.Button(SCREEN_H // 2 - restartImg.get_width() // 2, SCREEN_H // 2 - 80, restartImg, 3)
exitButton = button.Button(20, 30 + startImg.get_height() + 20, exitImg, 1)

monsterGroup = pygame.sprite.Group()
grenadeGroup = pygame.sprite.Group()
bulletGroup = pygame.sprite.Group()
explosionGroup = pygame.sprite.Group()
itemBoxGroup = pygame.sprite.Group()

waterGroup = pygame.sprite.Group()
decorationGroup = pygame.sprite.Group()
exitGroup = pygame.sprite.Group()

world_data = []
for i in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f'level{MapLevel}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, hpBar = world.process_data(world_data)

run = True
clock = pygame.time.Clock()

GrenadeThrown = False
grenade = False
shoot = False
mouseClick = False
movingLeft = False
movingRight = False

while run:
    clock.tick(fps)

    if not startGame:
        # menu
        screen.fill((128, 189, 255))
        if startButton.draw(screen):
            startGame = True
            startIntro = True
        if exitButton.draw(screen):
            run = False

    else:
        drawBackground()
        world.draw()

        drawText(f"HP: ", rpgfont, (0, 0, 0), screen, 7, 18)
        drawText(f"HP: ", rpgfont, (255, 255, 255), screen, 10, 15)
        hpBar.draw(player.hp)
        if player.ammunition > 0:
            drawText(f"Ammo: {player.ammunition}", rpgfont, (0, 0, 0), screen, 7, 58)
            drawText(f"Ammo: {player.ammunition}", rpgfont, (255, 255, 255), screen, 10, 55)
        elif player.ammunition == 0:
            drawText("Ammo: ", rpgfont, (255, 255, 255), screen, 10, 55)
            drawText(str(player.ammunition), rpgfont, (255, 0, 0), screen, 118, 55)
        drawText(f"Granaty: ", rpgfont, (0, 0, 0), screen, 7, 98)
        drawText(f"Granaty: ", rpgfont, (255, 255, 255), screen, 10, 95)
        if player.grenades > 0:
            grenadeStat = grenadeImg
            grenadeStat = pygame.transform.scale(grenadeStat,
                                                 (int(grenadeStat.get_width() * 1.5),
                                                  int(grenadeStat.get_height() * 1.5)))
            for i in range(player.grenades):
                screen.blit(grenadeStat, (170 + (i * 15), 102.5))
        else:
            drawText("BRAK", rpgfont, (0, 0, 0), screen, 168, 97)
            drawText("BRAK", rpgfont, (255, 0, 0), screen, 170, 95)

        decorationGroup.draw(screen)
        decorationGroup.update()

        player.update()
        player.draw()

        for enemy in monsterGroup:
            enemy.AI()
            enemy.update()
            enemy.draw()

        bulletGroup.update()
        bulletGroup.draw(screen)

        grenadeGroup.update()
        grenadeGroup.draw(screen)

        explosionGroup.update()
        explosionGroup.draw(screen)

        itemBoxGroup.update()
        itemBoxGroup.draw(screen)

        waterGroup.update()
        waterGroup.draw(screen)

        exitGroup.update()
        exitGroup.draw(screen)

        mouseClick = False

        if startIntro:
            if introFade.fade():
                startIntro = False
                introFade.fadeCounter = 0

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
            screen_scroll, levelComplete = player.move(movingLeft, movingRight)
            bg_scroll -= screen_scroll
            if levelComplete:
                startIntro = True
                introFade.fadeCounter = 0
                MapLevel += 1
                bg_scroll = 0
                if MapLevel <= MaxLevel:
                    world_data = reset()
                    with open(f'level{MapLevel}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, hpBar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if deathFade.fade():
                if restartButton.draw(screen):
                    deathFade.fadeCounter = 0
                    startIntro = True
                    bg_scroll = 0
                    world_data = reset()
                    with open(f'level{MapLevel}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, hpBar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # wcisniecie lewego przycisku myszki
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseClick = True
        # ruch klawiaturą
        if event.type == pygame.KEYDOWN and startGame:
            if event.key == pygame.K_a:
                movingLeft = True
            if event.key == pygame.K_d:
                movingRight = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                jumpSound.play()
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

pygame.quit()
