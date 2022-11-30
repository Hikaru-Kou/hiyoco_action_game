#!/usr/bin/env python
import pygame
from pygame.locals import *
import os
import sys

SCR_RECT = Rect(0,0,640,480)

GS = 32

class PyAction:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("最初")
        load = loader()
        #画像のロード
        # キャラクターチップをロード

        #オブジェクトグループとキャラの作成
        self.all = pygame.sprite.RenderUpdates()
        Character.containers = self.all
        player = Character("hiyoco.png")

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

    def draw(self,screen):
       """スプライト描画"""
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
    """自操作キャラクラス定義"""
    """移動速度をクラス変数として設定"""
    MOVE_SPEED = 5.0 #移動速度（1fps中のどの程度動くのかを設定)
    images = {}
    def __init__(self,filename):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = loader.split_image(loader.load_image(filename))
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom

        #浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0
    
    def update(self):
        """スプライトの更新"""
        #キー入力取得
        pressed_keys = pygame.key.get_pressed()

        #左右移動
        if pressed_keys[K_RIGHT]:
            self.image = self.right_image
            self.fpvx = self.MOVE_SPEED
        elif pressed_keys[K_LEFT]:
            self.image = self.left_image
            self.fpvx = -self.MOVE_SPEED
        else:
            self.fpvx = 0.0
        
        #浮動小数点の位置を更新
        self.fpx += self.fpvx

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

class loader():
    def load_image(filename,colorkey = None):
        print(filename)
        #filename = os.path.join(dir, filename)
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


    def split_image(self,image):
        """96x192のキャラクターイメージを32x32の16枚のイメージに分割"""
        """分割したイメージを格納したリストを返す"""
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