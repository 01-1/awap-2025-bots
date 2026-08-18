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
        # Build Explorer Buildings
        for x in range(rc.get_map().width):
            for y in range(rc.get_map().height):
                if rc.can_build_building(BuildingType.EXPLORER_BUILDING, x, y):
                    rc.build_building(BuildingType.EXPLORER_BUILDING, x, y)

        # Spawn Explorers
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.EXPLORER, building.id):
                rc.spawn_unit(UnitType.EXPLORER, building.id)

        # Perform explorations
        for unit in rc.get_units(rc.get_ally_team()):
            if unit.type == UnitType.EXPLORER:
                for building in rc.get_buildings(rc.get_ally_team()):
                    if rc.can_explore(unit.id, building.id):
                        rc.explore_for_gold(unit.id, building.id)
                        rc.explore_for_health(unit.id, building.id, unit.id)
