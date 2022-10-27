#!/usr/bin/env python
import pygame
from pygame.locals import *
import os
import sys

SCR_RECT = Rect(0,0,640,480)

class PyAction:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("最初")
        self.all = pygame.sprite.RenderUpdates()

        # メインループ
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()


if __name__ == "__main__":
    PyAction()