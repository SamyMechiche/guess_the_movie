import pygame
import requests
import random
from io import BytesIO
import os
import time
import numpy as np

# === CONFIG API ===
API_KEY = "7b895c57ad4a9fa9c3370916ea93fc2f"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3Yjg5NWM1N2FkNGE5ZmE5YzMzNzA5MTZlYTkzZmMyZiIsIm5iZiI6MTYyNDM2NTY2MC42NzkwMDAxLCJzdWIiOiI2MGQxZGE1YzIyOWFlMjAwNzNlYTk5MTkiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WXXc0qzMfJmcXWO2pWma5KxTVZfjCRclw7DvBCOX8EI"
}

# === INIT PYGAME ===
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Initialize sound mixer with specific parameters
largeur, hauteur = 1200, 800  # Increased window size
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Devine le Film")

# === SOUND EFFECTS ===
try:
    # Create sounds directory if it doesn't exist
    if not os.path.exists("assets/sounds"):
        os.makedirs("assets/sounds")

    # Load or create sound effects
    try:
        correct_sound = pygame.mixer.Sound("assets/sounds/correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/wrong.wav")
        hint_sound = pygame.mixer.Sound("assets/sounds/hint.wav")
        button_sound = pygame.mixer.Sound("assets/sounds/button.wav")
        reveal_sound = pygame.mixer.Sound("assets/sounds/reveal.wav")
        timer_sound = pygame.mixer.Sound("assets/sounds/timer.wav")
    except:
        # Create simple sound effects if files don't exist
        def create_beep_sound(frequency, duration):
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
            for s in range(n_samples):
                t = float(s) / sample_rate
                buf[s][0] = int(32767.0 * math.sin(2.0 * math.pi * frequency * t))
                buf[s][1] = int(32767.0 * math.sin(2.0 * math.pi * frequency * t))
            return pygame.sndarray.make_sound(buf)


        import numpy
        import math

        correct_sound = create_beep_sound(880, 0.2)  # High pitch for correct
        wrong_sound = create_beep_sound(220, 0.3)  # Low pitch for wrong
        hint_sound = create_beep_sound(440, 0.1)  # Medium pitch for hint
        button_sound = create_beep_sound(660, 0.1)  # Medium-high pitch for button
        reveal_sound = create_beep_sound(550, 0.15)  # Medium pitch for reveal
        timer_sound = create_beep_sound(330, 0.5)  # Low pitch for timer

        # Save the generated sounds
        pygame.mixer.Sound.save(correct_sound, "assets/sounds/correct.wav")
        pygame.mixer.Sound.save(wrong_sound, "assets/sounds/wrong.wav")
        pygame.mixer.Sound.save(hint_sound, "assets/sounds/hint.wav")
        pygame.mixer.Sound.save(button_sound, "assets/sounds/button.wav")
        pygame.mixer.Sound.save(reveal_sound, "assets/sounds/reveal.wav")
        pygame.mixer.Sound.save(timer_sound, "assets/sounds/timer.wav")

        # Reload the saved sounds
        correct_sound = pygame.mixer.Sound("assets/sounds/correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/wrong.wav")
        hint_sound = pygame.mixer.Sound("assets/sounds/hint.wav")
        button_sound = pygame.mixer.Sound("assets/sounds/button.wav")
        reveal_sound = pygame.mixer.Sound("assets/sounds/reveal.wav")
        timer_sound = pygame.mixer.Sound("assets/sounds/timer.wav")
except Exception as e:
    print(f"Error initializing sounds: {e}")


    # Fallback if sound system fails
    class DummySound:
        def play(self): pass


    correct_sound = wrong_sound = hint_sound = button_sound = reveal_sound = timer_sound = DummySound()

# Set sound volume
if isinstance(correct_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(correct_sound, 0.7)  # Increased volume
if isinstance(wrong_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(wrong_sound, 0.7)  # Increased volume
if isinstance(hint_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(hint_sound, 0.7)  # Increased volume
if isinstance(button_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(button_sound, 0.7)  # Increased volume
if isinstance(reveal_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(reveal_sound, 0.7)  # Increased volume
if isinstance(timer_sound, pygame.mixer.Sound):
    pygame.mixer.Sound.set_volume(timer_sound, 0.7)  # Increased volume

# === COULEURS ===
NOIR = (15, 15, 20)
BLANC = (240, 240, 240)
VERT = (46, 204, 113)
ROUGE = (231, 76, 60)
BLEU_CIEL = (52, 152, 219)
VIOLET = (155, 89, 182)
ORANGE = (230, 126, 34)
GRIS_FONCE = (50, 50, 60)
GRIS_CLAIR = (100, 100, 110)

# Dégradé de fond
COULEUR_FOND_HAUT = (30, 30, 40)
COULEUR_FOND_BAS = (20, 20, 30)

# === POLICES ===
try:
    font_medium = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 32)
    font_bold = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 40)
    font_light = pygame.font.Font("assets/fonts/Roboto-Light.ttf", 28)
    font_title = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 48)
except:
    # Fallback si les polices ne sont pas trouvées
    font_medium = pygame.font.SysFont("arial", 32, bold=True)
    font_bold = pygame.font.SysFont("arial", 40, bold=True)
    font_light = pygame.font.SysFont("arial", 28)
    font_title = pygame.font.SysFont("arial", 48, bold=True)

# === CONFIG ===
min_res = 10
max_res = 300
image_pos = (largeur // 2 - 300 // 2, 150)  # Centered horizontally, moved down
image_size = (300, 450)

# Difficulty settings
DIFFICULTY_SPEEDS = {
    "easy": 0.2,
    "medium": 0.1,
    "hard": 0.05
}

# === GAME STATE ===
movie = None
last_movie = None
user_input = ""
current_res = min_res
revealing = True
typing_started = False
error_pause_timer = 0
result_surface = font_medium.render("", True, BLANC)
result_surfaces = None
result_color = BLANC
current_player = None
players = []
player_count = 0
current_difficulty = "medium"
reveal_speed = DIFFICULTY_SPEEDS[current_difficulty]
hints_used = 0
max_hints = 3
start_time = 0
fully_revealed_time = 0
fully_revealed = False
current_round = 1
max_rounds = 10
player_streaks = {}  # Track consecutive correct guesses
skip_available = True  # Allow one skip per round
last_movie_display = None
last_movie_timer = 0
game_paused = False  # New game state for pause

# Filter settings
current_filters = {
    "year": None,  # e.g., "2020"
    "genre": None,  # e.g., "Action"
    "director": None,  # e.g., "Christopher Nolan"
    "rating": None  # e.g., "7.5"
}


# === PARTICLE SYSTEM ===
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)
        self.alpha = 255

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.alpha = int(255 * (self.life / 40))
        return self.life > 0

    def draw(self, surface):
        color = (*self.color[:3], self.alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.surface = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)

    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.surface.fill((0, 0, 0, 0))
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(self.surface)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))

# === TEXT RENDERING ===
class TextCache:
    def __init__(self):
        self.cache = {}

    def get_text(self, text, font, color):
        key = (text, font, color)
        if key not in self.cache:
            self.cache[key] = font.render(text, True, color)
        return self.cache[key]

text_cache = TextCache()

def draw_text(text, font, color, x, y, centered=True):
    surface = text_cache.get_text(text, font, color)
    rect = surface.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    fenetre.blit(surface, rect)
    return rect


# === FONCTIONS ===
def get_random_movie_poster():
    # Build the API URL with filters
    url = f"{BASE_URL}/discover/movie?"

    # Add filters to the URL
    params = []
    if current_filters["year"]:
        params.append(f"primary_release_year={current_filters['year']}")
    if current_filters["genre"]:
        # First, get the genre ID
        genre_url = f"{BASE_URL}/genre/movie/list"
        genre_response = requests.get(genre_url, headers=HEADERS)
        if genre_response.status_code == 200:
            genres = genre_response.json().get("genres", [])
            for genre in genres:
                if genre["name"].lower() == current_filters["genre"].lower():
                    params.append(f"with_genres={genre['id']}")
                    break
    if current_filters["rating"]:
        params.append(f"vote_average.gte={current_filters['rating']}")

    # Add random page
    params.append(f"page={random.randint(1, 10)}")

    # Combine all parameters
    url += "&".join(params)

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        movies = response.json().get("results", [])
        if movies:
            movie = random.choice(movies)
            title = movie.get("title", "Titre inconnu")
            poster_path = movie.get("poster_path")
            overview = movie.get("overview", "Pas de description disponible")
            release_date = movie.get("release_date", "Date inconnue")
            rating = movie.get("vote_average", 0)

            # Get director information if filter is active
            if current_filters["director"]:
                credits_url = f"{BASE_URL}/movie/{movie['id']}/credits"
                credits_response = requests.get(credits_url, headers=HEADERS)
                if credits_response.status_code == 200:
                    crew = credits_response.json().get("crew", [])
                    directors = [person["name"] for person in crew if person["job"] == "Director"]
                    if not any(d.lower() == current_filters["director"].lower() for d in directors):
                        return get_random_movie_poster()  # Try again if director doesn't match

            if poster_path:
                img_url = IMAGE_BASE_URL + poster_path
                img_data = requests.get(img_url)
                if img_data.status_code == 200:
                    image = pygame.image.load(BytesIO(img_data.content))
                    return {
                        "title": title,
                        "image": image,
                        "overview": overview,
                        "release_date": release_date,
                        "rating": rating
                    }
    return None


def reset_game():
    global movie, last_movie, user_input, result_surface, result_surfaces, result_color, current_res, revealing, typing_started, current_player, particles, hints_used, start_time, fully_revealed_time, fully_revealed, skip_available, last_movie_display, last_movie_timer, current_round
    if current_round > max_rounds:
        show_game_over()
        return

    if movie:
        last_movie = movie
        last_movie_display = {
            "title": last_movie["title"],
            "year": last_movie["release_date"][:4],
            "timer": pygame.time.get_ticks() + 5000  # Show for 5 seconds
        }
    movie = get_random_movie_poster()
    user_input = ""
    result_surface = font_medium.render("", True, BLANC)
    result_surfaces = None
    result_color = BLANC
    current_res = min_res
    revealing = True
    typing_started = False
    current_player = None
    particles = []
    hints_used = 0
    skip_available = True
    start_time = pygame.time.get_ticks()
    fully_revealed_time = 0
    fully_revealed = False


def draw_button(rect, text, color, hover_color=None, text_color=None):
    if hover_color is None:
        hover_color = get_button_hover_color(color)
    if text_color is None:
        text_color = get_theme_color("text")
    
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(fenetre, button_color, rect, border_radius=8)
    pygame.draw.rect(fenetre, (0, 0, 0, 30), rect, 2, border_radius=8)
    
    text_surface = font_medium.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    fenetre.blit(text_surface, text_rect)
    
    return is_hovered


def draw_input_box(rect, text, active, max_width=None):
    color = BLEU_CIEL if active else GRIS_FONCE
    pygame.draw.rect(fenetre, color, rect, border_radius=6)
    pygame.draw.rect(fenetre, (0, 0, 0, 30), rect, 2, border_radius=6)

    text_surf = font_light.render(text, True, BLANC)

    if max_width and text_surf.get_width() > max_width:
        # Couper le texte avec "..." si trop long
        while text_surf.get_width() > max_width - 30 and len(text) > 3:
            text = text[:-1]
            text_surf = font_light.render(text + "...", True, BLANC)

    text_rect = text_surf.get_rect(midleft=(rect.x + 10, rect.centery))
    fenetre.blit(text_surf, text_rect)


def select_player_count():
    button_width = 300
    button_height = 60
    button_spacing = 20
    total_height = (button_height * 3) + (button_spacing * 2)  # 3 buttons with 2 spaces
    start_y = (hauteur - total_height) // 2  # Center vertically

    btns = [
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y, button_width, button_height), 
         "text": "1 joueur", "value": 1, "color": VIOLET},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height), 
         "text": "2 joueurs", "value": 2, "color": BLEU_CIEL},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + (button_height + button_spacing) * 2, button_width, button_height), 
         "text": "3 joueurs", "value": 3, "color": ORANGE},
    ]

    while True:
        # Dégradé de fond
        fenetre.fill(COULEUR_FOND_HAUT)
        pygame.draw.rect(fenetre, COULEUR_FOND_BAS, (0, hauteur // 2, largeur, hauteur // 2))

        # Titre
        title = font_title.render("Devine le Film", True, BLANC)
        title_y = start_y - 100  # Position title above the buttons
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, title_y))

        subtitle = font_light.render("Choisis le nombre de joueurs :", True, GRIS_CLAIR)
        subtitle_y = title_y + title.get_height() + 20
        fenetre.blit(subtitle, (largeur // 2 - subtitle.get_width() // 2, subtitle_y))

        # Boutons
        for btn in btns:
            draw_button(btn["rect"], btn["text"], btn["color"], 
                       (min(btn["color"][0] + 30, 255), min(btn["color"][1] + 30, 255), min(btn["color"][2] + 30, 255)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in btns:
                    if btn["rect"].collidepoint(event.pos):
                        return btn["value"]


def setup_players(nb_players):
    input_active = [False] * nb_players
    names = ["" for _ in range(nb_players)]
    keys = ["" for _ in range(nb_players)]
    current_index = 0

    colors = [VIOLET, BLEU_CIEL, ORANGE]
    
    # Calculate positions for centered layout
    input_width = 400
    key_width = 80
    total_width = input_width + 20 + key_width
    input_height = 50
    spacing = 20
    total_height = (input_height * nb_players) + (spacing * (nb_players - 1))
    start_y = (hauteur - total_height) // 2

    input_rects = [pygame.Rect((largeur - total_width) // 2, start_y + i * (input_height + spacing), input_width, input_height) 
                  for i in range(nb_players)]
    key_rects = [pygame.Rect((largeur - total_width) // 2 + input_width + 20, start_y + i * (input_height + spacing), key_width, input_height) 
                for i in range(nb_players)]
    
    button_width = 300
    button_height = 60
    start_button_rect = pygame.Rect((largeur - button_width) // 2, start_y + total_height + 50, button_width, button_height)

    while True:
        # Dégradé de fond
        fenetre.fill(COULEUR_FOND_HAUT)
        pygame.draw.rect(fenetre, COULEUR_FOND_BAS, (0, hauteur // 2, largeur, hauteur // 2))

        # Titre
        title = font_title.render("Configuration", True, BLANC)
        title_y = start_y - 100
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, title_y))

        subtitle = font_light.render("Entrez les noms et touches des joueurs", True, GRIS_CLAIR)
        subtitle_y = title_y + title.get_height() + 20
        fenetre.blit(subtitle, (largeur // 2 - subtitle.get_width() // 2, subtitle_y))

        for i in range(nb_players):
            # Label joueur
            label = font_light.render(f"Joueur {i + 1}:", True, BLANC)
            label_x = (largeur - total_width) // 2 - label.get_width() - 20
            fenetre.blit(label, (label_x, start_y + i * (input_height + spacing) + 15))

            # Champ nom
            draw_input_box(input_rects[i], names[i], input_active[i], 380)

            # Champ touche
            pygame.draw.rect(fenetre, colors[i], key_rects[i], border_radius=6)
            pygame.draw.rect(fenetre, (0, 0, 0, 30), key_rects[i], 2, border_radius=6)
            key_surface = font_bold.render(keys[i].upper() if keys[i] else "?", True, BLANC)
            fenetre.blit(key_surface, (
                key_rects[i].centerx - key_surface.get_width() // 2,
                key_rects[i].centery - key_surface.get_height() // 2))

        # Bouton commencer
        can_start = all(names) and all(keys)
        btn_color = VERT if can_start else GRIS_FONCE
        hover_color = (min(btn_color[0] + 30, 255), min(btn_color[1] + 30, 255), min(btn_color[2] + 30, 255))

        if draw_button(start_button_rect, "COMMENCER", btn_color, hover_color if can_start else btn_color):
            pass  # Juste pour l'affichage

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(nb_players):
                    if input_rects[i].collidepoint(event.pos):
                        input_active = [j == i for j in range(nb_players)]
                        current_index = i
                    elif key_rects[i].collidepoint(event.pos):
                        keys[i] = ""
                        input_active = [False] * nb_players
                        current_index = -1
                if start_button_rect.collidepoint(event.pos) and can_start:
                    return [{"name": names[i], "key": keys[i], "score": 0, "color": colors[i]} for i
                            in range(nb_players)]

            elif event.type == pygame.KEYDOWN:
                if current_index != -1:
                    if event.key == pygame.K_RETURN:
                        input_active[current_index] = False
                        current_index = -1
                    elif event.key == pygame.K_BACKSPACE:
                        names[current_index] = names[current_index][:-1]
                    else:
                        if len(names[current_index]) < 15:  # Limite de caractères
                            names[current_index] += event.unicode
                else:
                    for i in range(nb_players):
                        if keys[i] == "" and event.key not in [pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_ESCAPE]:
                            keys[i] = pygame.key.name(event.key)


def select_difficulty():
    button_width = 300
    button_height = 60
    button_spacing = 20
    total_height = (button_height * 3) + (button_spacing * 2)  # 3 buttons with 2 spaces
    start_y = (hauteur - total_height) // 2  # Center vertically

    btns = [
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y, button_width, button_height), 
         "text": "Facile", "value": "easy", "color": VERT},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height), 
         "text": "Moyen", "value": "medium", "color": ORANGE},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + (button_height + button_spacing) * 2, button_width, button_height), 
         "text": "Difficile", "value": "hard", "color": ROUGE},
    ]

    while True:
        # Dégradé de fond
        fenetre.fill(COULEUR_FOND_HAUT)
        pygame.draw.rect(fenetre, COULEUR_FOND_BAS, (0, hauteur // 2, largeur, hauteur // 2))

        # Titre
        title = font_title.render("Niveau de Difficulté", True, BLANC)
        title_y = start_y - 100  # Position title above the buttons
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, title_y))

        subtitle = font_light.render("Choisis la difficulté :", True, GRIS_CLAIR)
        subtitle_y = title_y + title.get_height() + 20
        fenetre.blit(subtitle, (largeur // 2 - subtitle.get_width() // 2, subtitle_y))

        # Boutons
        for btn in btns:
            draw_button(btn["rect"], btn["text"], btn["color"], 
                       (min(btn["color"][0] + 30, 255), min(btn["color"][1] + 30, 255), min(btn["color"][2] + 30, 255)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in btns:
                    if btn["rect"].collidepoint(event.pos):
                        return btn["value"]


def select_filters():
    global current_filters

    # Calculate positions for centered layout
    input_width = 300
    input_height = 40
    spacing = 20
    total_height = (input_height * 4) + (spacing * 3)  # 4 inputs with 3 spaces
    start_y = (hauteur - total_height) // 2

    # Input fields
    year_input = ""
    genre_input = ""
    director_input = ""
    rating_input = ""
    active_input = None  # None, "year", "genre", "director", "rating"

    # Input rectangles
    year_rect = pygame.Rect((largeur - input_width) // 2, start_y, input_width, input_height)
    genre_rect = pygame.Rect((largeur - input_width) // 2, start_y + input_height + spacing, input_width, input_height)
    director_rect = pygame.Rect((largeur - input_width) // 2, start_y + (input_height + spacing) * 2, input_width, input_height)
    rating_rect = pygame.Rect((largeur - input_width) // 2, start_y + (input_height + spacing) * 3, input_width, input_height)

    # Buttons
    button_width = 300
    button_height = 60
    button_spacing = 20
    apply_button = pygame.Rect((largeur - button_width) // 2, start_y + total_height + 50, button_width, button_height)
    skip_button = pygame.Rect((largeur - button_width) // 2, start_y + total_height + 50 + button_height + button_spacing, button_width, button_height)

    while True:
        # Dégradé de fond
        fenetre.fill(COULEUR_FOND_HAUT)
        pygame.draw.rect(fenetre, COULEUR_FOND_BAS, (0, hauteur // 2, largeur, hauteur // 2))

        # Titre
        title = font_title.render("Filtres de Films", True, BLANC)
        title_y = start_y - 100
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, title_y))

        subtitle = font_light.render("Choisissez vos filtres (optionnel)", True, GRIS_CLAIR)
        subtitle_y = title_y + title.get_height() + 20
        fenetre.blit(subtitle, (largeur // 2 - subtitle.get_width() // 2, subtitle_y))

        # Labels
        year_label = font_medium.render("Année:", True, BLANC)
        genre_label = font_medium.render("Genre:", True, BLANC)
        director_label = font_medium.render("Réalisateur:", True, BLANC)
        rating_label = font_medium.render("Note minimale (0-10):", True, BLANC)

        label_x = (largeur - input_width) // 2 - 150  # Position labels to the left of inputs

        fenetre.blit(year_label, (label_x, start_y + 5))
        fenetre.blit(genre_label, (label_x, start_y + input_height + spacing + 5))
        fenetre.blit(director_label, (label_x, start_y + (input_height + spacing) * 2 + 5))
        fenetre.blit(rating_label, (label_x, start_y + (input_height + spacing) * 3 + 5))

        # Draw input boxes
        draw_input_box(year_rect, year_input, active_input == "year", 280)
        draw_input_box(genre_rect, genre_input, active_input == "genre", 280)
        draw_input_box(director_rect, director_input, active_input == "director", 280)
        draw_input_box(rating_rect, rating_input, active_input == "rating", 280)

        # Buttons
        draw_button(apply_button, "APPLIQUER", VERT,
                    (min(VERT[0] + 30, 255), min(VERT[1] + 30, 255), min(VERT[2] + 30, 255)))
        draw_button(skip_button, "PASSER", GRIS_FONCE,
                    (min(GRIS_FONCE[0] + 30, 255), min(GRIS_FONCE[1] + 30, 255), min(GRIS_FONCE[2] + 30, 255)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if year_rect.collidepoint(event.pos):
                    active_input = "year"
                elif genre_rect.collidepoint(event.pos):
                    active_input = "genre"
                elif director_rect.collidepoint(event.pos):
                    active_input = "director"
                elif rating_rect.collidepoint(event.pos):
                    active_input = "rating"
                elif apply_button.collidepoint(event.pos):
                    current_filters = {
                        "year": year_input if year_input else None,
                        "genre": genre_input if genre_input else None,
                        "director": director_input if director_input else None,
                        "rating": rating_input if rating_input else None
                    }
                    return
                elif skip_button.collidepoint(event.pos):
                    current_filters = {"year": None, "genre": None, "director": None, "rating": None}
                    return
            elif event.type == pygame.KEYDOWN:
                if active_input == "year":
                    if event.key == pygame.K_BACKSPACE:
                        year_input = year_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = None
                    elif event.unicode.isdigit() and len(year_input) < 4:
                        year_input += event.unicode
                elif active_input == "genre":
                    if event.key == pygame.K_BACKSPACE:
                        genre_input = genre_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = None
                    else:
                        genre_input += event.unicode
                elif active_input == "director":
                    if event.key == pygame.K_BACKSPACE:
                        director_input = director_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = None
                    else:
                        director_input += event.unicode
                elif active_input == "rating":
                    if event.key == pygame.K_BACKSPACE:
                        rating_input = rating_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = None
                    elif event.unicode.isdigit() or (event.unicode == "." and "." not in rating_input):
                        if len(rating_input) < 4:  # Allow up to 3 digits (e.g., "10.0")
                            rating_input += event.unicode


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def draw_hint_text(text, color=BLEU_CIEL):
    # Calculate the maximum width for the hint text
    max_width = largeur - 100  # Leave some margin on both sides

    # Wrap the text
    wrapped_lines = wrap_text(text, font_light, max_width)

    # Calculate total height needed
    line_height = font_light.get_height()
    total_height = len(wrapped_lines) * line_height

    # Calculate starting y position to center the text
    start_y = hauteur - total_height - 20  # 20 pixels from bottom

    # Draw each line
    for i, line in enumerate(wrapped_lines):
        text_surface = font_light.render(line, True, color)
        text_rect = text_surface.get_rect(centerx=largeur // 2, y=start_y + i * line_height)
        fenetre.blit(text_surface, text_rect)


# === THEMES ===
THEMES = {
    "dark": {
        "background_top": (30, 30, 40),
        "background_bottom": (20, 20, 30),
        "text": (240, 240, 240),
        "button": (155, 89, 182),
        "correct": (46, 204, 113),
        "wrong": (231, 76, 60),
        "hint": (52, 152, 219)
    },
    "light": {
        "background_top": (240, 240, 240),
        "background_bottom": (220, 220, 230),
        "text": (30, 30, 40),
        "button": (142, 68, 173),
        "correct": (39, 174, 96),
        "wrong": (192, 57, 43),
        "hint": (41, 128, 185)
    },
    "retro": {
        "background_top": (0, 0, 0),
        "background_bottom": (20, 20, 20),
        "text": (0, 255, 0),
        "button": (255, 0, 0),
        "correct": (0, 255, 0),
        "wrong": (255, 0, 0),
        "hint": (0, 0, 255)
    }
}

def get_theme_color(color_name):
    return THEMES[current_theme].get(color_name, THEMES["dark"][color_name])

def get_button_hover_color(color):
    return tuple(min(c + 30, 255) for c in color)

current_theme = "dark"  # Default theme

def select_theme():
    global current_theme
    theme_buttons = [
        {"rect": pygame.Rect(350, 250, 300, 60), "text": "Dark Mode", "value": "dark", "color": (30, 30, 40)},
        {"rect": pygame.Rect(350, 350, 300, 60), "text": "Light Mode", "value": "light", "color": (240, 240, 240)},
        {"rect": pygame.Rect(350, 450, 300, 60), "text": "Retro Mode", "value": "retro", "color": (0, 0, 0)}
    ]

    while True:
        fenetre.fill(THEMES[current_theme]["background_top"])
        pygame.draw.rect(fenetre, THEMES[current_theme]["background_bottom"], (0, hauteur // 2, largeur, hauteur // 2))

        title = font_title.render("Select Theme", True, THEMES[current_theme]["text"])
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, 100))

        for btn in theme_buttons:
            draw_button(btn["rect"], btn["text"], btn["color"], 
                       (min(btn["color"][0] + 30, 255), min(btn["color"][1] + 30, 255), min(btn["color"][2] + 30, 255)),
                       THEMES[current_theme]["text"])

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in theme_buttons:
                    if btn["rect"].collidepoint(event.pos):
                        current_theme = btn["value"]
                        return

# === PLAYER TURN INDICATOR ===
class TurnIndicator:
    def __init__(self):
        self.pulse_radius = 0
        self.pulse_growing = True
        self.max_radius = 20
        self.pulse_speed = 0.5

    def update(self):
        if self.pulse_growing:
            self.pulse_radius += self.pulse_speed
            if self.pulse_radius >= self.max_radius:
                self.pulse_growing = False
        else:
            self.pulse_radius -= self.pulse_speed
            if self.pulse_radius <= 0:
                self.pulse_growing = True

    def draw(self, surface, player):
        if not current_player:
            return
            
        # Draw pulsing circle around player's score
        center_x = 800
        center_y = 100 + players.index(player) * 50 + 20
        pygame.draw.circle(surface, player['color'], (center_x, center_y), 
                         int(self.pulse_radius), 2)

turn_indicator = TurnIndicator()

# === MOVIE INFORMATION DISPLAY ===
def show_movie_info(movie_data):
    info_surface = pygame.Surface((400, 300))
    info_surface.fill(THEMES[current_theme]["background_top"])
    
    # Title
    title = font_bold.render(movie_data["title"], True, THEMES[current_theme]["text"])
    info_surface.blit(title, (20, 20))
    
    # Year
    year = font_medium.render(f"Year: {movie_data['release_date'][:4]}", True, THEMES[current_theme]["text"])
    info_surface.blit(year, (20, 70))
    
    # Rating
    rating = font_medium.render(f"Rating: {movie_data['rating']}/10", True, THEMES[current_theme]["text"])
    info_surface.blit(rating, (20, 120))
    
    # Description
    description = wrap_text(movie_data["overview"], font_light, 360)
    for i, line in enumerate(description):
        text = font_light.render(line, True, THEMES[current_theme]["text"])
        info_surface.blit(text, (20, 170 + i * 30))
    
    return info_surface

# === PAUSE MENU ===
def show_pause_menu():
    global game_paused, current_theme, running
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    fenetre.blit(overlay, (0, 0))
    
    # Calculate button positions based on window size
    button_width = 300
    button_height = 60
    button_spacing = 20
    total_height = (button_height * 5) + (button_spacing * 4)  # 5 buttons with 4 spaces
    start_y = (hauteur - total_height) // 2  # Center vertically
    
    # Pause menu buttons
    theme_buttons = [
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y, button_width, button_height), 
         "text": "Dark Mode", "value": "dark", "color": (30, 30, 40)},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height), 
         "text": "Light Mode", "value": "light", "color": (240, 240, 240)},
        {"rect": pygame.Rect((largeur - button_width) // 2, start_y + (button_height + button_spacing) * 2, button_width, button_height), 
         "text": "Retro Mode", "value": "retro", "color": (0, 0, 0)}
    ]
    
    resume_button = pygame.Rect((largeur - button_width) // 2, start_y + (button_height + button_spacing) * 3, button_width, button_height)
    quit_button = pygame.Rect((largeur - button_width) // 2, start_y + (button_height + button_spacing) * 4, button_width, button_height)
    
    # Draw pause menu title
    title = font_title.render("Game Paused", True, THEMES[current_theme]["text"])
    title_y = start_y - 100  # Position title above the buttons
    fenetre.blit(title, (largeur // 2 - title.get_width() // 2, title_y))
    
    # Draw theme buttons
    for btn in theme_buttons:
        draw_button(btn["rect"], btn["text"], btn["color"], 
                   (min(btn["color"][0] + 30, 255), min(btn["color"][1] + 30, 255), min(btn["color"][2] + 30, 255)),
                   THEMES[current_theme]["text"])
    
    # Draw resume button
    draw_button(resume_button, "Resume Game", THEMES[current_theme]["button"],
                (min(THEMES[current_theme]["button"][0] + 30, 255), 
                 min(THEMES[current_theme]["button"][1] + 30, 255), 
                 min(THEMES[current_theme]["button"][2] + 30, 255)),
                THEMES[current_theme]["text"])
    
    # Draw quit button
    draw_button(quit_button, "Quit Game", THEMES[current_theme]["wrong"],
                (min(THEMES[current_theme]["wrong"][0] + 30, 255), 
                 min(THEMES[current_theme]["wrong"][1] + 30, 255), 
                 min(THEMES[current_theme]["wrong"][2] + 30, 255)),
                THEMES[current_theme]["text"])
    
    pygame.display.update()
    
    # Handle pause menu events
    while game_paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check theme buttons
                for btn in theme_buttons:
                    if btn["rect"].collidepoint(event.pos):
                        current_theme = btn["value"]
                        button_sound.play()
                        return
                # Check resume button
                if resume_button.collidepoint(event.pos):
                    game_paused = False
                    button_sound.play()
                    return
                # Check quit button
                elif quit_button.collidepoint(event.pos):
                    button_sound.play()
                    running = False
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_paused = False
                    button_sound.play()
                    return

# === CHOIX NOMBRE DE JOUEURS + SETUP ===
player_count = select_player_count()
players = setup_players(player_count)
current_difficulty = select_difficulty()
reveal_speed = DIFFICULTY_SPEEDS[current_difficulty]
select_filters()
select_theme()  # Add theme selection
reset_game()

# === BOUTON NOUVEAU FILM ===
button_rect = pygame.Rect(largeur - 300, hauteur - 100, 250, 60)  # New film button

# === BOUCLE PRINCIPALE ===
running = True
clock = pygame.time.Clock()


def show_game_over():
    # Reset game state for new game
    global current_round, player_streaks
    current_round = 1
    player_streaks = {}

    # Show game over screen
    while True:
        fenetre.fill(COULEUR_FOND_HAUT)
        pygame.draw.rect(fenetre, COULEUR_FOND_BAS, (0, hauteur // 2, largeur, hauteur // 2))

        # Title
        title = font_title.render("Partie Terminée", True, BLANC)
        fenetre.blit(title, (largeur // 2 - title.get_width() // 2, 100))

        # Scores
        subtitle = font_medium.render("Scores Finaux", True, GRIS_CLAIR)
        fenetre.blit(subtitle, (largeur // 2 - subtitle.get_width() // 2, 180))

        # Sort players by score
        sorted_players = sorted(players, key=lambda x: x["score"], reverse=True)

        for i, player in enumerate(sorted_players):
            score_text = f"{player['name']}: {player['score']:.1f} points"
            if i == 0 and player['score'] > 0:
                score_text += " 🏆"
            score_surface = font_bold.render(score_text, True, player['color'])
            fenetre.blit(score_surface, (largeur // 2 - score_surface.get_width() // 2, 250 + i * 60))

        # Buttons
        replay_button = pygame.Rect(350, 450, 300, 60)
        quit_button = pygame.Rect(350, 550, 300, 60)

        draw_button(replay_button, "REJOUER", VERT,
                    (min(VERT[0] + 30, 255), min(VERT[1] + 30, 255), min(VERT[2] + 30, 255)))
        draw_button(quit_button, "QUITTER", ROUGE,
                    (min(ROUGE[0] + 30, 255), min(ROUGE[1] + 30, 255), min(ROUGE[2] + 30, 255)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button.collidepoint(event.pos):
                    # Reset all player scores
                    for player in players:
                        player["score"] = 0
                    reset_game()
                    return
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()


# === GAME STATE MANAGEMENT ===
class GameState:
    def __init__(self):
        self.state = "menu"
        self.score = 0
        self.difficulty = "easy"
        self.hints_used = 0
        self.start_time = 0
        self.current_image = None
        self.guessed = False
        self.particle_system = ParticleSystem()

    def reset_round(self):
        self.hints_used = 0
        self.start_time = time.time()
        self.current_image = None
        self.guessed = False

    def calculate_score(self):
        if not self.guessed:
            return 0
            
        base_points = {"easy": 1, "medium": 2, "hard": 3}[self.difficulty]
        time_taken = time.time() - self.start_time
        time_bonus = max(0, 5 - time_taken)
        hint_penalty = self.hints_used * 0.5
        
        return round(base_points + time_bonus - hint_penalty, 1)

# === SOUND SYSTEM ===
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.volume = 0.5
        self.load_sounds()

    def load_sounds(self):
        sound_dir = "assets/sounds"
        os.makedirs(sound_dir, exist_ok=True)
        
        sound_definitions = {
            "correct": (880, 0.2),  # frequency, duration
            "wrong": (220, 0.2),
            "hint": (440, 0.1),
            "button": (660, 0.1),
            "reveal": (550, 0.2),
            "timer": (330, 0.1)
        }

        for name, (freq, duration) in sound_definitions.items():
            file_path = os.path.join(sound_dir, f"{name}.wav")
            if os.path.exists(file_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(file_path)
                except:
                    self.sounds[name] = self.generate_sound(freq, duration)
            else:
                self.sounds[name] = self.generate_sound(freq, duration)
                # Skip saving since pygame.mixer.Sound has no save method

            if isinstance(self.sounds[name], pygame.mixer.Sound):
                self.sounds[name].set_volume(self.volume)

    def generate_sound(self, frequency, duration):
        try:
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(frequency * t * 2 * np.pi)
            note = note * 0.3
            note = (note * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(note)
            return sound
        except:
            return pygame.mixer.Sound(buffer=bytearray(1))

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

# Initialize game state and sound manager
game_state = GameState()
sound_manager = SoundManager()

while running:
    # Dégradé de fond
    fenetre.fill(THEMES[current_theme]["background_top"])
    pygame.draw.rect(fenetre, THEMES[current_theme]["background_bottom"], (0, hauteur // 2, largeur, hauteur // 2))

    # Mise à jour des particules
    particles = [p for p in particles if not p.update()]

    # Affichage des particules
    for p in particles:
        p.draw(fenetre)

    if movie and movie["image"]:
        # Cadre pour l'image
        pygame.draw.rect(fenetre, GRIS_FONCE,
                         (image_pos[0] - 10, image_pos[1] - 10, image_size[0] + 20, image_size[1] + 20),
                         border_radius=12)
        pygame.draw.rect(fenetre, (0, 0, 0, 30),
                         (image_pos[0] - 10, image_pos[1] - 10, image_size[0] + 20, image_size[1] + 20), 2,
                         border_radius=12)

        # Image pixelisée
        original_image = movie["image"]
        small_image = pygame.transform.scale(original_image, (current_res, int(current_res * 1.5)))
        pixelated_image = pygame.transform.scale(small_image, image_size)
        fenetre.blit(pixelated_image, image_pos)

        if revealing and not typing_started and current_res < max_res:
            current_res += reveal_speed
        elif current_res >= max_res and not fully_revealed:
            reveal_sound.play()
            fully_revealed = True
            fully_revealed_time = pygame.time.get_ticks()
            result_surface = font_medium.render("Image complètement révélée !", True, BLEU_CIEL)
            result_color = BLEU_CIEL

        # Check if 5 seconds have passed since full reveal
        if fully_revealed and not typing_started:
            time_since_reveal = (pygame.time.get_ticks() - fully_revealed_time) / 1000
            if time_since_reveal >= 5:
                if current_player:
                    current_player["score"] -= 1
                    result_surface = font_bold.render("Temps écoulé ! -1 point", True, ROUGE)
                    result_color = ROUGE
                    current_player = None
                    revealing = False
                    typing_started = False
                    error_pause_timer = pygame.time.get_ticks() + 2000
                else:
                    result_surface = font_medium.render("", True, BLANC)
                    result_color = BLANC

    # Zone de saisie
    input_box_rect = pygame.Rect(largeur // 2 - 225, hauteur - 100, 450, 50)
    pygame.draw.rect(fenetre, GRIS_FONCE, input_box_rect, border_radius=8)
    pygame.draw.rect(fenetre, (0, 0, 0, 30), input_box_rect, 2, border_radius=8)

    text_surface = font_medium.render(user_input, True, BLANC)
    fenetre.blit(text_surface, (input_box_rect.x + 20, input_box_rect.y + 10))

    # Indicateur de saisie
    if pygame.time.get_ticks() % 1000 < 500 and typing_started:
        cursor_x = input_box_rect.x + 20 + text_surface.get_width()
        pygame.draw.rect(fenetre, BLANC, (cursor_x, input_box_rect.y + 15, 2, 30))

    # Résultat
    if isinstance(result_surfaces, list):  # If it's a correct guess with multiple lines
        for surface, rect in result_surfaces:
            fenetre.blit(surface, rect)
    elif result_surface:  # For other messages
        fenetre.blit(result_surface, (350, 660))
    elif hints_used == 3:  # If it's the description hint
        draw_hint_text(hint, result_color)

    # Bouton nouveau film
    draw_button(button_rect, "NOUVEAU FILM", THEMES[current_theme]["button"],
                (min(THEMES[current_theme]["button"][0] + 30, 255), 
                 min(THEMES[current_theme]["button"][1] + 30, 255), 
                 min(THEMES[current_theme]["button"][2] + 30, 255)),
                THEMES[current_theme]["text"])

    # Hint button
    hint_button_rect = pygame.Rect(largeur - 300, hauteur - 170, 250, 60)  # Hint button
    hint_text = f"Indice ({max_hints - hints_used} restants)"
    hint_button_hovered = draw_button(hint_button_rect, hint_text, THEMES[current_theme]["button"],
                                    (min(THEMES[current_theme]["button"][0] + 30, 255), 
                                     min(THEMES[current_theme]["button"][1] + 30, 255), 
                                     min(THEMES[current_theme]["button"][2] + 30, 255)),
                                    THEMES[current_theme]["text"])

    # Affichage du joueur actif
    if current_player:
        player_surface = font_bold.render(f"{current_player['name']} devine...", True, current_player['color'])
        fenetre.blit(player_surface, (50, 100))

        # Animation particules
        if random.random() < 0.2:
            particles.append(Particle(
                random.randint(50, 50 + player_surface.get_width()),
                random.randint(50, 50 + player_surface.get_height()),
                current_player['color']
            ))

    # Affichage des scores
    score_title = font_medium.render("SCORES", True, GRIS_CLAIR)
    fenetre.blit(score_title, (largeur - 250, 50))

    for i, player in enumerate(players):
        score_text = f"{player['name']}: {player['score']:.1f}"
        score_surface = font_bold.render(score_text, True, player['color'])
        fenetre.blit(score_surface, (largeur - 250, 100 + i * 50))

        # Étoile pour le leader
        if player['score'] == max(p['score'] for p in players) and player['score'] > 0:
            star = font_medium.render("★", True, (255, 215, 0))
            fenetre.blit(star, (largeur - 210, 100 + i * 50))

    # Draw round and difficulty info
    round_text = f"Round {current_round}/{max_rounds}"
    difficulty_text = f"Difficulté: {current_difficulty.capitalize()}"
    round_surface = font_medium.render(round_text, True, GRIS_CLAIR)
    difficulty_surface = font_medium.render(difficulty_text, True, GRIS_CLAIR)
    fenetre.blit(round_surface, (50, 150))
    fenetre.blit(difficulty_surface, (50, 180))

    # Draw last movie if available
    if last_movie_display and last_movie_timer > 0:
        fenetre.blit(last_movie_display, (50, 200))
        last_movie_timer -= 1

    # Draw streak info
    for i, player in enumerate(players):
        if player['name'] in player_streaks and player_streaks[player['name']] > 1:
            streak_text = f"Streak: {player_streaks[player['name']]}"
            streak_surface = font_medium.render(streak_text, True, player['color'])
            fenetre.blit(streak_surface, (largeur - 200, 250 + i * 50))

    # Add skip button
    skip_button_rect = pygame.Rect(largeur - 300, hauteur - 240, 250, 60)  # Skip button
    if skip_available:
        skip_hovered = draw_button(skip_button_rect, "PASSER", THEMES[current_theme]["button"],
                                (min(THEMES[current_theme]["button"][0] + 30, 255), 
                                 min(THEMES[current_theme]["button"][1] + 30, 255), 
                                 min(THEMES[current_theme]["button"][2] + 30, 255)),
                                THEMES[current_theme]["text"])
    else:
        pygame.draw.rect(fenetre, THEMES[current_theme]["background_top"], skip_button_rect, border_radius=8)
        pygame.draw.rect(fenetre, THEMES[current_theme]["text"], skip_button_rect, 2, border_radius=8)
        text_surface = font_medium.render("PASSER", True, THEMES[current_theme]["text"])
        text_rect = text_surface.get_rect(center=skip_button_rect.center)
        fenetre.blit(text_surface, text_rect)

    # Update turn indicator
    turn_indicator.update()
    for player in players:
        turn_indicator.draw(fenetre, player)
    
    # Show movie info after correct guess
    if isinstance(result_surfaces, list) and movie:  # If it's a correct guess
        movie_info = show_movie_info(movie)
        fenetre.blit(movie_info, (300, 200))

    # Add pause button (top-left corner)
    pause_button_rect = pygame.Rect(50, 50, 100, 40)
    draw_button(pause_button_rect, "Pause", THEMES[current_theme]["button"],
                (min(THEMES[current_theme]["button"][0] + 30, 255), 
                 min(THEMES[current_theme]["button"][1] + 30, 255), 
                 min(THEMES[current_theme]["button"][2] + 30, 255)),
                THEMES[current_theme]["text"])

    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Handle ESC key for pause menu
                game_paused = True
                button_sound.play()
                show_pause_menu()
                continue  # Skip other key processing when paused
            
            if game_paused:  # Skip other key processing when game is paused
                continue
                
            key_name = pygame.key.name(event.key)
            
            if not current_player:
                for p in players:
                    if key_name == p["key"]:
                        current_player = p
                        user_input = ""
                        typing_started = True
                        revealing = False
                        current_res = current_res
                        break
            else:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if user_input.lower() == movie["title"].lower():
                        correct_sound.play()
                        time_taken = (pygame.time.get_ticks() - start_time) / 1000
                        base_score = {"easy": 10, "medium": 15, "hard": 20}[current_difficulty]
                        time_bonus = max(0, 5 - time_taken)
                        hint_penalty = hints_used * 0.5
                        streak_bonus = player_streaks.get(current_player["name"], 0) * 0.5
                        total_score = base_score + time_bonus - hint_penalty + streak_bonus
                        
                        player_streaks[current_player["name"]] = player_streaks.get(current_player["name"], 0) + 1
                        
                        result_text1 = f"Correct !"
                        result_text2 = f"+{total_score:.1f} points"
                        if streak_bonus > 0:
                            result_text2 += f" (+{streak_bonus:.1f} bonus streak)"
                        
                        result_surface1 = font_bold.render(result_text1, True, VERT)
                        result_surface2 = font_bold.render(result_text2, True, VERT)
                        
                        text1_rect = result_surface1.get_rect(centerx=largeur // 2, y=650)
                        text2_rect = result_surface2.get_rect(centerx=largeur // 2, y=690)
                        
                        result_surfaces = [(result_surface1, text1_rect), (result_surface2, text2_rect)]
                        result_color = VERT
                        
                        current_res = max_res
                        revealing = False
                        current_player["score"] += total_score
                        current_round += 1
                        reset_game()
                    else:
                        wrong_sound.play()
                        result_surface = font_bold.render("Incorrect", True, ROUGE)
                        result_color = ROUGE
                        revealing = True
                        typing_started = False
                        current_player = None
                        # Reset streak on incorrect guess
                        if current_player:
                            player_streaks[current_player["name"]] = 0
                else:
                    if len(user_input) < 30:
                        user_input += event.unicode
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_paused:  # Skip mouse processing when game is paused
                continue
                
            if button_rect.collidepoint(event.pos):
                button_sound.play()
                reset_game()
            elif skip_button_rect.collidepoint(event.pos) and skip_available:
                button_sound.play()
                skip_available = False
                current_round += 1
                reset_game()
            elif hint_button_rect.collidepoint(event.pos) and hints_used < max_hints:
                hint_sound.play()
                hints_used += 1
                if hints_used == 1:
                    hint = f"Année: {movie['release_date'][:4]}"
                    result_surface = font_light.render(hint, True, BLEU_CIEL)
                    result_color = BLEU_CIEL
                elif hints_used == 2:
                    hint = f"Premier mot: {movie['title'].split()[0]}"
                    result_surface = font_light.render(hint, True, BLEU_CIEL)
                    result_color = BLEU_CIEL
                else:
                    hint = f"Description: {movie['overview']}"
                    result_surface = None
                    result_color = BLEU_CIEL
                error_pause_timer = pygame.time.get_ticks() + 5000
            elif pause_button_rect.collidepoint(event.pos):
                game_paused = True
                button_sound.play()
                show_pause_menu()

    if error_pause_timer and pygame.time.get_ticks() >= error_pause_timer:
        # Only restart the animation if we're not showing the third hint
        if hints_used < 3:
            revealing = True
        typing_started = False
        result_surface = font_medium.render("", True, BLANC)
        error_pause_timer = 0

pygame.quit()