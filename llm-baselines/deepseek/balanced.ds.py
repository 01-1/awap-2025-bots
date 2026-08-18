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
        # Build farms
        for x in range(rc.get_map().width):
            for y in range(rc.get_map().height):
                if rc.can_build_building(BuildingType.FARM_1, x, y):
                    rc.build_building(BuildingType.FARM_1, x, y)

        # Spawn a mix of units
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.KNIGHT, building.id):
                rc.spawn_unit(UnitType.KNIGHT, building.id)
            if rc.can_spawn_unit(UnitType.DEFENDER, building.id):
                rc.spawn_unit(UnitType.DEFENDER, building.id)

        # Attack enemy units
        for unit in rc.get_units(rc.get_ally_team()):
            enemy_units = rc.get_units(rc.get_enemy_team())
            if enemy_units:
                target = enemy_units[0]
                if rc.can_unit_attack_unit(unit.id, target.id):
                    rc.unit_attack_unit(unit.id, target.id)
