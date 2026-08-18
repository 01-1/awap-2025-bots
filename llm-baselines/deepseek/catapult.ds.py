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
        # Spawn Catapults
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.CATAPULT, building.id):
                rc.spawn_unit(UnitType.CATAPULT, building.id)

        # Attack enemy buildings and units
        for unit in rc.get_units(rc.get_ally_team()):
            if unit.type == UnitType.CATAPULT:
                enemy_buildings = rc.get_buildings(rc.get_enemy_team())
                if enemy_buildings:
                    target = enemy_buildings[0]
                    if rc.can_unit_attack_building(unit.id, target.id):
                        rc.unit_attack_building(unit.id, target.id)
