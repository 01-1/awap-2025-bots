from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
import random

# Configurable proportions for unit spawning
#WARRIOR_PROPORTION = 0.7  # 70% chance to spawn Warrior
#HEALER_PROPORTION = 0.3   # 30% chance to spawn Healer
SPAWNLOOP = 'WWWWHH'

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.last_unable_heal = False
        self.spawnloop_index = 0
    
    def play_turn(self, rc: RobotController):
        team = rc.get_ally_team()
        ally_castle_id = -1

        # Find the ally castle
        ally_buildings = rc.get_buildings(team)
        for building in ally_buildings:
            if building.type == BuildingType.MAIN_CASTLE:
                ally_castle_id = rc.get_id_from_building(building)[1]
                break

        ally_castle = rc.get_building_from_id(ally_castle_id)
        if ally_castle is None:
            return

        ally_castle_xy = (ally_castle.x, ally_castle.y)

        # Find the enemy castle
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

        # Decide whether to move units off the castle
        move_off = rc.get_balance(team) >= 2

        # Get enemy unit IDs for targeting
        enemy_unit_ids = rc.get_unit_ids(enemy)

        # Loop through all ally units
        healers = []  # Track healers for healing logic
        for unit_id in rc.get_unit_ids(team):
            unit = rc.get_unit_from_id(unit_id)
            if unit is None:
                continue

            # Track healers
            if unit.type == UnitType.LAND_HEALER_1:
                healers.append(unit)

            else:
                # Attack enemy castle if possible
                if enemy_castle_id in rc.get_building_ids(enemy) and rc.can_unit_attack_building(unit_id, enemy_castle_id):
                    rc.unit_attack_building(unit_id, enemy_castle_id)

                # Attack enemy units if possible
                for enemy_unit_id in enemy_unit_ids:
                    if rc.can_unit_attack_unit(unit_id, enemy_unit_id):
                        rc.unit_attack_unit(unit_id, enemy_unit_id)

            # Move units toward the enemy castle
            if (unit.x, unit.y) == ally_castle_xy and not move_off:
                continue

            possible_move_dirs = rc.unit_possible_move_directions(unit_id)
            possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))

            best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
            if rc.can_move_unit_in_direction(unit_id, best_dir):
                rc.move_unit_in_direction(unit_id, best_dir)

        # Heal nearby units
        for healer in healers:
            lowest_health = 9**9
            unit_to_heal = None

            for ally_unit in rc.get_units(team):
                if rc.can_heal_unit(healer.id, ally_unit.id):
                    if ally_unit.health < lowest_health:
                        lowest_health = ally_unit.health
                        unit_to_heal = ally_unit

            if unit_to_heal is not None:
                rc.heal_unit(healer.id, unit_to_heal.id)

        # Spawn units based on proportions
        if SPAWNLOOP[self.spawnloop_index % len(SPAWNLOOP)] == 'W':
            if rc.can_spawn_unit(UnitType.WARRIOR, ally_castle_id):
                rc.spawn_unit(UnitType.WARRIOR, ally_castle_id)
                self.spawnloop_index += 1
        else:
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id)
                self.spawnloop_index += 1


# The above code was modified from the following DeepSeek LLM generated code.

#   from src.player import Player
#   from src.map import Map
#   from src.robot_controller import RobotController
#   from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
#   from src.units import Unit
#   from src.buildings import Building
#   import random

#   # Configurable proportions for unit spawning
#   WARRIOR_PROPORTION = 0.7  # 70% chance to spawn Warrior
#   HEALER_PROPORTION = 0.3   # 30% chance to spawn Healer

#   class BotPlayer(Player):
#       def __init__(self, map: Map):
#           self.map = map
#       
#       def play_turn(self, rc: RobotController):
#           team = rc.get_ally_team()
#           ally_castle_id = -1

#           # Find the ally castle
#           ally_buildings = rc.get_buildings(team)
#           for building in ally_buildings:
#               if building.type == BuildingType.MAIN_CASTLE:
#                   ally_castle_id = rc.get_id_from_building(building)[1]
#                   break

#           ally_castle = rc.get_building_from_id(ally_castle_id)
#           if ally_castle is None:
#               return

#           ally_castle_xy = (ally_castle.x, ally_castle.y)

#           # Find the enemy castle
#           enemy = rc.get_enemy_team()
#           enemy_castle_id = -1

#           enemy_buildings = rc.get_buildings(enemy)
#           for building in enemy_buildings:
#               if building.type == BuildingType.MAIN_CASTLE:
#                   enemy_castle_id = rc.get_id_from_building(building)[1]
#                   break

#           enemy_castle = rc.get_building_from_id(enemy_castle_id)
#           if enemy_castle is None: 
#               return

#           # Decide whether to move units off the castle
#           move_off = rc.get_balance(team) >= 4

#           # Get enemy unit IDs for targeting
#           enemy_unit_ids = rc.get_unit_ids(enemy)

#           # Loop through all ally units
#           healers = []  # Track healers for healing logic
#           for unit_id in rc.get_unit_ids(team):
#               unit = rc.get_unit_from_id(unit_id)
#               if unit is None:
#                   continue

#               # Track healers
#               if unit.type == UnitType.LAND_HEALER_1:
#                   healers.append(unit)

#               # Attack enemy castle if possible
#               if enemy_castle_id in rc.get_building_ids(enemy) and rc.can_unit_attack_building(unit_id, enemy_castle_id):
#                   rc.unit_attack_building(unit_id, enemy_castle_id)

#               # Attack enemy units if possible
#               for enemy_unit_id in enemy_unit_ids:
#                   if rc.can_unit_attack_unit(unit_id, enemy_unit_id):
#                       rc.unit_attack_unit(unit_id, enemy_unit_id)

#               # Move units toward the enemy castle
#               if (unit.x, unit.y) == ally_castle_xy and not move_off:
#                   continue

#               possible_move_dirs = rc.unit_possible_move_directions(unit_id)
#               possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))

#               best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
#               if rc.can_move_unit_in_direction(unit_id, best_dir):
#                   rc.move_unit_in_direction(unit_id, best_dir)

#           # Heal nearby units
#           for healer in healers:
#               for ally_unit in rc.get_units(team):
#                   if rc.can_heal_unit(healer.id, ally_unit.id):
#                       rc.heal_unit(healer.id, ally_unit.id)

#           # Spawn units based on proportions
#           roll = random.random()
#           if roll < WARRIOR_PROPORTION and rc.can_spawn_unit(UnitType.WARRIOR, ally_castle_id):
#               rc.spawn_unit(UnitType.WARRIOR, ally_castle_id)
#           elif rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id):
#               rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id)
