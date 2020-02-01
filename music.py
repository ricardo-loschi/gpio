# Importando o PyGame
import pygame
import os

# Inicializando o PyGame
pygame.init()

# Carregando o arquivo MP3 e executando
if os.path.exists('alarme.mp3'):
    pygame.mixer.music.load('alarme.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(10)

    clock = pygame.time.Clock()
    clock.tick(10)
    '''
    while pygame.mixer.music.get_busy():
        pygame.event.poll()
        clock.tick(10)
    '''
else:
    print('O arquivo alerta.mp3 nao esta no diretario do script Python')
