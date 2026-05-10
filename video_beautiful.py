import pygame
import sys
import math
from collections import defaultdict

# ══════════════════════════════════════════════════════════════════
#  WINDOW & FPS
# ══════════════════════════════════════════════════════════════════
WIDTH, HEIGHT = 1280, 820
FPS = 2

# ══════════════════════════════════════════════════════════════════
#  PALETTE  (matches reference image colours)
# ══════════════════════════════════════════════════════════════════
BG_OUTSIDE    = (58,  62,  58)   # dark asphalt outside
BG_PANEL      = (35,  37,  32)   # header/footer panels
WALL_COLOR    = (100, 70,  50)   # brown outer wall
FLOOR_GENERIC = (200,190,170)    # neutral tile
SHADOW        = (0,   0,   0,  80)

ZONE_COLORS = {
    'K':   {'fill': (175, 230, 165), 'border': (70, 150, 60),   'label_bg': (80, 165, 70),   'name': 'Кухня',     'floor': (218, 212, 198)},
    'BVR': {'fill': (250, 170, 200), 'border': (185, 60, 110),  'label_bg': (210, 80,  130),  'name': 'Напитки',   'floor': (215, 208, 196)},
    'C':   {'fill': (255, 235, 130), 'border': (175, 140, 20),  'label_bg': (200, 165, 40),   'name': 'Прилавок',  'floor': (222, 215, 200)},
    'FF':  {'fill': (245, 215, 150), 'border': (160, 120, 50),  'label_bg': (190, 145, 70),   'name': 'Картофель', 'floor': (220, 213, 198)},
    'TS':  {'fill': (150, 195, 255), 'border': ( 50,  95, 165), 'label_bg': (65,  110, 185),  'name': 'Зал',       'floor': (212, 207, 195)},
}

TEXT_DARK  = (30,  30,  30)
TEXT_LIGHT = (255, 255, 255)
TEXT_DIM   = (160, 160, 160)

EMPLOYEE_BADGE_COLORS = [
    ((230,  80,  80), (255, 200, 200)),  # red
    ((80,  140, 230), (200, 220, 255)),  # blue
    ((80,  200, 120), (200, 255, 220)),  # green
    ((200, 130,  50), (255, 220, 170)),  # orange
    ((160,  80, 220), (230, 200, 255)),  # purple
    ((50,  180, 200), (190, 245, 255)),  # teal
]

STATIONS = ['K', 'BVR', 'C', 'FF', 'TS']


# ══════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════
def read_data():
    datetimes = []
    for date in ['2026-04-27', '2026-04-28', '2026-04-29',
                 '2026-04-30', '2026-05-01', '2026-05-02', '2026-05-03']:
        for h in range(7, 23):
            datetimes.append((date, h))

    employees_shifts = defaultdict(dict)
    with open('schedule_result.csv', 'r') as f:
        for line in f.readlines()[1:]:
            ds, station_key, employee_id, starttime, finishtime = line.split(';')
            employees_shifts[employee_id][ds] = (
                int(starttime), int(finishtime), station_key.strip()
            )
    return datetimes, employees_shifts


def get_current_employees(date, h, employees_shifts):
    res = defaultdict(list)
    for emp in employees_shifts:
        if date in employees_shifts[emp]:
            start, finish, station = employees_shifts[emp][date]
            if start <= h <= finish:
                res[station].append(emp)
    return res


# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_rrect(surf, color, rect, r=10, border_color=None, border_w=0):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border_color and border_w:
        pygame.draw.rect(surf, border_color, rect, border_w, border_radius=r)


def draw_tile_floor(surf, color, rect, tile_size=24):
    """Draw a simple tile pattern inside rect."""
    x0, y0, w, h = rect
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    base.fill(color)
    darker = tuple(max(0, c - 20) for c in color)
    # horizontal lines
    for y in range(0, h, tile_size):
        pygame.draw.line(base, darker, (0, y), (w, y), 1)
    # vertical lines
    for x in range(0, w, tile_size):
        pygame.draw.line(base, darker, (x, 0), (x, h), 1)
    surf.blit(base, (x0, y0))


def shadow_rect(surf, rect, offset=4, alpha=60):
    sx, sy, sw, sh = rect
    s = pygame.Surface((sw, sh), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surf.blit(s, (sx + offset, sy + offset))


# ══════════════════════════════════════════════════════════════════
#  DECORATIVE FURNITURE
# ══════════════════════════════════════════════════════════════════
def draw_kitchen_deco(surf, zone_rect):
    x, y, w, h = zone_rect
    # Countertop strip along the top
    counter_h = 28
    draw_rrect(surf, (160, 160, 155), (x+10, y+10, w-20, counter_h), r=4)
    # Small equipment boxes
    eq_colors = [(130,130,125), (120,120,115), (110,100,90)]
    for i, ec in enumerate(eq_colors):
        bx = x + 18 + i * 52
        draw_rrect(surf, ec, (bx, y+14, 38, 20), r=3)
    # Central worktop
    draw_rrect(surf, (170,165,150), (x + w//2 - 35, y + h//2 - 14, 70, 28), r=4)
    draw_rrect(surf, (140,135,120), (x + w//2 - 30, y + h//2 - 10, 60, 20), r=3)


def draw_bvr_deco(surf, zone_rect):
    x, y, w, h = zone_rect
    # Drink dispensers row
    for i in range(4):
        dx = x + 14 + i * 26
        draw_rrect(surf, (200, 60, 60), (dx, y+12, 18, 36), r=4)
        draw_rrect(surf, (240,100,100), (dx+3, y+16, 12, 10), r=2)
    # Sink area
    draw_rrect(surf, (180,175,165), (x + w - 55, y+14, 42, 30), r=4)


def draw_counter_deco(surf, zone_rect):
    x, y, w, h = zone_rect
    # Menu board strip
    board_h = 22
    draw_rrect(surf, (40, 40, 45), (x+8, y+8, w-16, board_h), r=3)
    for i in range(4):
        bx = x + 16 + i * ((w-32)//4)
        draw_rrect(surf, (200,150,60), (bx, y+12, (w-40)//4 - 4, 14), r=2)
    # Counter desk
    desk_y = y + h - 50
    draw_rrect(surf, (160, 130, 70), (x+8, desk_y, w-16, 30), r=5)
    draw_rrect(surf, (130, 100, 40), (x+8, desk_y, w-16, 30), r=5, border_color=(100,75,20), border_w=2)
    # Two POS terminals
    for px in [x + w//3 - 10, x + 2*w//3 - 10]:
        draw_rrect(surf, (30, 30, 35), (px, desk_y - 22, 22, 20), r=3)
        draw_rrect(surf, (20, 20, 25), (px+3, desk_y - 20, 16, 14), r=2)


def draw_ff_deco(surf, zone_rect):
    x, y, w, h = zone_rect
    # Fry bin
    draw_rrect(surf, (180,155, 80), (x+10, y+10, w-20, 40), r=4)
    # Fry pile (yellow squiggles)
    for i in range(8):
        fx = x + 15 + i * 12
        pygame.draw.line(surf, (230,200,50), (fx, y+18), (fx+4, y+38), 3)
    # Equipment right side
    draw_rrect(surf, (155,145,135), (x + w - 42, y + 12, 32, 50), r=4)
    draw_rrect(surf, (130,120,110), (x + w - 38, y + 16, 24, 14), r=2)


def draw_ts_deco(surf, zone_rect):
    x, y, w, h = zone_rect
    # Tables with chairs
    table_positions = [
        (x + 40,  y + 30),
        (x + 170, y + 30),
        (x + 340, y + 30),
        (x + 470, y + 30),
        (x + 100, y + h - 75),
        (x + 280, y + h - 75),
        (x + 420, y + h - 75),
    ]
    table_w, table_h = 60, 40
    chair_size = 14
    chair_color    = (200, 150, 50)
    chair_shadow   = (160, 110, 20)
    table_color    = (195, 165, 110)
    table_shadow   = (150, 120, 70)

    for tx, ty in table_positions:
        if tx + table_w > x + w - 10 or ty + table_h > y + h - 10:
            continue
        cx, cy = tx + table_w // 2, ty + table_h // 2

        # shadow
        shadow_rect(surf, (tx+3, ty+3, table_w, table_h), offset=0, alpha=40)
        # table
        draw_rrect(surf, table_shadow, (tx, ty, table_w, table_h), r=5)
        draw_rrect(surf, table_color,  (tx+2, ty+2, table_w-4, table_h-4), r=4)

        # chairs around table
        chairs = [
            (cx - chair_size // 2, ty - chair_size - 3),       # top
            (cx - chair_size // 2, ty + table_h + 3),           # bottom
            (tx - chair_size - 3,  cy - chair_size // 2),       # left
            (tx + table_w + 3,     cy - chair_size // 2),       # right
        ]
        for chx, chy in chairs:
            draw_rrect(surf, chair_shadow, (chx+1, chy+1, chair_size, chair_size), r=4)
            draw_rrect(surf, chair_color,  (chx,   chy,   chair_size, chair_size), r=4)

    # Plant decorations along entry wall
    for px in [x + w//4, x + w//2, x + 3*w//4]:
        draw_rrect(surf, (60, 100, 55), (px - 8, y + 4, 16, 18), r=3)
        pygame.draw.circle(surf, (80, 140, 70), (px, y + 4), 10)


# ══════════════════════════════════════════════════════════════════
#  EMPLOYEE BADGES
# ══════════════════════════════════════════════════════════════════
def draw_employee_badges(surf, font_badge, font_tiny, employees, zone_rect, employee_colors):
    """Draw employee avatar badges inside a zone, auto-arranged."""
    x, y, w, h = zone_rect
    if not employees:
        return

    badge_r = 20          # radius
    badge_d = badge_r * 2
    pad     = 6
    cols    = max(1, (w - pad) // (badge_d + pad))

    for idx, emp in enumerate(employees):
        col = idx % cols
        row = idx // cols

        bx = x + pad + col * (badge_d + pad) + badge_r
        by = y + h - pad - badge_r - row * (badge_d + pad + 4)
        if by - badge_r < y + 8:
            break

        bg, acc = employee_colors.get(emp, (EMPLOYEE_BADGE_COLORS[0][0], EMPLOYEE_BADGE_COLORS[0][1]))

        # drop shadow
        pygame.draw.circle(surf, (0, 0, 0, 60), (bx + 2, by + 2), badge_r)
        # filled circle
        pygame.draw.circle(surf, bg,  (bx, by), badge_r)
        pygame.draw.circle(surf, acc, (bx, by), badge_r, 2)

        # Initials (up to 3 chars)
        initials = emp[:3]
        txt = font_badge.render(initials, True, TEXT_LIGHT)
        surf.blit(txt, (bx - txt.get_width() // 2, by - txt.get_height() // 2))


# ══════════════════════════════════════════════════════════════════
#  HEADER / LEGEND
# ══════════════════════════════════════════════════════════════════
def draw_header(surf, font_title, font_info, font_small, date, h, tick):
    import datetime as dt
    header_h = 72
    pygame.draw.rect(surf, BG_PANEL, (0, 0, WIDTH, header_h))
    pygame.draw.line(surf, (85, 88, 78), (0, header_h), (WIDTH, header_h), 2)

    # Title
    title = font_title.render("Вкусно и точка", True, (240, 230, 200))
    surf.blit(title, (20, 12))

    subtitle = font_small.render("Расписание сотрудников по станциям", True, (150, 145, 130))
    surf.blit(subtitle, (22, 44))

    # Datetime
    try:
        d = dt.date.fromisoformat(date)
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        wday = weekdays[d.weekday()]
    except Exception:
        wday = ''

    time_str = f"{wday},  {date}   {str(h).zfill(2)}:00"
    ts = font_info.render(time_str, True, (240, 200, 80))
    surf.blit(ts, (WIDTH - ts.get_width() - 20, 10))

    # Progress bar
    total_hours = 16
    hour_idx    = h - 7
    bar_x, bar_y, bar_w, bar_h = WIDTH - ts.get_width() - 20, 44, ts.get_width(), 8
    pygame.draw.rect(surf, (60, 60, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    fill = int(bar_w * hour_idx / total_hours)
    if fill > 0:
        pygame.draw.rect(surf, (230, 180, 50), (bar_x, bar_y, fill, bar_h), border_radius=4)
    pygame.draw.rect(surf, (100, 90, 50), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    hour_labels_font = font_small
    for i in range(0, total_hours + 1, 2):
        lx = bar_x + int(bar_w * i / total_hours)
        lbl = hour_labels_font.render(str(7 + i), True, (110, 105, 90))
        surf.blit(lbl, (lx - lbl.get_width() // 2, bar_y + 12))


def draw_legend(surf, font_badge, font_small, current_employees):
    """Bottom strip: zone chips + employee count."""
    leg_h  = 48
    leg_y  = HEIGHT - leg_h
    pygame.draw.rect(surf, BG_PANEL, (0, leg_y, WIDTH, leg_h))
    pygame.draw.line(surf, (85, 88, 78), (0, leg_y), (WIDTH, leg_y), 2)

    cx = 20
    for key in STATIONS:
        zc = ZONE_COLORS[key]
        chip_w = 36
        draw_rrect(surf, zc['label_bg'], (cx, leg_y + 10, chip_w, 28), r=6)
        lbl = font_badge.render(key, True, TEXT_LIGHT)
        surf.blit(lbl, (cx + chip_w//2 - lbl.get_width()//2, leg_y + 10 + (28 - lbl.get_height())//2))
        cx += chip_w + 4

        name_lbl = font_small.render(zc['name'], True, (190, 185, 175))
        surf.blit(name_lbl, (cx, leg_y + 10 + (28 - name_lbl.get_height())//2))
        cx += name_lbl.get_width() + 28

    # Total
    total = sum(len(v) for v in current_employees.values())
    total_lbl = font_badge.render(f"Итого: {total}", True, (220, 215, 200))
    surf.blit(total_lbl, (WIDTH - total_lbl.get_width() - 20, leg_y + (leg_h - total_lbl.get_height())//2))


def draw_zone_label(surf, font_zone, font_name, key, zone_rect, count=0):
    x, y, w, h = zone_rect
    zc   = ZONE_COLORS[key]
    name = zc['name']

    key_txt   = font_zone.render(key,  True, TEXT_LIGHT)
    name_txt  = font_name.render(name, True, TEXT_LIGHT)
    count_str = str(count)
    count_txt = font_name.render(count_str, True, TEXT_LIGHT)

    pad_x     = 14
    pad_y     = 6
    inner_gap = 8
    # circle badge dimensions
    cbadge_r  = max(12, count_txt.get_height() // 2 + 4)
    cbadge_d  = cbadge_r * 2

    badge_w = (pad_x
               + key_txt.get_width() + inner_gap
               + name_txt.get_width() + inner_gap
               + cbadge_d + pad_x)
    badge_h = max(key_txt.get_height(), name_txt.get_height(), cbadge_d) + pad_y * 2

    lx = x + w // 2 - badge_w // 2
    ly = y + 10

    shadow_rect(surf, (lx, ly, badge_w, badge_h), offset=3, alpha=80)
    draw_rrect(surf, zc['label_bg'], (lx, ly, badge_w, badge_h), r=8)

    mid_y = ly + badge_h // 2

    # Key (bold, left)
    surf.blit(key_txt, (lx + pad_x, mid_y - key_txt.get_height() // 2))

    # Divider after key
    div1_x = lx + pad_x + key_txt.get_width() + inner_gap // 2
    pygame.draw.line(surf, (255, 255, 255, 80),
                     (div1_x, ly + 6), (div1_x, ly + badge_h - 6), 1)

    # Name
    name_x = div1_x + inner_gap // 2
    surf.blit(name_txt, (name_x, mid_y - name_txt.get_height() // 2))

    # Divider after name
    div2_x = name_x + name_txt.get_width() + inner_gap // 2
    pygame.draw.line(surf, (255, 255, 255, 80),
                     (div2_x, ly + 6), (div2_x, ly + badge_h - 6), 1)

    # Count circle badge
    cx_badge = div2_x + inner_gap // 2 + cbadge_r
    cy_badge = mid_y
    # darker circle bg
    darker_bg = tuple(max(0, c - 35) for c in zc['label_bg'])
    pygame.draw.circle(surf, darker_bg, (cx_badge, cy_badge), cbadge_r)
    pygame.draw.circle(surf, TEXT_LIGHT, (cx_badge, cy_badge), cbadge_r, 1)
    surf.blit(count_txt, (cx_badge - count_txt.get_width() // 2,
                           cy_badge - count_txt.get_height() // 2))


# ══════════════════════════════════════════════════════════════════
#  MAIN FLOOR PLAN LAYOUT
# ══════════════════════════════════════════════════════════════════
# Matches reference: K=top wide, BVR/C/FF=middle row, TS=bottom wide

HEADER_H = 74
FOOTER_H = 50
WALL     = 18   # outer wall thickness
MARGIN_X = 28
MARGIN_Y = 14

def compute_zones():
    """
    Building area inside outer walls:
      top    = HEADER_H + WALL + MARGIN_Y
      bottom = HEIGHT - FOOTER_H - WALL - MARGIN_Y
      left   = WALL + MARGIN_X
      right  = WIDTH - WALL - MARGIN_X
    """
    bldg_x = WALL + MARGIN_X
    bldg_y = HEADER_H + WALL + MARGIN_Y
    bldg_w = WIDTH  - 2 * (WALL + MARGIN_X)
    bldg_h = HEIGHT - HEADER_H - FOOTER_H - 2 * (WALL + MARGIN_Y)

    inner_gap = 6   # gap between zones

    # Row heights
    k_h  = int(bldg_h * 0.36)
    ts_h = int(bldg_h * 0.38)
    mid_h = bldg_h - k_h - ts_h - 2 * inner_gap

    # Top row: K spans full width
    k_rect = (bldg_x, bldg_y, bldg_w, k_h)

    # Middle row split: BVR 30% | C 38% | FF 32%
    mid_y = bldg_y + k_h + inner_gap
    bvr_w = int(bldg_w * 0.30)
    ff_w  = int(bldg_w * 0.30)
    c_w   = bldg_w - bvr_w - ff_w - 2 * inner_gap

    bvr_rect = (bldg_x,                          mid_y, bvr_w, mid_h)
    c_rect   = (bldg_x + bvr_w + inner_gap,      mid_y, c_w,   mid_h)
    ff_rect  = (bldg_x + bvr_w + c_w + 2*inner_gap, mid_y, ff_w, mid_h)

    # Bottom row: TS spans full width
    ts_y   = mid_y + mid_h + inner_gap
    ts_rect = (bldg_x, ts_y, bldg_w, ts_h)

    return {
        'K':   k_rect,
        'BVR': bvr_rect,
        'C':   c_rect,
        'FF':  ff_rect,
        'TS':  ts_rect,
    }, (bldg_x, bldg_y, bldg_w, bldg_h)


DECO_FNS = {
    'K':   draw_kitchen_deco,
    'BVR': draw_bvr_deco,
    'C':   draw_counter_deco,
    'FF':  draw_ff_deco,
    'TS':  draw_ts_deco,
}


def draw_building(surf, zone_rects, bldg_rect, font_zone, font_name, font_badge, font_tiny,
                  current_employees, employee_colors):
    bx, by, bw, bh = bldg_rect

    # ── Outer wall (brown) ──
    outer = (bx - WALL, by - WALL, bw + 2*WALL, bh + 2*WALL)
    draw_rrect(surf, (90, 60, 38), outer, r=10)
    draw_rrect(surf, (70, 45, 25), outer, r=10, border_color=(55,35,15), border_w=3)

    # ── Each zone ──
    for key in STATIONS:
        rect = zone_rects[key]
        zc   = ZONE_COLORS[key]

        # floor — solid light fill + subtle tile grid
        pygame.draw.rect(surf, zc['fill'], rect, border_radius=6)
        # tile grid lines slightly darker than fill
        grid_color = tuple(max(0, c - 18) for c in zc['fill'])
        rx, ry, rw, rh = rect
        # clip grid lines inside rounded rect
        clip_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(clip_surf, (255,255,255,255), (0,0,rw,rh), border_radius=6)
        grid_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
        for gx in range(0, rw, 22):
            pygame.draw.line(grid_surf, grid_color + (255,), (gx, 0), (gx, rh), 1)
        for gy in range(0, rh, 22):
            pygame.draw.line(grid_surf, grid_color + (255,), (0, gy), (rw, gy), 1)
        grid_surf.blit(clip_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(grid_surf, (rx, ry))

        # border
        draw_rrect(surf, (0,0,0,0), rect, r=6,
                   border_color=zc['border'], border_w=3)

        # decorative furniture
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(rect))
        DECO_FNS[key](surf, rect)
        surf.set_clip(clip)

        # Zone label badge (center-top)
        count = len(current_employees.get(key, []))
        draw_zone_label(surf, font_zone, font_name, key, rect, count=count)

        # Employee badges (bottom area)
        draw_employee_badges(surf, font_badge, font_tiny,
                             current_employees.get(key, []),
                             rect, employee_colors)


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Вкусно и точка — Расписание")

    def sys_font(size, bold=False):
        for name in ['dejavusans', 'arial', 'freesansbold', 'freesans']:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.Font(None, size)

    font_title = sys_font(32, bold=True)
    font_info  = sys_font(26)
    font_zone  = sys_font(22, bold=True)
    font_name  = sys_font(18)
    font_badge = sys_font(16, bold=True)
    font_small = sys_font(15)
    font_tiny  = sys_font(13)

    clock = pygame.time.Clock()
    datetimes, employees_shifts = read_data()

    # Assign stable colours to employees
    all_emps = sorted(employees_shifts.keys())
    employee_colors = {
        emp: EMPLOYEE_BADGE_COLORS[i % len(EMPLOYEE_BADGE_COLORS)]
        for i, emp in enumerate(all_emps)
    }

    zone_rects, bldg_rect = compute_zones()
    tick = 0
    cur  = 0

    PAUSE_START     = FPS * 2      # 2 секунды перед началом
    PAUSE_DAY_BREAK = FPS * 2      # 2 секунды между днями
    PAUSE_END       = FPS * 3      # 3 секунды в конце

    pause_frames_left = PAUSE_START   # начальная пауза
    last_date         = None

    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def render_frame(date, h, empty=False):
        """Отрисовать кадр. При empty=True — зоны без сотрудников."""
        screen.fill(BG_OUTSIDE)
        for ry in range(0, HEIGHT, 48):
            pygame.draw.line(screen, (70, 74, 70), (0, ry), (WIDTH, ry), 1)
        ce = {} if empty else get_current_employees(date, h, employees_shifts)
        draw_header(screen, font_title, font_info, font_small, date, h, tick)
        draw_building(screen, zone_rects, bldg_rect, font_zone, font_name, font_badge, font_tiny,
                      ce, employee_colors)
        draw_legend(screen, font_badge, font_small, ce)

    def draw_center_banner(line1_text, line2_text, line1_color=(240, 200, 80), line2_color=(220, 215, 200)):
        """Полупрозрачный баннер по центру экрана."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        # Рамка баннера
        bw, bh = 520, 110
        bx = WIDTH  // 2 - bw // 2
        by = HEIGHT // 2 - bh // 2
        draw_rrect(screen, (30, 34, 30), (bx, by, bw, bh), r=14)
        draw_rrect(screen, (0, 0, 0, 0),  (bx, by, bw, bh), r=14,
                   border_color=(90, 85, 60), border_w=2)

        l1 = font_title.render(line1_text, True, line1_color)
        l2 = font_info.render(line2_text,  True, line2_color)
        cx = WIDTH // 2
        cy = HEIGHT // 2
        screen.blit(l1, (cx - l1.get_width() // 2, cy - l1.get_height() - 4))
        screen.blit(l2, (cx - l2.get_width() // 2, cy + 4))

    def pause(frames, draw_fn):
        """Показывать draw_fn() в течение frames тиков; выход по Esc/закрытие."""
        for _ in range(frames):
            if not handle_events():
                pygame.quit(); sys.exit()
            draw_fn()
            pygame.display.flip()
            clock.tick(FPS)

    def get_weekday(date):
        import datetime as dt
        try:
            d = dt.date.fromisoformat(date)
            return ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                    'Пятница', 'Суббота', 'Воскресенье'][d.weekday()]
        except Exception:
            return ''

    running = True

    # ── Начальная пауза: пустой ресторан + баннер «Начало недели» ──
    first_date = datetimes[0][0]
    def draw_start():
        render_frame(first_date, 7, empty=True)
        draw_center_banner("Начало недели", f"{get_weekday(first_date)}, {first_date}")
    pause(PAUSE_START, draw_start)

    while running:
        if not handle_events():
            break

        date, h = datetimes[cur]

        # ── Пауза между днями: пустой ресторан + баннер нового дня ──
        if date != last_date and last_date is not None:
            def draw_day_break(d=date):
                render_frame(d, 7, empty=True)
                draw_center_banner(get_weekday(d), d)
            pause(PAUSE_DAY_BREAK, draw_day_break)

        last_date = date

        render_frame(date, h)
        pygame.display.flip()
        clock.tick(FPS)
        tick += 1
        cur  += 1

        # ── Финальная пауза: пустой ресторан + баннер «Конец недели» ──
        if cur >= len(datetimes):
            last_d = datetimes[-1][0]
            def draw_end(d=last_d):
                render_frame(d, 22, empty=True)
                draw_center_banner("Конец недели", "До следующей смены!", (180, 220, 180))
            pause(PAUSE_END, draw_end)
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()