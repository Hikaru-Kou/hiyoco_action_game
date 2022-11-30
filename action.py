#!/usr/bin/env python
import pygame
from pygame.locals import *
import os
import sys

SCR_RECT = Rect(0, 0, 640, 480)
GS = 32
DOWN,LEFT,RIGHT= 1,4,5


class PyAction:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("アニメーション(移動)")

        self.all = pygame.sprite.RenderUpdates()
        Character.containers = self.all

        # 画像のロード
        player = Character("hiyoco.png",0,0)               

        # メインループ
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()

    def update(self):
        """スプライトの更新"""
        self.all.update()

    def draw(self, screen):
        """スプライトの描画"""
        screen.fill((0,0,0))
        self.all.draw(screen)

    def key_handler(self):
        """キー入力処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    

class Character(pygame.sprite.Sprite):
    animycle = 12
    frame = 0
    MOVE_SPEED = 5.0  # 移動速度
    JUMP_SPEED = 8.0
    GRAVITY = 0.2
    direction = RIGHT
    
    
    def __init__(self,filename,x,y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = split_image(load_image(filename))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom

        # 浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        #地面にいるか？
        self.on_floor = False


    def update(self):
        """スプライトの更新"""
         # キャラクターアニメーション
        self.frame += 1
        # キー入力取得
        pressed_keys = pygame.key.get_pressed()

        # 左右移動
        if pressed_keys[K_RIGHT]:
            self.direction = RIGHT
            self.fpvx = self.MOVE_SPEED
            self.image = self.images[int(self.direction * 3 + self.frame / self.animycle%3)]
            
        elif pressed_keys[K_LEFT]:
            self.direction = LEFT
            self.fpvx = -self.MOVE_SPEED
            self.image = self.images[int(self.direction * 3 + self.frame / self.animycle%3)]
            
        else:
            if self.direction == RIGHT:
                self.image = self.images[16]

            if self.direction == LEFT:
                self.image = self.images[13]

            self.fpvx = 0.0
        
        #ジャンプ
        if pressed_keys[K_UP] or pressed_keys[K_SPACE]:
            if self.on_floor:
                self.fpvy = -self.JUMP_SPEED
                self.on_floor = False

        # 速度を更新
        if not self.on_floor:
            self.fpvy += self.GRAVITY  # 下向きに重力をかける
        # 浮動小数点の位置を更新
        self.fpx += self.fpvx
        self.fpy += self.fpvy

        # 着地したか調べる
        if self.fpy > SCR_RECT.height - self.rect.height:
            self.fpy = SCR_RECT.height - self.rect.height  # 床にめり込まないように位置調整
            self.fpvy = 0
            self.on_floor = True
            
        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)
        

def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:", filename)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def split_image(image):
    """96x192のキャラクターイメージを32x32の18のイメージに分割
    分割したイメージを格納したリストを返す"""
    imageList = []
    for i in range(0, 96, GS):
        for j in range(0, 192, GS):
            surface = pygame.Surface((GS,GS))
            surface.blit(image, (0,0), (j,i,GS,GS))
            surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
            surface.convert()
            imageList.append(surface)
    return imageList

if __name__ == "__main__":
    PyAction()
