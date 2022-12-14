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
        pygame.display.set_caption("マップファイル読み込み")

        # ブロック画像のロード
        Block.image = load_image("block.png", -1)

        # マップのロード
        self.map = Map("data/test.map")

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
        self.map.update()

    def draw(self, screen):
        self.map.draw()

        #オフセットに基づいてマップの一部を画面に描画
        offsetx, offsety = self.map.calc_offset()

        # 端ではスクロールしない
        if offsetx < 0:
            offsetx = 0
        elif offsetx > self.map.width - SCR_RECT.width:
            offsetx = self.map.width - SCR_RECT.width

        if offsety < 0:
            offsety = 0
        elif offsety > self.map.height - SCR_RECT.height:
            offsety = self.map.height - SCR_RECT.height

        # マップの一部を画面に描画
        screen.blit(self.map.surface, (0,0), (offsetx, offsety, SCR_RECT.width, SCR_RECT.height))

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
    MOVE_SPEED = 5.0  # 移動最大速度
    MOVE_ACCEL = 0.3
    JUMP_SPEED = 8.0
    GRAVITY = 0.25
    direction = DOWN
    
    def __init__(self,filename,pos,blocks):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = split_image(load_image(filename))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks #衝突判定用

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
        #慣性力(x軸方向)
        inertia = 0.3
        # キー入力取得
        pressed_keys = pygame.key.get_pressed()

        # 左右移動
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.direction = RIGHT
            if self.fpvx <= self.MOVE_SPEED:
                self.fpvx = self.fpvx + self.MOVE_ACCEL
                if self.fpvx >= self.MOVE_SPEED:
                    self.fpvx = self.MOVE_SPEED
            self.image = self.images[int(self.direction * 3 + self.frame / self.animycle%3)]
            
        elif pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.direction = LEFT
            if self.fpvx >= - self.MOVE_SPEED:
                self.fpvx = self.fpvx - self.MOVE_ACCEL
                if self.fpvx <= -self.MOVE_SPEED:
                    self.fpvx = -self.MOVE_SPEED
            #self.fpvx = -self.MOVE_SPEED
            self.image = self.images[int(self.direction * 3 + self.frame / self.animycle%3)]
            
        else:
            if self.direction == RIGHT:
                self.image = self.images[16]
                self.fpvx = self.fpvx - inertia
                if self.fpvx <= 0:
                    self.fpvx = 0
                    self.direction = DOWN


            if self.direction == LEFT:
                self.image = self.images[13]
                self.fpvx = self.fpvx + inertia
                if self.fpvx >= 0:
                    self.fpvx = 0
                    self.direction = DOWN
        
        #ジャンプ
        if pressed_keys[K_UP] or pressed_keys[K_SPACE]:
            if self.on_floor:
                self.fpvy = -self.JUMP_SPEED
                self.on_floor = False

        # 速度を更新
        if not self.on_floor:
            self.fpvy += self.GRAVITY  # 下向きに重力をかける


        """
        # 着地したか調べる
        if self.fpy > SCR_RECT.height - self.rect.height:
            self.fpy = SCR_RECT.height - self.rect.height  # 床にめり込まないように位置調整
            self.fpvy = 0
            self.on_floor = True
        """

        
        # X方向の衝突判定処理
        self.collision_x()

        # この時点でX方向に関しては衝突がないことが保証されてる

        # Y方向の衝突判定処理
        self.collision_y()

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)


    def collision_x(self):
        """X方向の衝突判定処理"""
        # キャラクターのサイズ
        width = self.rect.width
        height = self.rect.height

        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx
        newrect = Rect(newx, self.fpy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvx > 0:    # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpx = newx


    def collision_y(self):
        """Y方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height

        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        newrect = Rect(self.fpx, newy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvy > 0:    # 下に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpy = block.rect.top - height
                    self.fpvy = 0
                    # 下に移動中に衝突したなら床の上にいる
                    self.on_floor = True
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpy = newy
                # 衝突ブロックがないなら床の上にいない
                self.on_floor = False
        

class Block(pygame.sprite.Sprite):
    """ブロック"""
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

class Map:
    """マップ（プレイヤーや内部のスプライトを含む)"""
    GS = 32 #グリッドサイズ

    def __init__(self,filename):
        #スプライトグループの登録
        self.all = pygame.sprite.RenderUpdates()
        self.blocks = pygame.sprite.Group()
        Character.containers = self.all
        Block.containers = self.all, self.blocks

        #プレイヤーの作成
        self.Character = Character("hiyoco.png",(300,200),self.blocks)

        #マップをロードしてマップ内スプライトの作成
        self.load(filename)

        #マップサーフェイスを作成
        self.surface = pygame.Surface((self.col * self.GS, self.row * self.GS)).convert()
    
    def draw(self):
        """マップサーフェイスにマップナイスプライを描画"""
        self.surface.fill((0,0,0))
        self.all.draw(self.surface)

    def update(self):
        """マップ内スプライトを更新"""
        self.all.update()

    def calc_offset(self):
        """オフセットを計算"""
        offsetx = self.Character.rect.topleft[0] - SCR_RECT.width/2
        offsety = self.Character.rect.topleft[1] - SCR_RECT.height/2
        print(offsetx,offsety)
        return offsetx, offsety

    def load(self,filename):
        """マップをロードしてスプライトを作成"""
        map = []
        fp = open(filename, "r")
        for line in fp:
            line = line.rstrip()  # 改行除去
            map.append(list(line))
            self.row = len(map)
            self.col = len(map[0])
        self.width = self.col * self.GS
        self.height = self.row * self.GS
        fp.close()

        # マップからスプライトを作成
        for i in range(self.row):
            for j in range(self.col):
                if map[i][j] == 'B':
                    Block((j*self.GS, i*self.GS))  # ブロック

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