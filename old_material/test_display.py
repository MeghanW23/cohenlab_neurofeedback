import pygame
import os

def main():
    pygame.init()

    # Set environment variable for window position
    os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"

    # Set the display mode to FULLSCREEN for testing
    screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
    pygame.display.set_caption("Fullscreen Test")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with a color
        screen.fill((0, 128, 255))

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
