from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
import random

class BotPlayer(Player):
    def __init__(self, map: Map):
        pass
    
    def play_turn(self, rc: RobotController):
        for unit in rc.get_units(rc.get_ally_team()):
            action = random.choice(["move", "attack", "build"])
            if action == "move":
                direction = random.choice(list(Direction))
                if rc.can_move(unit, direction):
                    rc.move(unit, direction)
            elif action == "attack":
                enemies = rc.get_visible_enemies(unit)
                if enemies:
                    rc.attack(unit, random.choice(enemies))
            elif action == "build" and rc.can_build(unit, BuildingType.FACTORY):
                rc.build(unit, BuildingType.FACTORY)
