import pygame
from pygame import mixer
import math
import random
import sys

width = 800
height = 600
fps = 60
block = 20

# colors
black = (0, 0, 0)
green = (0, 255, 0)  # snek boi
hed_green = (0, 150, 0) #snek boi hed
gray = (128, 128, 128)  # ratz
yellow = (255, 255, 0)  # wildcard
blue = (0, 0, 255)  # speeeeeed
purple = (255, 0, 255)  # sloooooow
red = (255, 0, 0)  # blood + game over
white = (255, 255, 255)  # text

pygame.init()
mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snek (bom om like snek game)")
clock = pygame.time.Clock()

#sounds
background = "background_music.mp3"
death = mixer.Sound("hiss.mp3")

flip = False

def reset():
    mixer.music.load(background)
    mixer.music.play(-1)
    global flip
    flip = False
    return {
        "snake_history": [(width // 2, height // 2)],
        "snake_length": 4,
        "rats eaten": 0,
        "base_rat_fast": 2,
        "rats": [],
        "die?": False,
        "die_pos": None,
        "message": "",
        "message_timer": 0,
        "message_color": purple,
        "rush_timer": 0,
        "calm_timer": 0
    }

game = reset()

while True:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mixer.music.stop()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN and game["die?"]:
            game = reset()

    if not game["die?"]:

        if game["rush_timer"] > 0:
            game["rush_timer"] -= 1

        if game["calm_timer"] > 0:
            game["calm_timer"] -= 1

        is_rush_active = game["rush_timer"] > 0
        is_calm_active = game["calm_timer"] > 0

        mx, my = pygame.mouse.get_pos()
        if flip:
            mouse_x = width - mx
            mouse_y = height - my
        else:
            mouse_x, mouse_y = mx, my
        
        hed_x, hed_y = game["snake_history"][0]

        dirToX = mouse_x - hed_x
        dirToY = mouse_y - hed_y
        distance = math.hypot(dirToX, dirToY)

        snake_fast = 10 if is_rush_active else 5
        
        if distance > snake_fast:
            hed_x += dirToX / distance * snake_fast
            hed_y += dirToY / distance * snake_fast
        else:
            hed_x = mouse_x
            hed_y = mouse_y

        game["snake_history"].insert(0, (hed_x, hed_y))
        if len(game["snake_history"]) > game["snake_length"] * 4:
            game["snake_history"].pop()

        if random.random() < 0.03:  # 3% a frame ie 72 % a second.
            
            # Make sure a rat is only ONE type of power-up {AI assistance needed(im dum lol)}
            rat_type_roll = random.random()
            is_wildcard = False
            is_rush = False
            is_calm = False

            if rat_type_roll < 0.005:
                is_wildcard = True
            elif rat_type_roll < 0.02:
                is_rush = True
            elif rat_type_roll < 0.035:
                is_calm = True

            side = random.randint(0, 3)
            rat_fast = game["base_rat_fast"] + (game["rats eaten"] // 10)
            
            if side == 0:
                x = random.randint(0, width)
                y = -block
                vx = 0
                vy = rat_fast
            elif side == 1:
                x = random.randint(0, width)
                y = height + block
                vx = 0
                vy = -rat_fast
            elif side == 2:
                x = -block
                y = random.randint(0, height)
                vx = rat_fast
                vy = 0
            else:
                x = width + block
                y = random.randint(0, height)
                vx = -rat_fast
                vy = 0

            game["rats"].append({
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "is_wildcard": is_wildcard,
                "is_rush": is_rush,
                "is_calm": is_calm
            })

        hed_rect = pygame.Rect(hed_x - block/2, hed_y - block/2, block, block)
        
        alive_rats = []
        for rat in game["rats"]:
            speed_mult = 0.5 if is_calm_active else 1.0
            
            rat["x"] += rat["vx"] * speed_mult
            rat["y"] += rat["vy"] * speed_mult

            rat_rect = pygame.Rect(rat["x"] - block / 2, rat["y"] - block / 2, block, block)
            
            if hed_rect.colliderect(rat_rect):
                if rat["is_wildcard"]:
                    flip = not flip
                    game["message"] = "MOVEMENT FLIPPED!" if flip else "MOVEMENT RESTORED!"
                    game["message_timer"] = fps * 2
                    game["message_color"] = yellow
                elif rat["is_rush"]:
                    game["rush_timer"] = fps * 4
                    game["message"] = "SPEED BOOST!"
                    game["message_timer"] = fps * 2
                    game["message_color"] = blue
                elif rat["is_calm"]:
                    game["calm_timer"] = fps * 4
                    game["message"] = "take a break :)"
                    game["message_timer"] = fps * 2
                    game["message_color"] = purple
                else:
                    game["snake_length"] += 1
                    game["rats eaten"] += 1
                continue

            hit_body = False
            for x in range(4, len(game["snake_history"]), 4):
                bx, by = game["snake_history"][x]
                body_rect = pygame.Rect(bx - block/2, by - block/2, block, block)
                if body_rect.colliderect(rat_rect):
                    if not (rat["is_wildcard"] or rat["is_rush"] or rat["is_calm"]):
                        hit_body = True
                        game["die_pos"] = (rat["x"], rat["y"])
                    break

            if hit_body:
                game["die?"] = True
                mixer.music.stop()
                death.play(0)
                break

            if -50 < rat["x"] < width + 50 and -50 < rat["y"] < height + 50:
                alive_rats.append(rat)

        if not game["die?"]:
            game["rats"] = alive_rats

    for rat in game["rats"]:
        color = yellow if rat["is_wildcard"] else blue if rat["is_rush"] else purple if rat["is_calm"] else gray
        pygame.draw.rect(screen, color, (rat["x"] - block / 2, rat["y"] - block / 2, block, block))

    for i in range(0, len(game["snake_history"]), 4):
        sx, sy = game["snake_history"][i]
        if i == 0:
            tcolor = hed_green
            size = block + 4
        else:
            tcolor = green
            size = block
        pygame.draw.rect(screen, tcolor, (sx - size / 2, sy - size / 2, size, size))

    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Rats Eaten: {game["rats eaten"]} || Speed: {game["base_rat_fast"] + (game["rats eaten"] // 10)}', True, red)
    screen.blit(score_text, (10, 10))

    if game["message_timer"] > 0:
        game["message_timer"] -= 1

        funky_font = pygame.font.SysFont("comicsansms", 48, bold=True)
        msg_surf = funky_font.render(game["message"], True, game["message_color"])
        
        # Mirror the text horizontally {AI USAGE}
        if flip:
            msg_surf = pygame.transform.flip(msg_surf, True, False) 
        screen.blit(msg_surf, (width // 2 - msg_surf.get_width() // 2, 100))

    # Draw Game Over and Blood {AI USAGE}
    if game["die?"]:
        # Draw Blood Spatter at death position
        if game["die_pos"]:
            dx, dy = game["die_pos"]
            pygame.draw.circle(screen, red, (dx, dy), 15)
            pygame.draw.circle(screen, red, (dx + 12, dy - 10), 10)
            pygame.draw.circle(screen, red, (dx - 10, dy + 8), 12)
            pygame.draw.circle(screen, red, (dx - 15, dy - 12), 6)
            pygame.draw.circle(screen, red, (dx + 5, dy + 15), 8)

        die_txt = font.render("GAME OVER!", True, red)
        restart_txt = font.render("(press any key to restart)", True, white)
        screen.blit(die_txt, (width // 2 - die_txt.get_width() // 2, height // 2 - die_txt.get_height() // 2))
        screen.blit(restart_txt, (width // 2 - restart_txt.get_width() // 2, height // 2 + die_txt.get_height() // 2))

    pygame.display.flip()
    clock.tick(fps)