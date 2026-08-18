from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building

class BotPlayer(Player):
    def __init__(self, map: Map):
        pass
    
    def play_turn(self, rc: RobotController):
        # Spawn Rats
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.RAT, building.id):
                rc.spawn_unit(UnitType.RAT, building.id)

        # Sabotage enemy farms
        for unit in rc.get_units(rc.get_ally_team()):
            if unit.type == UnitType.RAT:
                if rc.can_harm_farm(unit.id):
                    rc.harm_farm(unit.id)
