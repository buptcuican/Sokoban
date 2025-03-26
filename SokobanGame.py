import pygame
import sys
from pygame.locals import *

# 初始化 Pygame
pygame.init()

# 颜色定义
WALL_COLOR = (100, 100, 100)
FLOOR_COLOR = (200, 200, 200)
GRID_COLOR = (180, 180, 180)
PLAYER_COLOR = (255, 0, 0)
BOX_COLOR = (139, 69, 19)
BOX_ON_TARGET_COLOR = (255, 165, 0)
TARGET_COLOR = (0, 0, 255)
TEXT_COLOR = (0, 255, 0)
FAIL_COLOR = (255, 0, 0)

# 关卡配置
LEVELS = [
    [
        "##########",
        "#     O  #",
        "# P  B   #",
        "#        #",
        "##########",
    ],
    [
        "##########",
        "#   O   O#",
        "#  B B  P#",
        "#        #",
        "##########",
    ],
    [
        "#########",
        "#  O   P#",
        "# B##B  #",
        "#   O  ##",
        "#########",
    ]
]


class SokobanGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), FULLSCREEN)
        self.fullscreen = True
        pygame.display.set_caption("SokobanGame - Stage 1")
        self.clock = pygame.time.Clock()
        self.current_level = 0
        self.init_game()
        self.win_time = 0
        self.fail_time = 0
        
        self.last_state = None
        self.final_victory = False  # 新增最终胜利状态

    def init_game(self):
        map_data = LEVELS[self.current_level]
        self.game_state = self.parse_map(map_data)
        self.cell_size = self.calculate_cell_size()
        self.game_over = False
        self.victory = False
        self.last_state = None
        self.final_victory = False  # 重置最终胜利状态

    def parse_map(self, map_data):
        elements = {
            "walls": [],
            "player": (0, 0),
            "boxes": [],
            "targets": []
        }

        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == "#":
                    elements["walls"].append((x, y))
                elif char == "P":
                    elements["player"] = (x, y)
                elif char == "B":
                    elements["boxes"].append((x, y))
                elif char == "O":
                    elements["targets"].append((x, y))
        return elements

    def calculate_cell_size(self):
        width, height = self.screen.get_size()
        max_cols = max(len(row) for row in LEVELS[self.current_level])
        max_rows = len(LEVELS[self.current_level])
        return min(width // max_cols, height // max_rows)

    def draw_player(self, x, y):
        size = self.cell_size
        pygame.draw.rect(self.screen, PLAYER_COLOR,
                         (x * size + size // 4, y * size + size // 2,
                          size // 2, size // 2))
        pygame.draw.circle(self.screen, PLAYER_COLOR,
                           (x * size + size // 2, y * size + size // 3),
                           size // 4)
        pygame.draw.line(self.screen, PLAYER_COLOR,
                         (x * size + size // 2, y * size + 3 * size // 4),
                         (x * size + size // 4, y * size + size), 3)
        pygame.draw.line(self.screen, PLAYER_COLOR,
                         (x * size + size // 2, y * size + 3 * size // 4),
                         (x * size + 3 * size // 4, y * size + size), 3)

    def draw_target(self, x, y):
        size = self.cell_size
        pygame.draw.line(self.screen, TARGET_COLOR,
                         (x * size + size // 4, y * size + size // 4),
                         (x * size + 3 * size // 4, y * size + 3 * size // 4), 3)
        pygame.draw.line(self.screen, TARGET_COLOR,
                         (x * size + 3 * size // 4, y * size + size // 4),
                         (x * size + size // 4, y * size + 3 * size // 4), 3)

    def draw(self):
        self.screen.fill(FLOOR_COLOR)
        size = self.cell_size

        # 绘制网格
        for y in range(len(LEVELS[self.current_level])):
            for x in range(len(LEVELS[self.current_level][y])):
                rect = pygame.Rect(x * size, y * size, size, size)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        # 绘制墙壁
        for x, y in self.game_state["walls"]:
            pygame.draw.rect(self.screen, WALL_COLOR,
                             (x * size, y * size, size, size))

        # 绘制目标点
        for x, y in self.game_state["targets"]:
            self.draw_target(x, y)

        # 绘制箱子
        for x, y in self.game_state["boxes"]:
            color = BOX_ON_TARGET_COLOR if (x, y) in self.game_state["targets"] else BOX_COLOR
            pygame.draw.rect(self.screen, color,
                             (x * size + 2, y * size + 2,
                              size - 4, size - 4), 0, 5)

        # 绘制玩家
        px, py = self.game_state["player"]
        self.draw_player(px, py)

        # 状态互斥显示逻辑（新增）
        current_state = None
        if self.final_victory:
            current_state = "final"
        elif self.victory:
            current_state = "victory"
        elif self.game_over:
            current_state = "fail"

        # 仅在状态变化时清除旧提示
        if current_state != self.last_state:
            self.screen.fill(FLOOR_COLOR)  # 清除旧内容
            self.last_state = current_state

        # 优先绘制最终胜利提示
        if self.final_victory:
            self.show_message("You have passed all the stages", TEXT_COLOR)
        elif self.victory:
            if self.current_level == len(LEVELS) - 1:
                self.show_message(".", TEXT_COLOR)
            else:
                self.show_message("You passed! You will go into next stage after 3 seconds.", TEXT_COLOR)
        elif self.game_over:
            if pygame.time.get_ticks() - self.fail_time > 3000:
                self.show_message("Press any button to restart.", FAIL_COLOR)
            else:
                self.show_message("You failed! ", FAIL_COLOR)


        pygame.display.flip()

    def show_message(self, text, color):
        font = pygame.font.Font(None, 36)
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surf, text_rect)

    def move_player(self, dx, dy):
        if self.victory or self.game_over:
            return

        px, py = self.game_state["player"]
        new_x, new_y = px + dx, py + dy

        if (new_x, new_y) in self.game_state["walls"]:
            return

        if (new_x, new_y) in self.game_state["boxes"]:
            box_new_x, box_new_y = new_x + dx, new_y + dy
            if (box_new_x, box_new_y) in self.game_state["walls"] or \
                    (box_new_x, box_new_y) in self.game_state["boxes"]:
                return
            self.game_state["boxes"].remove((new_x, new_y))
            self.game_state["boxes"].append((box_new_x, box_new_y))

        self.game_state["player"] = (new_x, new_y)
        self.check_game_state()

    def check_game_state(self):
        # 胜利检测
        if all(pos in self.game_state["boxes"] for pos in self.game_state["targets"]):
            self.victory = True
            self.game_over = False  # 新增：清除失败状态
            self.win_time = pygame.time.get_ticks()

            # 如果是最后一关直接标记最终胜利
            if self.current_level == len(LEVELS) - 1:
                self.final_victory = True
            else:
                pygame.display.set_caption(f"SokobanGame -  Stage {self.current_level + 2}")
            return

        # 失败检测
        for box in self.game_state["boxes"]:
            if box not in self.game_state["targets"] and self.is_box_stuck(box):
                self.game_over = True
                self.victory = False  # 新增：清除胜利状态
                self.fail_time = pygame.time.get_ticks()
                return

    def is_box_stuck(self, box):
        x, y = box
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        movable = False

        for dx, dy in directions:
            adj_pos = (x + dx, y + dy)
            opposite_pos = (x - dx, y - dy)
            if adj_pos not in self.game_state["walls"] and \
                    adj_pos not in self.game_state["boxes"] and \
                    opposite_pos not in self.game_state["walls"] and \
                    opposite_pos not in self.game_state["boxes"]:
                movable = True
                break
        return not movable

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                # 失败后且超过3秒时，任意键重试
                if self.game_over and pygame.time.get_ticks() - self.fail_time > 3000:
                    self.init_game()
                    return

                if event.key == K_UP:
                    self.move_player(0, -1)
                elif event.key == K_DOWN:
                    self.move_player(0, 1)
                elif event.key == K_LEFT:
                    self.move_player(-1, 0)
                elif event.key == K_RIGHT:
                    self.move_player(1, 0)
                elif event.key == K_f:
                    self.toggle_fullscreen()
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), RESIZABLE)
                self.cell_size = self.calculate_cell_size()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0), FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (800, 600), RESIZABLE)
        self.cell_size = self.calculate_cell_size()

    def run(self):
        while True:
            self.handle_events()
            self.clock.tick(60)

            # 最终胜利处理
            if self.final_victory:
                self.draw()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()

            # 普通胜利处理
            if self.victory and pygame.time.get_ticks() - self.win_time > 3000:
                if self.current_level < len(LEVELS) - 1:
                    self.current_level += 1
                    self.init_game()
                else:
                    self.final_victory = True  # 触发最终胜利状态

            self.draw()


if __name__ == "__main__":
    game = SokobanGame()
    game.run()