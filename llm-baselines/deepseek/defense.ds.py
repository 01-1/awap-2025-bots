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
        # Build farms and upgrade them
        for x in range(rc.get_map().width):
            for y in range(rc.get_map().height):
                if rc.can_build_building(BuildingType.FARM_1, x, y):
                    rc.build_building(BuildingType.FARM_1, x, y)
                elif rc.can_build_building(BuildingType.FARM_2, x, y):
                    rc.build_building(BuildingType.FARM_2, x, y)

        # Spawn Defenders and Healers
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.DEFENDER, building.id):
                rc.spawn_unit(UnitType.DEFENDER, building.id)
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, building.id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, building.id)

        # Heal nearby units
        for unit in rc.get_units(rc.get_ally_team()):
            if unit.type == UnitType.LAND_HEALER_1:
                for ally_unit in rc.get_units(rc.get_ally_team()):
                    if rc.can_heal_unit(unit.id, ally_unit.id):
                        rc.heal_unit(unit.id, ally_unit.id)
