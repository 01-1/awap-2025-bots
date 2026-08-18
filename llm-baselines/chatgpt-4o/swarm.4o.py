
# Aggressive Bot
# Focuses on attacking enemy units aggressively

from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
# Swarm Bot
# Creates many units for an overwhelming attack

class BotPlayer(Player):
    def __init__(self, map: Map):
        pass
    
    def play_turn(self, rc: RobotController):
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_produce_unit(building, UnitType.SOLDIER):
                rc.produce_unit(building, UnitType.SOLDIER)
