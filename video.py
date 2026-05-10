import pygame
import sys
from collections import defaultdict

WIDTH, HEIGHT = 1000, 500
FPS = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

STATIONS = ['BVR', 'C', 'FF', 'K', 'TS']
STATION_NAMES = {'BVR': 'Напитки', 'C': 'Прилавок', 'FF': 'Картофель', 'K': 'Кухня', 'TS': 'Зал'}
ZONE_WIDTH = (WIDTH - 20 * (len(STATIONS) + 1)) // len(STATIONS)
ZONE_HEIGHT = (HEIGHT - 150)


def read_data():
    datetimes = []
    for date in ['2026-04-27', '2026-04-28', '2026-04-29', '2026-04-30', '2026-05-01', '2026-05-02',
                 '2026-05-03']:
        for h in range(7, 23):
            datetimes.append((date, h))
    employees_shits = defaultdict(dict)
    with open('schedule_result.csv', 'r') as f:
        for line in f.readlines()[1:]:
            ds, station_key, employee_id, starttime, finishtime = line.split(';')
            employees_shits[employee_id][ds] = (int(starttime), int(finishtime), station_key)

    return datetimes, employees_shits


def draw_zones(screen, font):
    for i, zone in enumerate(STATIONS):
        pygame.draw.rect(screen, BLACK, (20 + (ZONE_WIDTH + 20) * i, 100, ZONE_WIDTH, ZONE_HEIGHT), 1)

        text_surface = font.render(f"{zone} ({STATION_NAMES[zone]})", True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.left = 20 + (ZONE_WIDTH + 20) * i
        text_rect.top = 70
        screen.blit(text_surface, text_rect)

def draw_employees(screen, font, current_employees):
    for i, zone in enumerate(STATIONS):
        employees = current_employees[zone]
        employee_count = 0
        zone_left = 20 + (ZONE_WIDTH + 20) * i
        for employee in employees:
            text_surface = font.render(employee, True, BLACK)
            text_rect = text_surface.get_rect()
            text_rect.left = 10 + zone_left + 50 * (employee_count % 3)
            text_rect.top = 110 + 50 * (employee_count // 3)
            screen.blit(text_surface, text_rect)
            employee_count += 1

def get_current_employees(date, h, employees_shits):
    res = defaultdict(list)
    for employee_id in employees_shits:
        if date in employees_shits[employee_id]:
            if employees_shits[employee_id][date][0] <= h <= employees_shits[employee_id][date][1]:
                res[employees_shits[employee_id][date][2]].append(employee_id)
    return res


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Визуализация")

    font = pygame.font.Font(None, 36)

    clock = pygame.time.Clock()

    datetimes, employees_shifts = read_data()

    running = True
    current_datetime = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        date = datetimes[current_datetime][0]
        h = datetimes[current_datetime][1]
        text_surface = font.render(date + ' ' + str(h).rjust(2, '0') + ':00', True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.left = 20
        text_rect.top = 20
        screen.blit(text_surface, text_rect)

        draw_zones(screen, font)

        current_employees = get_current_employees(date, h, employees_shifts)
        draw_employees(screen, font, current_employees)

        pygame.display.flip()
        clock.tick(FPS)
        current_datetime += 1
        if current_datetime > len(datetimes) - 1:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
