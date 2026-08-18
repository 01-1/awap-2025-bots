# Written using claude

from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
import random

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.phase = "defense"  # Phases: defense, expand, attack
        self.defensive_line = []  # Track defensive units
        self.farm_defenders = {}  # Track defenders for each farm {farm_id: [unit_ids]}
        self.spawnloop_index = 0
    
    def get_castle_info(self, rc: RobotController):
        team = rc.get_ally_team()
        enemy = rc.get_enemy_team()
        
        ally_castle, ally_castle_id, enemy_castle, enemy_castle_id = None, None, None, None
        # Find ally castle
        for building in rc.get_buildings(team):
            if building.type == BuildingType.MAIN_CASTLE:
                ally_castle = building
                ally_castle_id = rc.get_id_from_building(building)[1]
                break
                
        # Find enemy castle
        for building in rc.get_buildings(enemy):
            if building.type == BuildingType.MAIN_CASTLE:
                enemy_castle = building
                enemy_castle_id = rc.get_id_from_building(building)[1]
                break
                
        return team, enemy, ally_castle, ally_castle_id, enemy_castle, enemy_castle_id

    def build_defensive_line(self, rc: RobotController, ally_castle):
        if self.spawnloop_index % 3 == 2:  # Healers
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle.id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle.id)
                self.spawnloop_index += 1
        else:  # Knights
            if rc.can_spawn_unit(UnitType.KNIGHT, ally_castle.id):
                rc.spawn_unit(UnitType.KNIGHT, ally_castle.id)
                self.spawnloop_index += 1

    def build_farm(self, rc: RobotController):
        # Try to build a farm in a random valid location
        valid_tiles = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                if rc.can_build_building(BuildingType.FARM_1, x, y):
                    valid_tiles.append((x, y))
        
        if valid_tiles:
            x, y = random.choice(valid_tiles)
            return rc.build_building(BuildingType.FARM_1, x, y)
        return False

    def defend_farm(self, rc: RobotController, farm_id):
        # Spawn defenders for a farm if needed
        farm = rc.get_building_from_id(farm_id)
        if farm and farm_id not in self.farm_defenders:
            if rc.can_spawn_unit(UnitType.KNIGHT, farm_id):
                rc.spawn_unit(UnitType.KNIGHT, farm_id)
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, farm_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, farm_id)

    def upgrade_defenders(self, rc: RobotController):
        # Replace knights with catapults at farms
        team = rc.get_ally_team()
        for unit_id in rc.get_unit_ids(team):
            unit = rc.get_unit_from_id(unit_id)
            if unit and unit.type == UnitType.KNIGHT:
                rc.sell_unit(unit_id)
                # Spawn catapult at nearest farm
                for building in rc.get_buildings(team):
                    if building.type == BuildingType.FARM_1:
                        if rc.can_spawn_unit(UnitType.CATAPULT, building.id):
                            rc.spawn_unit(UnitType.CATAPULT, building.id)
                            break

    def manage_units(self, rc: RobotController, enemy_castle):
        team = rc.get_ally_team()
        enemy = rc.get_enemy_team()
        
        # Manage all units
        for unit_id in rc.get_unit_ids(team):
            unit = rc.get_unit_from_id(unit_id)
            if not unit:
                continue

            # Healing logic
            if unit.type == UnitType.LAND_HEALER_1:
                lowest_health = float('inf')
                unit_to_heal = None
                for ally_unit in rc.get_units(team):
                    if rc.can_heal_unit(unit_id, ally_unit.id):
                        if ally_unit.health < lowest_health:
                            lowest_health = ally_unit.health
                            unit_to_heal = ally_unit
                if unit_to_heal:
                    rc.heal_unit(unit_id, unit_to_heal.id)
            
            # Attack logic
            else:
                # Attack enemy units in range
                for enemy_unit_id in rc.get_unit_ids(enemy):
                    if rc.can_unit_attack_unit(unit_id, enemy_unit_id):
                        rc.unit_attack_unit(unit_id, enemy_unit_id)
                
                # Attack enemy castle if in range
                if rc.can_unit_attack_building(unit_id, enemy_castle.id):
                    rc.unit_attack_building(unit_id, enemy_castle.id)

            # Movement logic for attack phase
            if self.phase == "attack":
                possible_moves = rc.unit_possible_move_directions(unit_id)
                if possible_moves:
                    # Move toward enemy castle
                    best_move = min(possible_moves, 
                                  key=lambda d: rc.get_chebyshev_distance(
                                      *rc.new_location(unit.x, unit.y, d),
                                      enemy_castle.x, enemy_castle.y))
                    if rc.can_move_unit_in_direction(unit_id, best_move):
                        rc.move_unit_in_direction(unit_id, best_move)

    def play_turn(self, rc: RobotController):
        # Get basic game info
        team, enemy, ally_castle, ally_castle_id, enemy_castle, enemy_castle_id = self.get_castle_info(rc)
        current_turn = rc.get_turn()

        if ally_castle is None or enemy_castle is None:
            return
        
        # Phase management
        if current_turn < 100 and self.phase == "defense":
            # Build initial defensive line
            self.build_defensive_line(rc, ally_castle)
            if len(rc.get_unit_ids(team)) >= 4:
                self.phase = "expand"
        
        elif current_turn < 2000 and self.phase == "expand":
            # Build and defend farms
            if rc.get_balance(team) >= BuildingType.FARM_1.cost:
                self.build_farm(rc)
            
            # Defend existing farms
            for building in rc.get_buildings(team):
                if building.type == BuildingType.FARM_1:
                    self.defend_farm(rc, building.id)
        
        elif (current_turn >= 2000 or len(rc.get_buildings(team)) >= 10) and self.phase != "attack":
            # Transition to attack phase
            self.phase = "attack"
            self.upgrade_defenders(rc)
        
        # Always manage units
        self.manage_units(rc, enemy_castle)
