

import math
import time
import threading
from collections import deque


PORT = "/dev/cu.usbmodem11201"        
BAUD = 115200
MAX_DISTANCE = 60      
FADE = 4.0        
SIMULATE = False       

try:
    import pygame
except ImportError:
    raise SystemExit("pygame manquant. Installe-le avec : pip install pygame")

try:
    import serial  # pyserial
except ImportError:
    if not SIMULATE:
        raise SystemExit("pyserial manquant. Installe-le avec : pip install pyserial")
    serial = None


state = {
    "angle": 0,
    "points": [],    
    "lock": threading.Lock(),
    "running": True,
    "connected": False,
}


def serial_reader():
    """Lit le port serie en continu et met a jour l'etat partage."""
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print("Impossible d'ouvrir le port serie:", e)
        print("Verifie PORT, ou passe SIMULATE = True pour tester l'affichage.")
        return
    time.sleep(2)    
    ser.reset_input_buffer()
    state["connected"] = True
    while state["running"]:
        try:
            line = ser.readline().decode("ascii", errors="ignore").strip()
        except Exception:
            continue
        if not line or "," not in line:
            continue
        a_str, d_str = line.split(",", 1)
        try:
            a = int(a_str)
            d = float(d_str)
        except ValueError:
            continue
        a = max(0, min(180, a))
        with state["lock"]:
            state["angle"] = a
            if 0 < d <= MAX_DISTANCE:
                state["points"].append([a, d, time.time()])
    ser.close()


def sim_reader():
    """Genere un balayage factice avec quelques obstacles, pour tester."""
    state["connected"] = True
    a, direction = 0, 1
    obstacles = {35: 22, 90: 40, 130: 15}   # angle -> distance
    while state["running"]:
        with state["lock"]:
            state["angle"] = a
            if a in obstacles:
                jitter = (time.time() * 7) % 6 - 3
                state["points"].append([a, obstacles[a] + jitter, time.time()])
        a += direction
        if a >= 180:
            a, direction = 180, -1
        elif a <= 0:
            a, direction = 0, 1
        time.sleep(0.015)



W, H = 1000, 560
CX, CY = W // 2, H - 40
R = min(CX - 50, CY - 50)

BG = (6, 14, 8)
GRID = (24, 90, 44)
GRID_TEXT = (60, 160, 90)
SWEEP = (40, 255, 90)


def polar(angle, r):
    rad = math.radians(angle)
    return CX + r * math.cos(rad), CY - r * math.sin(rad)


def dist_color(d):
    """Rouge (proche) -> jaune -> vert (loin)."""
    f = max(0.0, min(1.0, d / MAX_DISTANCE))
    r = int(255 + (60 - 255) * f)
    g = int(70 + (255 - 70) * f)
    b = int(50 + (90 - 50) * f)
    return (r, g, b)


def alpha_circle(screen, color, pos, radius, alpha):
    s = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (radius + 1, radius + 1), radius)
    screen.blit(s, (pos[0] - radius - 1, pos[1] - radius - 1))


def main():
    reader = sim_reader if (SIMULATE or serial is None) else serial_reader
    threading.Thread(target=reader, daemon=True).start()

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Radar ultrason")
    font = pygame.font.SysFont("consolas", 16)
    big = pygame.font.SysFont("consolas", 22, bold=True)
    clock = pygame.time.Clock()

    rings = 4
    sweep_hist = deque(maxlen=22)

    while state["running"]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["running"] = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state["running"] = False

        now = time.time()
        with state["lock"]:
            cur = state["angle"]
            state["points"] = [p for p in state["points"] if now - p[2] < FADE]
            points = list(state["points"])
            connected = state["connected"]

        screen.fill(BG)

        # --- grille fixe : anneaux + radiales + etiquettes ---
        for i in range(1, rings + 1):
            rr = R * i / rings
            arc = [polar(a, rr) for a in range(0, 181, 2)]
            pygame.draw.lines(screen, GRID, False, arc, 1)
            lx, ly = polar(90, rr)
            screen.blit(font.render(f"{int(MAX_DISTANCE * i / rings)}", True, GRID_TEXT),
                        (lx + 4, ly - 8))
        for a in range(0, 181, 30):
            pygame.draw.line(screen, GRID, (CX, CY), polar(a, R), 1)
            lx, ly = polar(a, R + 20)
            screen.blit(font.render(f"{a}", True, GRID_TEXT), (lx - 8, ly - 8))

        # --- secteur lumineux du balayage (effet film) ---
        if len(sweep_hist) >= 2:
            wedge = [(CX, CY)] + [polar(a, R) for a in sweep_hist]
            glow = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.polygon(glow, (40, 255, 90, 35), wedge)
            screen.blit(glow, (0, 0))

        # --- nuage de points qui s'estompent ---
        for a, d, t in points:
            age = now - t
            alpha = max(0, int(255 * (1 - age / FADE)))
            x, y = polar(a, d / MAX_DISTANCE * R)
            alpha_circle(screen, dist_color(d), (int(x), int(y)), 4, alpha)

        # --- trainee du faisceau (du fonce au clair) ---
        sweep_hist.append(cur)
        n = len(sweep_hist)
        for idx, a in enumerate(sweep_hist):
            f = (idx + 1) / n
            col = (int(SWEEP[0] * f), int(SWEEP[1] * f), int(SWEEP[2] * f))
            pygame.draw.line(screen, col, (CX, CY), polar(a, R), 2)

        # --- HUD ---
        screen.blit(big.render(f"{cur:>3}\u00b0", True, SWEEP), (20, 16))
        status = "connecte" if connected else "en attente du port serie..."
        screen.blit(font.render(status, True, GRID_TEXT), (20, 46))
        screen.blit(font.render("Echelle : cm   |   Echap pour quitter", True, GRID_TEXT),
                    (20, H - 26))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()