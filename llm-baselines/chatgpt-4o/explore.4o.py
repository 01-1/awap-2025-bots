
# Aggressive Bot
# Focuses on attacking enemy units aggressively

from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
# Explorer Bot
# Moves units around to uncover the map

class BotPlayer(Player):
    def __init__(self, map: Map):
        pass
    
    def play_turn(self, rc: RobotController):
        for unit in rc.get_units(rc.get_ally_team()):
            for direction in Direction:
                if rc.can_move(unit, direction):
                    rc.move(unit, direction)
                    break
