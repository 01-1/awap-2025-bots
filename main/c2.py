# written with help from chatgpt, deepseek, claude

from functools import total_ordering
from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
from collections import deque
import random

dir8 = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 1),
              (1, -1), (1, 0), (1, 1)]

rdir = {}
LANDMOVABLE = (Tile.GRASS, Tile.SAND, Tile.BRIDGE)

for direction in Direction:
    rdir[(direction.dx, direction.dy)] = direction

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.phase = "defense"  # Phases: defense, expand, attack
        # self.defensive_positions = {}  # Track target positions for defensive units {unit_id: (target_x, target_y)}
        # Deprecated
        self.defensive_positions_list = []
        self.farm_defenders = {}  # Track defenders for each farm {farm_id: [(target_x, target_y, unit_type)]}
        self.spawnloop_index = 0
        self.units_to_position = []  # Queue of units that need positioning
        self.sent_catapult = False
        self.posi = 0
    
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

    def get_defensive_positions_init(self, castle, enemy_castle):
        # Calculate 4 positions in front of the castle
        positions = []
        for i in range(-4, 5):
            for j in range(-4, 5):
                positions.append((i, j))

        edx,edy = (enemy_castle.x - castle.x, enemy_castle.y - castle.y)

        positions.sort(key=lambda p: (max(abs(p[0]), abs(p[1])), self.get_chebyshev_distance(p[0], p[1], edx, edy)))
        
        positions = [(castle.x+i, castle.y+j) for i, j in positions]

        return [(x,y) for x,y in positions if self.map.in_bounds(x,y) and self.map.tiles[x][y] in LANDMOVABLE]

    def move_unit_toward_position(self, rc: RobotController, unit_id, target_x, target_y):
        unit = rc.get_unit_from_id(unit_id)
        #print(unit.x, unit.y, target_x, target_y)

        if not unit:
            return False

        if (unit.x, unit.y) == (target_x, target_y):
            return True

        # Get possible moves
        possible_moves = rc.unit_possible_move_directions(unit_id)
        if not possible_moves:
            return False

        # Find best move toward target
        best_move = min(possible_moves, 
                       key=lambda d: rc.get_chebyshev_distance(
                           *rc.new_location(unit.x, unit.y, d),
                           target_x, target_y))
        
        if rc.can_move_unit_in_direction(unit_id, best_move):
            rc.move_unit_in_direction(unit_id, best_move)
            return True
        return False


    def get_chebyshev_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        '''
        Returns the chebyshev (chessboard) distance between (x1, y1) and (x2, y2)
        
        Chebyshev distance between two points is the maximum lateral distance along an axis.
        It is also the minimum number of moves in chess that a king needs to move from (x1, y1) to (x2, y2)
        '''

        return max(abs(x1 - x2), abs(y1 - y2))

    def chebyshev_shortest_path(self, start, end, target_radius=0):
        rows, cols =self.map.width, self.map.height
        dist = [[-1] * cols for _ in range(rows)]  # Distance grid, -1 means unvisited
        parent = [[None] * cols for _ in range(rows)]  # Store the parent for path reconstruction
        queue = deque([start])
        dist[start[0]][start[1]] = 0  # Start distance is 0
        ex, ey = end

        while queue:
            x, y = queue.popleft()

            if self.get_chebyshev_distance(x, y, ex, ey) <= target_radius:  # If we reached the destination, reconstruct the path
                path = []
                xy = (x, y)
                while xy is not None:
                    path.append(xy)
                    x, y = xy
                    xy = parent[x][y]  # Move backwards
                return path[::-1]  # Reverse to get correct order

            for dx, dy in dir8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and self.map.tiles[nx][ny] in LANDMOVABLE and dist[nx][ny] == -1:
                    dist[nx][ny] = dist[x][y] + 1
                    parent[nx][ny] = (x, y)  # Store parent for path reconstruction
                    queue.append((nx, ny))

        return None  # If no path exists

    def build_defensive_line(self, rc: RobotController, ally_castle):
        team = rc.get_ally_team()
        defensive_positions = self.defensive_positions_list
        
        # Check if we need more defensive units
        #current_defenders = 0
        target_pos = None
        for i, (x, y) in enumerate(defensive_positions):
            if rc.sense_units_within_radius(team, x, y, 0) == []:
                target_pos = x, y
                break

        #if current_defenders >= len(defensive_positions):
        if target_pos is None:
            return False
            # Spawn alternating units
        #target_pos = defensive_positions[current_defenders]

        modder = 3
        if rc.get_chebyshev_distance(target_pos[0], target_pos[1], ally_castle.x, ally_castle.y) < 3:
            modder = 2
        
        if self.posi % modder != 0:
            if rc.get_balance(team) < 1:
                return True
        elif rc.get_balance(team) < 3:
            return True

        # Move units out of the way

        shortest_path = self.chebyshev_shortest_path(target_pos, (ally_castle.x, ally_castle.y))

        if shortest_path is None:
            #print('g')
            return False
        #print(shortest_path)

        for i, pos in enumerate(shortest_path[:-1]):
            prev_pos = shortest_path[i+1]
            x, y = prev_pos
            x2, y2 = pos
            dx, dy = x2-x, y2-y
            units = rc.sense_units_within_radius(team, x, y, 0)
            if len(units)==0:
                continue
            unit = units[0]
            rc.move_unit_in_direction(unit.id, rdir[(dx, dy)])


        # Next: detect if catapults are being built, detect if opponent has bad defense etc

        if self.posi % modder != 0:  # Knights
            rc.spawn_unit(UnitType.KNIGHT, ally_castle.id)
        else:  # Healers
            rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle.id)

        self.posi += 1

        return True
        #   if rc.can_spawn_unit(UnitType.KNIGHT, ally_castle.id):
        #       if rc.spawn_unit(UnitType.KNIGHT, ally_castle.id):
        #           unit_id = rc.sense_units_within_radius(team, ally_castle.x, ally_castle.y, 0)[0].id
        #           self.defensive_positions[unit_id] = target_pos
        #   if rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle.id):
        #       if rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle.id):
        #           unit_id = rc.sense_units_within_radius(team, ally_castle.x, ally_castle.y, 0)[0].id
        #           target_pos = defensive_positions[current_defenders]
        #           self.defensive_positions[unit_id] = target_pos

    def get_farm_defensive_positions(self, farm):
        # Calculate positions around the farm
        positions = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = farm.x + dx, farm.y + dy
                if 0 <= x < self.map.width and 0 <= y < self.map.height:
                    positions.append((x, y))
        return positions

    def build_farm(self, rc: RobotController):
        # Try to build a farm in a random valid location
        valid_tiles = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                if rc.can_build_building(BuildingType.FARM_1, x, y):
                    valid_tiles.append((x, y))
        
        if valid_tiles:
            x, y = random.choice(valid_tiles)
            if rc.build_building(BuildingType.FARM_1, x, y):
                # Set up defensive positions for this farm
                farm_id = len(rc.get_buildings(rc.get_ally_team())) - 1
                positions = self.get_farm_defensive_positions(Building(rc.get_ally_team(), BuildingType.FARM_1, x, y))
                self.farm_defenders[farm_id] = positions
                return True
        return False

    def defend_farm(self, rc: RobotController, farm_id):
        farm = rc.get_building_from_id(farm_id)
        if not farm or farm_id not in self.farm_defenders:
            return

        team = rc.get_ally_team()
        positions = self.farm_defenders[farm_id]
        
        # Spawn defenders if needed
        current_defenders = sum(1 for unit in rc.get_units(team) 
                              if any(self.move_unit_toward_position(rc, unit.id, x, y) 
                                    for x, y in positions))
        
        if current_defenders < len(positions):
            if rc.can_spawn_unit(UnitType.KNIGHT, farm_id):
                rc.spawn_unit(UnitType.KNIGHT, farm_id)
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, farm_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, farm_id)

    def manage_units(self, rc: RobotController, enemy_castle):
        team = rc.get_ally_team()
        enemy = rc.get_enemy_team()
        
        # Move units to their defensive positions
        for unit_id in rc.get_unit_ids(team):
            unit = rc.get_unit_from_id(unit_id)
            if not unit:
                continue

            # Move to defensive position if assigned
            #if unit_id in self.defensive_positions:
                #target_x, target_y = self.defensive_positions[unit_id]
                #self.move_unit_toward_position(rc, unit_id, target_x, target_y)

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
                # Attack enemy castle if in range
                attack = False
                if rc.can_unit_attack_building(unit_id, enemy_castle.id):
                    if rc.unit_attack_building(unit_id, enemy_castle.id):
                        attack = True
                # Attack enemy units in range
                for enemy_unit_id in rc.get_unit_ids(enemy):
                    if rc.can_unit_attack_unit(unit_id, enemy_unit_id):
                        if rc.unit_attack_unit(unit_id, enemy_unit_id):
                            attack = True

                if not attack and unit.type == UnitType.CATAPULT:
                    self.move_unit_toward_position(rc, unit_id, enemy_castle.x, enemy_castle.y)
                

    def play_turn(self, rc: RobotController):
        # Get basic game info
        team, enemy, ally_castle, ally_castle_id, enemy_castle, enemy_castle_id = self.get_castle_info(rc)
        current_turn = rc.get_turn()

        if ally_castle is None or enemy_castle is None:
            return

        if len(self.defensive_positions_list) == 0:
            self.defensive_positions_list = self.get_defensive_positions_init(ally_castle, enemy_castle)
            self.enemy_weak_spots = self.get_defensive_positions_init(enemy_castle, ally_castle)
        
        # Phase management
        #if self.phase == "defense":
            # Build initial defensive line
            #if not self.build_defensive_line(rc, ally_castle):
                #self.phase = 'expand'
            
            # Check if defensive line is complete
#           all_in_position = True
#           for unit_id, (target_x, target_y) in self.defensive_positions.items():
#               unit = rc.get_unit_from_id(unit_id)
#               if not unit or (unit.x, unit.y) != (target_x, target_y):
#                   all_in_position = False
#                   break
#                   
#           if all_in_position:
#               self.phase = "expand"

        if not self.build_defensive_line(rc, ally_castle) and not self.sent_catapult:
            buildings = rc.get_buildings(team)
            if len(buildings) > 1:
                for x, y in self.enemy_weak_spots:
                    if len(rc.sense_units_within_radius(enemy, x, y, 0)) == 0:
                        for building in buildings:
                            if self.chebyshev_shortest_path((building.x, building.y), (enemy_castle.x, enemy_castle.y), 4) is not None and building.type != BuildingType.MAIN_CASTLE and rc.spawn_unit(UnitType.CATAPULT, building.id):
                                self.sent_catapult = True
                                break
                        break

        # Build and defend farms
        while rc.get_balance(team) >= BuildingType.FARM_1.cost:
            if not self.build_farm(rc):
                break

        
        #if len(rc.get_units(enemy))
            
            # Defend existing farms
        #for building in rc.get_buildings(team):
            #if building.type == BuildingType.FARM_1:
                #self.defend_farm(rc, building.id)
        
        #if (current_turn >= 2000 or len(rc.get_buildings(team)) >= 10) and self.phase != "attack":
            # Transition to attack phase
            #self.phase = "attack"
            #self.defensive_positions.clear()  # Clear defensive positions to allow units to move
        
        # Always manage units
        self.manage_units(rc, enemy_castle)

        # TODO check if dies
