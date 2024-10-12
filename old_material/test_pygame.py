import pygame
import sys
import nilearn

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving Rectangle")

# Set up colors
black = (0, 0, 0)
red = (255, 0, 0)

# Set up rectangle properties
rect_x, rect_y = 50, 50
rect_width, rect_height = 60, 40
rect_speed = 5

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move rectangle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rect_x -= rect_speed
    if keys[pygame.K_RIGHT]:
        rect_x += rect_speed
    if keys[pygame.K_UP]:
        rect_y -= rect_speed
    if keys[pygame.K_DOWN]:
        rect_y += rect_speed

    # Fill the screen with black
    screen.fill(black)

    # Draw the rectangle
    pygame.draw.rect(screen, red, (rect_x, rect_y, rect_width, rect_height))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

