# Partially written using DeepSeek LLM. The original DeepSeek-written code is provided below this code; it has been heavily modified.

from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building

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

        enemy_unit_ids = rc.get_unit_ids(enemy)

        unused_castle_atks = []
        unused_castle_atk = 0

        team_units = rc.get_unit_ids(team)
        #for unit_id in team_units:
        while 1:
            if not team_units:
                team_units = unused_castle_atks
                unused_castle_atks = []

            if not team_units:
                break

            unit_id = team_units.pop()
            unit = rc.get_unit_from_id(unit_id)
            if unit is None:
                continue

            catk = False

            if enemy_castle_id in rc.get_building_ids(enemy) and rc.can_unit_attack_building(unit_id, enemy_castle_id):
                catk = True
                defense = 0
                for unit in rc.sense_units_within_radius(enemy, enemy_castle.x, enemy_castle.y, 0):
                    defense += unit.defense
                if defense < unit.health:
                    rc.unit_attack_building(unit_id, enemy_castle_id)
                    catk = False

            for enemy_unit_id in enemy_unit_ids:
                if rc.can_unit_attack_unit(unit_id, enemy_unit_id):
                    enemy_unit = rc.get_unit_from_id(enemy_unit_id)
                    if enemy_unit is None:
                        return
                    if enemy_unit.defense < unit.health:
                        rc.unit_attack_unit(unit_id, enemy_unit_id)
                        catk = False
            
            if catk:
                unused_castle_atks.append(unit_id)
                unused_castle_atk += unit.damage

            unit = rc.get_unit_from_id(unit_id)
            if unit is None:
                continue
            
            possible_move_dirs = rc.unit_possible_move_directions(unit_id)
            possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))

            best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
            if rc.can_move_unit_in_direction(unit_id, best_dir):
                rc.move_unit_in_direction(unit_id, best_dir)

        if rc.can_spawn_unit(UnitType.CATAPULT, ally_castle_id):
            rc.spawn_unit(UnitType.CATAPULT, ally_castle_id)


# DeepSeek Written Code

#   from src.player import Player
#   from src.map import Map
#   from src.robot_controller import RobotController
#   from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
#   from src.units import Unit
#   from src.buildings import Building

#   class BotPlayer(Player):
#       def __init__(self, map: Map):
#           self.map = map
#       
#       def play_turn(self, rc: RobotController):
#           team = rc.get_ally_team()
#           ally_castle_id = -1

#           ally_buildings = rc.get_buildings(team)
#           for building in ally_buildings:
#               if building.type == BuildingType.MAIN_CASTLE:
#                   ally_castle_id = rc.get_id_from_building(building)[1]
#                   break

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

#           # Spawn Catapults
#           if rc.can_spawn_unit(UnitType.CATAPULT, ally_castle_id):
#               rc.spawn_unit(UnitType.CATAPULT, ally_castle_id)

#           # Attack enemy buildings
#           for unit_id in rc.get_unit_ids(team):
#               if enemy_castle_id in rc.get_building_ids(enemy) and rc.can_unit_attack_building(unit_id, enemy_castle_id):
#                   rc.unit_attack_building(unit_id, enemy_castle_id)

#               unit = rc.get_unit_from_id(unit_id)
#               if unit is None:
#                   return
#               
#               possible_move_dirs = rc.unit_possible_move_directions(unit_id)
#               possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))

#               best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
#               if rc.can_move_unit_in_direction(unit_id, best_dir):
#                   rc.move_unit_in_direction(unit_id, best_dir)
