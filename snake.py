# snake.py - Serpiente en Python (pygame)
import asyncio, math, random, pygame

W, H, HUD = 640, 600, 50
C_MIN, C_MAX, F_MIN, F_MAX = 6, 36, 4, 28

EXT, F_A, F_B, BARRA = (10, 20, 16), (18, 38, 31), (23, 48, 40), (12, 24, 20)
CUERPO, CABEZA, OJOS = (230, 195, 75), (250, 225, 120), (25, 25, 25)
COMIDA, TXT, SUB, ACT = (255, 95, 80), (235, 245, 230), (155, 180, 165), (80, 200, 150)
PANEL, PISTA, P_ON = (15, 30, 24), (28, 54, 44), (60, 150, 115)
BTN, BTN_H, MARCO = (24, 48, 38), (38, 76, 62), (70, 140, 110)

DIRS = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}


class Juego:
    def __init__(self, c=16, f=12):
        self.record, self.estado = 0, "inicio"
        self.reset(c, f)

    def reset(self, c=None, f=None):
        if c: self.cols = max(C_MIN, min(C_MAX, c))
        if f: self.filas = max(F_MIN, min(F_MAX, f))
        cx, cy = self.cols // 2, self.filas // 2
        self.cuerpo = [(cx, cy), (max(0, cx - 1), cy), (max(0, cx - 2), cy)]
        self.ant, self.dir, self.cola, self.pts = list(self.cuerpo), (1, 0), [], 0
        self.spawn()

    def spawn(self):
        libres = [(x, y) for x in range(self.cols) for y in range(self.filas) if (x, y) not in self.cuerpo]
        self.comida = random.choice(libres) if libres else None

    def girar(self, d):
        u = self.cola[-1] if self.cola else self.dir
        if d != u and d != (-u[0], -u[1]) and len(self.cola) < 2: self.cola.append(d)

    def paso(self):
        self.ant = list(self.cuerpo)
        if self.cola: self.dir = self.cola.pop(0)
        nx, ny = self.cuerpo[0][0] + self.dir[0], self.cuerpo[0][1] + self.dir[1]
        come = ((nx, ny) == self.comida)
        if not (0 <= nx < self.cols and 0 <= ny < self.filas) or (nx, ny) in (self.cuerpo if come else self.cuerpo[:-1]):
            self.estado, self.record = "fin", max(self.record, self.pts)
            return
        self.cuerpo.insert(0, (nx, ny))
        if come:
            self.pts += 1
            self.ant.append(self.ant[-1])
            self.spawn()
            if not self.comida: self.estado, self.record = "fin", max(self.record, self.pts)
        else: self.cuerpo.pop()


def draw_slider(pantalla, r, tit, val, vmin, vmax, suf, m, drag, f1, f2):
    if drag: val = vmin + round(max(0.0, min(1.0, (m[0] - r.x) / max(1, r.w))) * (vmax - vmin))
    t = (val - vmin) / max(1, vmax - vmin)
    pygame.draw.rect(pantalla, PISTA, r, border_radius=5)
    pygame.draw.rect(pantalla, P_ON, (r.x, r.y, int(t * r.w), r.h), border_radius=5)
    hx = r.x + int(t * r.w)
    pygame.draw.circle(pantalla, (255, 245, 180) if (r.inflate(20, 20).collidepoint(m) or drag) else CABEZA, (hx, r.centery), 9)
    pygame.draw.circle(pantalla, BARRA, (hx, r.centery), 9, 2)
    pantalla.blit(f2.render(tit, True, TXT), (r.x, r.y - 22))
    v_txt = f1.render(f"{val}{suf}", True, CABEZA)
    pantalla.blit(v_txt, (r.right - v_txt.get_width(), r.y - 24))
    return val


def draw_game(pantalla, j, celda, ox, oy, w, h, a):
    pygame.draw.rect(pantalla, MARCO, pygame.Rect(ox, oy, w, h).inflate(8, 8), 3, 8)
    for x in range(j.cols):
        for y in range(j.filas):
            pygame.draw.rect(pantalla, F_A if (x + y) % 2 else F_B, (ox + x * celda, oy + y * celda, celda, celda))
    if j.comida:
        r = max(3, int(celda * 0.38 * (1 + 0.12 * math.sin(pygame.time.get_ticks() / 180))))
        pygame.draw.circle(pantalla, COMIDA, (int(ox + j.comida[0] * celda + celda / 2), int(oy + j.comida[1] * celda + celda / 2)), r)
    for i in reversed(range(len(j.cuerpo))):
        cx, cy = j.cuerpo[i]
        if a < 1.0 and i < len(j.ant):
            cx, cy = j.ant[i][0] + (cx - j.ant[i][0]) * a, j.ant[i][1] + (cy - j.ant[i][1]) * a
        rx, ry = ox + round(cx * celda) + 1, oy + round(cy * celda) + 1
        pygame.draw.rect(pantalla, CABEZA if i == 0 else CUERPO, (rx, ry, celda - 2, celda - 2), border_radius=max(2, celda // 4))
        if i == 0:
            dx, dy = j.dir
            off, ro = max(2, celda // 3), max(1, celda // 8)
            px, py = ox + cx * celda + celda / 2, oy + cy * celda + celda / 2
            pygame.draw.circle(pantalla, OJOS, (int(px + dx * off), int(py - off)) if dx else (int(px - off), int(py + dy * off)), ro)
            pygame.draw.circle(pantalla, OJOS, (int(px + dx * off), int(py + off)) if dx else (int(px + off), int(py + dy * off)), ro)


async def main():
    pygame.init()
    pantalla = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Serpiente")
    reloj = pygame.time.Clock()

    f1, f_tit = pygame.font.Font(None, 24), pygame.font.Font(None, 42)
    f2, f_btn = pygame.font.Font(None, 22), pygame.font.Font(None, 24)

    vel, acel = 5, True
    cols, filas, esc = 16, 12, 100
    cfg, pest, drag = False, "vel", None

    j = Juego(cols, filas)
    ult = pygame.time.get_ticks()

    while True:
        m = pygame.mouse.get_pos()
        r_cfg = pygame.Rect(W - 115, HUD // 2 - 16, 100, 32)
        pw, ph = 480, 410
        px, py = (W - pw) // 2, (H - ph) // 2
        r_tvel, r_ttam = pygame.Rect(px + 16, py + 16, 210, 38), pygame.Rect(px + 246, py + 16, 210, 38)
        r_ok = pygame.Rect(px + pw // 2 - 80, py + ph - 48, 160, 36)
        r_svel, r_tog = pygame.Rect(px + 25, py + 125, pw - 50, 10), pygame.Rect(px + 25, py + 200, pw - 50, 40)
        r_sc, r_sf, r_se = pygame.Rect(px + 25, py + 105, pw - 50, 10), pygame.Rect(px + 25, py + 175, pw - 50, 10), pygame.Rect(px + 25, py + 245, pw - 50, 10)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return

            if cfg:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if r_tvel.collidepoint(e.pos): pest = "vel"
                    elif r_ttam.collidepoint(e.pos): pest = "tam"
                    elif r_ok.collidepoint(e.pos): cfg = False
                    elif pest == "vel" and r_tog.collidepoint(e.pos): acel = not acel
                    elif pest == "vel" and r_svel.inflate(20, 24).collidepoint(e.pos): drag = "vel"
                    elif pest == "tam":
                        if r_sc.inflate(20, 24).collidepoint(e.pos): drag = "c"
                        elif r_sf.inflate(20, 24).collidepoint(e.pos): drag = "f"
                        elif r_se.inflate(20, 24).collidepoint(e.pos): drag = "e"
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1: drag = None
                elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_c): cfg = False
            else:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and r_cfg.collidepoint(e.pos):
                    cfg = True
                    if j.estado == "jugando": j.estado = "pausa"
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_c:
                        cfg = True
                        if j.estado == "jugando": j.estado = "pausa"
                    elif e.key in DIRS:
                        if j.estado in ("inicio", "fin"):
                            if j.estado == "fin": j.reset(cols, filas)
                            j.estado, ult = "jugando", pygame.time.get_ticks()
                        if j.estado == "jugando": j.girar(DIRS[e.key])
                    elif e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_p):
                        if j.estado in ("inicio", "fin"):
                            j.reset(cols, filas)
                            j.estado, ult = "jugando", pygame.time.get_ticks()
                        elif j.estado == "jugando": j.estado = "pausa"
                        elif j.estado == "pausa": j.estado, ult = "jugando", pygame.time.get_ticks()
                    elif e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

        now = pygame.time.get_ticks()
        interv = max(35, (205 - vel * 16) - ((j.pts // 2) * 4 if acel else 0))
        if j.estado == "jugando" and not cfg:
            while now - ult >= interv and j.estado == "jugando":
                ult += interv
                j.paso()
            alpha = min(1.0, (now - ult) / interv)
        else: alpha = 1.0

        pantalla.fill(EXT)
        c_max = min((W - 60) // j.cols, (H - HUD - 50) // j.filas)
        celda = max(10, int(c_max * (esc / 100.0)))
        gw, gh = j.cols * celda, j.filas * celda
        draw_game(pantalla, j, celda, (W - gw) // 2, HUD + (H - HUD - gh) // 2, gw, gh, alpha)

        pygame.draw.rect(pantalla, BARRA, (0, 0, W, HUD))
        pygame.draw.line(pantalla, (25, 50, 40), (0, HUD), (W, HUD), 2)
        pantalla.blit(f1.render(f"Puntos: {j.pts}   Récord: {j.record}   [ {j.cols}x{j.filas} ]", True, TXT), (15, HUD // 2 - 8))

        pygame.draw.rect(pantalla, BTN_H if r_cfg.collidepoint(m) else BTN, r_cfg, border_radius=6)
        pygame.draw.rect(pantalla, CUERPO, r_cfg, 1, 6)
        pantalla.blit(f2.render("⚙ Ajustes", True, CABEZA), f2.render("⚙ Ajustes", True, CABEZA).get_rect(center=r_cfg.center))

        if not cfg and j.estado in ("inicio", "pausa", "fin"):
            v = pygame.Surface((W, H - HUD), pygame.SRCALPHA)
            v.fill((10, 20, 16, 215))
            pantalla.blit(v, (0, HUD))
            cy = HUD + (H - HUD) // 2
            mensajes = {
                "inicio": [("SERPIENTE", CABEZA, -42, f_tit), (f"Tablero: {j.cols} x {j.filas}", TXT, -10, f2),
                           ("Presioná Flechas o Espacio para jugar", SUB, 18, f2), ("Clic en ⚙ Ajustes (o C) para configurar con el mouse", ACT, 44, f1)],
                "pausa": [("EN PAUSA", TXT, -16, f_tit), ("Espacio para reanudar", SUB, 20, f2)],
                "fin": [("FIN DEL JUEGO", COMIDA, -28, f_tit), (f"Puntaje: {j.pts}", TXT, 0, f2), ("Espacio o Flechas para volver a jugar", CABEZA, 28, f2)]
            }[j.estado]
            for txt_s, col, dy, f in mensajes:
                s = f.render(txt_s, True, col)
                pantalla.blit(s, s.get_rect(center=(W // 2, cy + dy)))

        if cfg:
            v = pygame.Surface((W, H), pygame.SRCALPHA)
            v.fill((6, 14, 10, 230))
            pantalla.blit(v, (0, 0))
            pygame.draw.rect(pantalla, PANEL, (px, py, pw, ph), border_radius=14)
            pygame.draw.rect(pantalla, ACT, (px, py, pw, ph), 2, 14)

            for r, nom, act in [(r_tvel, "⚡ Velocidad", pest == "vel"), (r_ttam, "📐 Tamaño (Mouse)", pest == "tam")]:
                pygame.draw.rect(pantalla, BTN_H if (act or r.collidepoint(m)) else BTN, r, border_radius=8)
                if act: pygame.draw.rect(pantalla, ACT, r, 2, 8)
                pantalla.blit(f2.render(nom, True, CABEZA if act else TXT), f2.render(nom, True, CABEZA if act else TXT).get_rect(center=r.center))

            if pest == "vel":
                vel = draw_slider(pantalla, r_svel, "Velocidad de la serpiente", vel, 1, 10, " / 10", m, drag == "vel", f1, f2)
                pygame.draw.rect(pantalla, BTN_H if r_tog.collidepoint(m) else BTN, r_tog, border_radius=8)
                pygame.draw.rect(pantalla, CUERPO, r_tog, 1, 8)
                pantalla.blit(f2.render("Acelerar al comer manzana:", True, TXT), (r_tog.left + 15, r_tog.centery - 8))
                t_ac = f2.render("Activado" if acel else "Fijo", True, ACT if acel else COMIDA)
                pantalla.blit(t_ac, (r_tog.right - t_ac.get_width() - 15, r_tog.centery - 8))
            else:
                nc = draw_slider(pantalla, r_sc, "Ancho (columnas)", cols, C_MIN, C_MAX, " cols", m, drag == "c", f1, f2)
                nf = draw_slider(pantalla, r_sf, "Alto (filas)", filas, F_MIN, F_MAX, " filas", m, drag == "f", f1, f2)
                esc = draw_slider(pantalla, r_se, "Tamaño del cuadrado", esc, 40, 100, " %", m, drag == "e", f1, f2)
                if nc != cols or nf != filas:
                    cols, filas = nc, nf
                    j.reset(cols, filas)

            pygame.draw.rect(pantalla, ACT if r_ok.collidepoint(m) else CABEZA, r_ok, border_radius=8)
            pantalla.blit(f_btn.render("Listo / Jugar", True, BARRA), f_btn.render("Listo / Jugar", True, BARRA).get_rect(center=r_ok.center))

        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
