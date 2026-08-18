# Written mostly using deepseek.
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
        self.turn = 0
        self.defensive_barrier_built = False
        self.farm_locations = []  # Track farm locations for defense
        self.attack_phase = False  # Flag for late-game attack phase

    def play_turn(self, rc: RobotController):
        self.turn += 1
        team = rc.get_ally_team()
        ally_castle_id = -1

        # Find the ally castle
        ally_buildings = rc.get_buildings(team)
        ally_castle = None
        for building in ally_buildings:
            if building.type == BuildingType.MAIN_CASTLE:
                ally_castle_id = rc.get_id_from_building(building)[1]
                ally_castle = building
                break

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
                enemy_castle = building
                break

        if enemy_castle is None:
            return

        # Early Game: Build defensive barrier and farms
        if not self.defensive_barrier_built:
            self.build_defensive_barrier(rc, ally_castle_xy, ally_castle_id)
            self.defensive_barrier_built = True

        if self.turn <= 2000:
            self.build_farms_randomly(rc, ally_castle_xy)
            self.defend_farms(rc, team)
        else:
            self.attack_phase = True

        # Late Game: Replace units and attack
        if self.attack_phase:
            self.replace_units_with_healers_and_catapults(rc, team)
            self.move_all_units_to_attack(rc, team, enemy_castle)

        # Spawn units based on phase
        if not self.attack_phase:
            if rc.can_spawn_unit(UnitType.KNIGHT, ally_castle_id):
                rc.spawn_unit(UnitType.KNIGHT, ally_castle_id)
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, ally_castle_id)

    def build_defensive_barrier(self, rc: RobotController, castle_xy: tuple, castle_id: int):
        """Build a 4-wide defensive barrier of Knights and Healers around the castle."""
        x, y = castle_xy
        directions = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),  # Immediate neighbors
            (x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2),  # 2 tiles away
            (x + 3, y), (x - 3, y), (x, y + 3), (x, y - 3),  # 3 tiles away
            (x + 4, y), (x - 4, y), (x, y + 4), (x, y - 4),  # 4 tiles away
        ]

        for dx, dy in directions:
            if rc.can_spawn_unit(UnitType.KNIGHT, castle_id):
                rc.spawn_unit(UnitType.KNIGHT, castle_id)
            if rc.can_spawn_unit(UnitType.LAND_HEALER_1, castle_id):
                rc.spawn_unit(UnitType.LAND_HEALER_1, castle_id)

    def build_farms_randomly(self, rc: RobotController, castle_xy: tuple):
        """Build farms randomly across the map."""
        for _ in range(rc.get_balance(rc.get_ally_team())): # quite slow
            x = random.randint(0, self.map.width - 1)
            y = random.randint(0, self.map.height - 1)
            if rc.can_build_building(BuildingType.FARM_1, x, y):
                rc.build_building(BuildingType.FARM_1, x, y)
                self.farm_locations.append((x, y))

    def defend_farms(self, rc: RobotController, team: Team):
        """Defend farms with Knights and Healers."""
        for farm_xy in self.farm_locations:
            farm_x, farm_y = farm_xy
            for unit in rc.get_units(team):
                if unit.type == UnitType.KNIGHT or unit.type == UnitType.LAND_HEALER_1:
                    # Move units toward farms to defend them
                    possible_move_dirs = rc.unit_possible_move_directions(unit.id)
                    possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), farm_x, farm_y))
                    best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
                    if rc.can_move_unit_in_direction(unit.id, best_dir):
                        rc.move_unit_in_direction(unit.id, best_dir)

    def replace_units_with_healers_and_catapults(self, rc: RobotController, team: Team):
        """Replace Knights at farms with Healers and Catapults."""
        for unit in rc.get_units(team):
            if unit.type == UnitType.KNIGHT:
                if rc.can_spawn_unit(UnitType.LAND_HEALER_1, unit.id):
                    rc.spawn_unit(UnitType.LAND_HEALER_1, unit.id)
                if rc.can_spawn_unit(UnitType.CATAPULT, unit.id):
                    rc.spawn_unit(UnitType.CATAPULT, unit.id)

    def move_all_units_to_attack(self, rc: RobotController, team: Team, enemy_castle: Building):
        """Move all units to attack the enemy castle."""
        for unit in rc.get_units(team):
            if unit.type == UnitType.CATAPULT or unit.type == UnitType.LAND_HEALER_1:
                # Move toward the enemy castle
                possible_move_dirs = rc.unit_possible_move_directions(unit.id)
                possible_move_dirs.sort(key=lambda dir: rc.get_chebyshev_distance(*rc.new_location(unit.x, unit.y, dir), enemy_castle.x, enemy_castle.y))
                best_dir = possible_move_dirs[0] if len(possible_move_dirs) > 0 else Direction.STAY
                if rc.can_move_unit_in_direction(unit.id, best_dir):
                    rc.move_unit_in_direction(unit.id, best_dir)

                # Attack the enemy castle if in range
                if rc.can_unit_attack_building(unit.id, enemy_castle.id):
                    rc.unit_attack_building(unit.id, enemy_castle.id)
