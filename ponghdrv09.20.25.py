import pygame
from pygame.locals import *
import sys
import array
import os
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ULTRA ! PONG [DEEPSEEK EDITION]")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 150, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)

# Clock for 60 FPS
clock = pygame.time.Clock()

# Leaderboard file
LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pong_leaderboard.txt")

# Paddle class
class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, HEIGHT // 2 - 50, 10, 100)

    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 5, HEIGHT // 2 - 5, 10, 10)
        self.dx = 5
        self.dy = 5

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # Bounce off top/bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy = -self.dy
            bounce_sound.play()

# Sound generation functions
def generate_square_sound(freq, duration=0.1, volume=0.5, sample_rate=44100, duty=0.5):
    num_samples = int(sample_rate * duration)
    period = int(sample_rate / freq)
    high_samples = int(period * duty)
    data = array.array('h', [int(32767 * volume) if (i % period) < high_samples else int(-32767 * volume) for i in range(num_samples)])
    return pygame.mixer.Sound(data)

def generate_triangle_sound(freq, duration=0.1, volume=0.5, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    period_samples = sample_rate / freq
    triangle_steps = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    step_length = period_samples / len(triangle_steps)
    scale = (32767 * volume) / 7.5
    data = array.array('h', [int((triangle_steps[int((i / step_length) % len(triangle_steps))] - 7.5) * scale) for i in range(num_samples)])
    return pygame.mixer.Sound(data)

def generate_noise_sound(freq, duration=0.1, volume=0.5, sample_rate=44100, mode=0):
    num_samples = int(sample_rate * duration)
    period = sample_rate / freq
    lfsr = 1
    clock_counter = 0.0
    max_amp = int(32767 * volume)
    data = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        clock_counter += 1
        if clock_counter >= period:
            clock_counter -= period
            bit0 = lfsr & 1
            if mode == 0:
                bit1 = (lfsr >> 1) & 1
                feedback = bit0 ^ bit1
            else:
                bit6 = (lfsr >> 6) & 1
                feedback = bit0 ^ bit6
            lfsr = (lfsr >> 1) | (feedback << 14)
        data[i] = max_amp if (lfsr & 1) == 0 else -max_amp
    return pygame.mixer.Sound(data)

# Leaderboard functions
def save_to_leaderboard(player_score, opponent_score):
    """Save game result to leaderboard file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        winner = "PLAYER" if player_score > opponent_score else "OPPONENT"
        score_entry = f"{timestamp} | {winner} | Player: {player_score} - Opponent: {opponent_score}\\n"
        
        # Create file if it doesn't exist
        if not os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'w') as f:
                f.write("ULTRA PONG LEADERBOARD\\n")
                f.write("======================\\n\\n")
        
        # Append new entry
        with open(LEADERBOARD_FILE, 'a') as f:
            f.write(score_entry)
    except Exception as e:
        print(f"Error saving to leaderboard: {e}")

def show_leaderboard():
    """Display leaderboard screen"""
    leaderboard_active = True
    
    # Read leaderboard data
    entries = []
    try:
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                entries = f.readlines()[2:]  # Skip header lines
    except Exception as e:
        print(f"Error reading leaderboard: {e}")
    
    while leaderboard_active:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_RETURN:
                    leaderboard_active = False
        
        # Draw leaderboard background
        screen.fill(BLACK)
        
        # Draw title
        title_text = title_font.render("LEADERBOARD", True, YELLOW)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        # Draw entries
        y_pos = 120
        if not entries:
            no_data_text = menu_font.render("No games played yet!", True, WHITE)
            screen.blit(no_data_text, (WIDTH//2 - no_data_text.get_width()//2, 200))
        else:
            # Show last 10 entries
            recent_entries = entries[-10:]
            for entry in recent_entries:
                entry_text = credit_font.render(entry.strip(), True, WHITE)
                screen.blit(entry_text, (WIDTH//2 - entry_text.get_width()//2, y_pos))
                y_pos += 30
        
        # Draw back prompt
        back_text = menu_font.render("Press ENTER or ESC to go back", True, GRAY)
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, 500))
        
        pygame.display.flip()
        clock.tick(60)

# Create sound objects
bounce_sound = generate_triangle_sound(523)
hit_sound = generate_square_sound(659, duty=0.125)
score_sound = generate_noise_sound(1000, duration=0.2, mode=1)

# Fonts
title_font = pygame.font.Font(None, 72)
menu_font = pygame.font.Font(None, 48)
credit_font = pygame.font.Font(None, 24)
score_font = pygame.font.Font(None, 74)
game_over_font = pygame.font.Font(None, 64)

def show_main_menu():
    """Display the main menu and return when user starts the game"""
    menu_active = True
    
    while menu_active:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    menu_active = False
                elif event.key == K_l:  # Press L for leaderboard
                    show_leaderboard()
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Draw menu background
        screen.fill(BLACK)
        
        # Draw title
        title_text = title_font.render("ULTRA ! PONG", True, LIGHT_BLUE)
        subtitle_text = title_font.render("[DEEPSEEK EDITION]", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 170))
        
        # Draw start prompt
        start_text = menu_font.render("PRESS ENTER TO START", True, WHITE)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 300))
        
        # Draw leaderboard prompt
        leaderboard_text = credit_font.render("Press L for Leaderboard", True, GRAY)
        screen.blit(leaderboard_text, (WIDTH//2 - leaderboard_text.get_width()//2, 350))
        
        # Draw credits
        credit1 = credit_font.render("By Team Flames Pong", True, GRAY)
        credit2 = credit_font.render("[C] Atari", True, GRAY)
        screen.blit(credit1, (WIDTH//2 - credit1.get_width()//2, 450))
        screen.blit(credit2, (WIDTH//2 - credit2.get_width()//2, 480))
        
        pygame.display.flip()
        clock.tick(60)

def show_game_over(winner, player_score, opponent_score):
    """Display game over screen and return user choice (True=restart, False=quit)"""
    game_over_active = True
    selected_option = 0  # 0 = Restart, 1 = Quit
    
    # Save to leaderboard
    save_to_leaderboard(player_score, opponent_score)
    
    # Game over sound
    game_over_sound = generate_noise_sound(200, duration=0.5, volume=0.7)
    game_over_sound.play()
    
    while game_over_active:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    selected_option = 1 - selected_option  # Toggle between 0 and 1
                elif event.key == K_RETURN:
                    return selected_option == 0  # True for restart, False for quit
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Draw game over screen
        screen.fill(BLACK)
        
        # Draw game over text
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        winner_text = menu_font.render(f"{winner} WINS!", True, WHITE)
        score_text = menu_font.render(f"Final Score: {player_score} - {opponent_score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 80))
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, 160))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 210))
        
        # Draw options
        restart_color = GREEN if selected_option == 0 else WHITE
        quit_color = GREEN if selected_option == 1 else WHITE
        
        restart_text = menu_font.render("Y - RESTART", True, restart_color)
        quit_text = menu_font.render("N - QUIT", True, quit_color)
        
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2 - 100, 300))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2 + 100, 300))
        
        # Draw selection arrows
        if selected_option == 0:
            pygame.draw.polygon(screen, GREEN, [(WIDTH//2 - 150, 320), (WIDTH//2 - 130, 310), (WIDTH//2 - 130, 330)])
            pygame.draw.polygon(screen, GREEN, [(WIDTH//2 - 50, 320), (WIDTH//2 - 70, 310), (WIDTH//2 - 70, 330)])
        else:
            pygame.draw.polygon(screen, GREEN, [(WIDTH//2 + 150, 320), (WIDTH//2 + 130, 310), (WIDTH//2 + 130, 330)])
            pygame.draw.polygon(screen, GREEN, [(WIDTH//2 + 50, 320), (WIDTH//2 + 70, 310), (WIDTH//2 + 70, 330)])
        
        # Draw instructions
        instructions = credit_font.render("Use LEFT/RIGHT to select, ENTER to confirm", True, GRAY)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, 400))
        
        pygame.display.flip()
        clock.tick(60)

# Show main menu first
show_main_menu()

# Main game function
def main_game():
    # Create game objects
    player = Paddle(20)
    opponent = Paddle(WIDTH - 30)
    ball = Ball()

    # Scores
    player_score = 0
    opponent_score = 0

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Player input
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            player.move(-5)
        if keys[K_s]:
            player.move(5)

        # Simple AI for opponent
        if opponent.rect.centery < ball.rect.centery:
            opponent.move(5)
        elif opponent.rect.centery > ball.rect.centery:
            opponent.move(-5)

        # Move ball
        ball.move()

        # Ball-paddle collisions
        if ball.rect.colliderect(player.rect) or ball.rect.colliderect(opponent.rect):
            ball.dx = -ball.dx
            hit_sound.play()

        # Scoring
        if ball.rect.left <= 0:
            opponent_score += 1
            score_sound.play()
            ball = Ball()  # Reset ball
        if ball.rect.right >= WIDTH:
            player_score += 1
            score_sound.play()
            ball = Ball()  # Reset ball

        # Check for game over
        if player_score >= 5 or opponent_score >= 5:
            winner = "PLAYER" if player_score >= 5 else "OPPONENT"
            return show_game_over(winner, player_score, opponent_score)

        # Drawing
        screen.fill(BLACK)
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, player.rect)
        pygame.draw.rect(screen, WHITE, opponent.rect)
        pygame.draw.ellipse(screen, WHITE, ball.rect)
        # Draw center line (dashed)
        for i in range(10, HEIGHT, 20):
            pygame.draw.line(screen, WHITE, (WIDTH // 2, i), (WIDTH // 2, i + 10), 5)
        # Draw scores
        player_text = score_font.render(str(player_score), True, WHITE)
        screen.blit(player_text, (WIDTH // 4, 20))
        opponent_text = score_font.render(str(opponent_score), True, WHITE)
        screen.blit(opponent_text, (WIDTH * 3 // 4, 20))

        pygame.display.flip()
        clock.tick(60)

# Game loop with restart functionality
while True:
    restart = main_game()
    if not restart:
        break

pygame.quit()
sys.exit()
