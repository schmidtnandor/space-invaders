import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """Egy osztály, amely egyetlen idegent képvisel a flottában."""

    # Settings
    alien_speed: int
    alien_shoot_intensity: int
    alien_shoot_damage: int
    alien_hp: int
    
    # Minimum spacing between aliens to prevent overlapping
    MIN_SPACING = 8  # pixels - strictly enforced minimum gap

    def __init__(self, screen_width: int, screen_height: int, x: int = 0, y: int = 0):
        """Az idegen inicializálása és kezdőpozíciójának beállítása.
        
        Args:
            screen_width: A képernyő szélessége
            screen_height: A képernyő magassága
            x: Kezdő X pozíció (alapértelmezés: 0, a bal oldal)
            y: Kezdő Y pozíció (alapértelmezés: 0, a felső oldal)
        """
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Kép betöltése és 1/7-re skálázása
        self.image = pygame.image.load("grafika/enemy.png")
        # Scale to 1/7 of original size (multiply by 1/7 ≈ 0.142857)
        original_width = self.image.get_width()
        original_height = self.image.get_height()
        scaled_width = int(original_width / 7)
        scaled_height = int(original_height / 7)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
        self.rect = self.image.get_rect()

        # Settings
        self.alien_speed: int = 2  # Pixelek száma per frame
        self.alien_shoot_intensity: int = 1
        self.alien_shoot_damage: int = 1
        self.alien_hp: int = 1

        # Pozíció beállítása
        self.rect.x = x
        self.rect.y = y
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update_movement(self, fleet_moving_right: bool, fleet_is_dropping: bool, fleet_drop_speed: float):
        """Szinkronizált flottamozgás: az összes idegen ugyanolyan irányba mozog.
        
        Args:
            fleet_moving_right: A flotta jobbra mozog-e
            fleet_is_dropping: A flotta éppen csepegésben van-e
            fleet_drop_speed: A csepegés jelenlegi sebessége
        """
        if fleet_is_dropping:
            # Csepegés fázis: lefelé mozgás
            self.y += fleet_drop_speed
            self.rect.y = int(self.y)
        else:
            # Horizontális mozgás
            if fleet_moving_right:
                self.x += self.alien_speed
            else:
                self.x -= self.alien_speed
            
            self.rect.x = int(self.x)

    def check_screen(self):
        """Enforce screen boundaries while maintaining spacing and preventing sticking."""
        # Right boundary (with small margin to detect edge precisely)
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width - 1
            self.x = float(self.rect.x)
        
        # Left boundary (with small margin to detect edge precisely)
        elif self.rect.left < 0:
            self.rect.left = 1
            self.x = float(self.rect.x)
        
        # Top boundary (solid ceiling)
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = float(self.rect.y)
        
        # Bottom boundary (remove from screen)
        if self.rect.top >= self.screen_height:
            self.kill()

    def check_collision_with_aliens(self, aliens_group):
        """Strictly enforces spacing to prevent any overlapping or touching.
        
        Checks all nearby aliens and ensures minimum spacing is maintained
        in all directions - no images or hitboxes ever touch.
        
        Args:
            aliens_group: Az összes idegent tartalmazó sprite csoport
        """
        # Saját sprite kizárása az ütközés ellenőrzéséből
        colliding = pygame.sprite.spritecollide(self, aliens_group, False)
        colliding = [alien for alien in colliding if alien is not self]
        
        if colliding:
            # Calculate required adjustments to maintain minimum spacing
            max_offset_y = 0
            max_offset_x = 0
            
            for alien in colliding:
                # Vertical overlap check
                if self.rect.bottom > alien.rect.top:
                    vertical_overlap = self.rect.bottom - alien.rect.top
                    required_offset = vertical_overlap + self.MIN_SPACING
                    max_offset_y = max(max_offset_y, required_offset)
                
                # Horizontal overlap check
                if self.rect.right > alien.rect.left and self.rect.left < alien.rect.right:
                    if self.rect.centerx < alien.rect.centerx:
                        # This alien is to the left, move left
                        horizontal_overlap = self.rect.right - alien.rect.left
                        required_offset = horizontal_overlap + self.MIN_SPACING
                        max_offset_x = max(max_offset_x, required_offset)
                    else:
                        # This alien is to the right, move right
                        horizontal_overlap = alien.rect.right - self.rect.left
                        required_offset = horizontal_overlap + self.MIN_SPACING
                        max_offset_x = max(max_offset_x, required_offset)
            
            # Apply vertical adjustment (move up preferentially)
            if max_offset_y > 0:
                self.rect.y -= max_offset_y
                self.y = float(self.rect.y)
            
            # Apply horizontal adjustment if needed
            if max_offset_x > 0:
                if self.rect.centerx < aliens_group.sprites()[0].rect.centerx if aliens_group.sprites() else True:
                    self.rect.x -= max_offset_x
                    self.x = float(self.rect.x)
                else:
                    self.rect.x += max_offset_x
                    self.x = float(self.rect.x)
            
            # Final bounds check - ensure never goes above top
            if self.rect.top < 0:
                self.rect.top = 0
                self.y = float(self.rect.y)

    def blitme(self, screen: pygame.Surface):
        """Kirajzolás."""
        screen.blit(self.image, self.rect)
