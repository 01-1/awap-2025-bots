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
        # Spawn as many cheap units as possible
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.KNIGHT, building.id):
                rc.spawn_unit(UnitType.KNIGHT, building.id)
            if rc.can_spawn_unit(UnitType.WARRIOR, building.id):
                rc.spawn_unit(UnitType.WARRIOR, building.id)

        # Attack enemy units and castles
        for unit in rc.get_units(rc.get_ally_team()):
            enemy_units = rc.get_units(rc.get_enemy_team())
            if enemy_units:
                target = enemy_units[0]  # Attack the first enemy unit
                if rc.can_unit_attack_unit(unit.id, target.id):
                    rc.unit_attack_unit(unit.id, target.id)
            else:
                # Attack enemy castles if no units are found
                enemy_buildings = rc.get_buildings(rc.get_enemy_team())
                if enemy_buildings:
                    target = enemy_buildings[0]
                    if rc.can_unit_attack_building(unit.id, target.id):
                        rc.unit_attack_building(unit.id, target.id)
