
# Aggressive Bot
# Focuses on attacking enemy units aggressively

from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import Team, Tile, GameConstants, Direction, BuildingType, UnitType
from src.units import Unit
from src.buildings import Building
# Adaptive Bot
# Changes strategy based on the enemy

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.defensive_mode = False
    
    def play_turn(self, rc: RobotController):
        if rc.sense_units_within_radius(rc.get_enemy_team(), 0, 0, 10**10) > rc.sense_units_within_radius(rc.get_ally_team(), 0, 0, 10**10):
            self.defensive_mode = True
        
        for unit in rc.get_units(rc.get_ally_team()):
            if self.defensive_mode:
                if rc.can_build(unit, BuildingType.WALL):
                    rc.build(unit, BuildingType.WALL)
            else:
                enemies = rc.get_visible_enemies(unit)
                if enemies:
                    rc.attack(unit, enemies[0])
