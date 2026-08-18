from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
import random

# Configurable proportions
KNIGHT_PROPORTION = 0.6
WARRIOR_PROPORTION = 0.3
LAND_HEALER_PROPORTION = 0.1

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map

    def play_turn(self, rc: RobotController):
        team = rc.get_ally_team()
        ally_castle_id = -1

        ally_buildings = rc.get_buildings(team)
        for building in ally_buildings:
            if building.type == BuildingType.MAIN_CASTLE:
                ally_castle_id = rc.get_id_from_building(building)[1]
                break

        enemy = rc.get_enemy_team()
        enemy_castle_id = -1

        enemy_buildings = rc.get_buildings(enemy)
        for building in enemy_buildings:
            if building.type == BuildingType.MAIN_CASTLE:
                enemy_castle_id = rc.get_id_from_building(building)[1]
                break

        enemy_castle = rc.get_building_from_id(enemy_castle_id)
        if enemy_castle is None:
            return

        # Get current unit counts
        units = rc.get_units(team)
        total_units = len(units)
        if total_units == 0:
            if rc.can_spawn_unit(UnitType.KNIGHT, ally_castle_id):
                rc.spawn_unit(UnitType.KNIGHT, ally_castle_id)
        else:
            # Calculate current proportions
            knights = sum(1 for u in units if u.type == UnitType.KNIGHT)
            warriors = sum(1 for u in units if u.type == UnitType.WARRIOR)
            healers = sum(1 for u in units if u.type == UnitType.LAND_HEALER_1)

            # Random choice based on proportions
            roll = random.random()
            if roll < KNIGHT_PROPORTION and rc.can_spawn_unit(UnitType.KNIGHT, ally_castle_id):
                rc.spawn_unit(UnitType.KNIGHT, ally_castle_id)
            elif roll < KNIGHT_PROPORTION + WARRIOR_PROPORTION and rc.can_spawn_unit(UnitType.WARRIOR, ally_castle_id):
                rc.spawn_unit(UnitType.WARRIOR, ally_castle_id)
            elif rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id)

        # Loop through all the units
        healers = []
        for unit_id in rc.get_unit_ids(team):
            unit = rc.get_unit_from_id(unit_id)
            if unit is None:
                return

            # Manage healers
            if unit.type == UnitType.LAND_HEALER_1:
                healers.append(unit)

            # Heal units occasionally
            if random.random() < LAND_HEALER_PROPORTION and len(healers) > 0:
                for healer in healers:
                    if rc.can_heal_unit(unit_id, healer):
                        rc.heal_unit(unit_id, healer)

            # Attack castle if possible
            if enemy_castle_id in rc.get_building_ids(enemy) and rc.can_unit_attack_building(unit_id, enemy_castle_id):
                rc.unit_attack_building(unit_id, enemy_castle_id)

            # Move toward castle
            possible_move_dirs = rc.unit_possible_move_directions(unit_id)
            possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))
            best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
            if rc.can_move_unit_in_direction(unit_id, best_dir):
                rc.move_unit_in_direction(unit_id, best_dir)
