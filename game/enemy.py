import random
import time

from config import ROOM_GRAPH


class EnemyAI:
    def __init__(self) -> None:
        self.position = "main-stage"
        self.at_door = False
        self.ai_level = 1
        self.last_move_time = time.time()

    def move_enemy(self, hour: int) -> None:
        now = time.time()
        if now - self.last_move_time < 4:
            return
        self.last_move_time = now

        ai_level = self.ai_level + hour
        move_chance = min(0.1 * ai_level, 0.80)

        if random.random() > move_chance:
            return

        current = self.position
        options = ROOM_GRAPH.get(current, [])
        if not options:
            return

        forward_rooms = [r for r in options if r != "main-stage"]
        retreat_rooms = [r for r in options if r not in ["office"]]

        if current in ["left-hall", "right-hall"] and random.random() < 0.3:
            self.position = random.choice(retreat_rooms)
        elif current == "dining" and random.random() < 0.2:
            pass
        else:
            self.position = random.choice(forward_rooms or options)

        if self.position == "office":
            self.at_door = True

    def reset(self) -> None:
        self.position = "main-stage"
        self.at_door = False
