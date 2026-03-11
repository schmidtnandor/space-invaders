from Game import Game
import pygame
import sys
from alien import Alien  # Beimportáljuk az osztályodat

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    # 1. Kell egy csoport, ami tárolja az összes megszületett alient
    aliens = pygame.sprite.Group()

    # 2. Időzítő beállítása (ezredmásodpercben)
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 2000) # 2 másodpercenként küld egy jelet

    while True:
        # Események kezelése
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            # 3. SPAWNOLÁS: Ha az időzítő jelez, csinálunk egy új alient
            if event.type == SPAWN_EVENT:
                uj_alien = Alien(screen)
                aliens.add(uj_alien)

        # FRISSÍTÉS
        # Végigmegyünk a csoporton és mindenkin meghívjuk a te mozgásfüggvényedet
        for alien in aliens:
            alien.mozgas()
            alien.check_screen()

        # RAJZOLÁS
        screen.fill((30, 30, 30)) # Háttér színe
        
        # Kirajzoljuk az összes alient a csoportból
        for alien in aliens:
            alien.blitme()

        pygame.display.flip()

run_game()


def main() -> None:
    game = Game()


if __name__ == "__main__":
    main()
