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
        # Build Ports on water tiles
        for x in range(rc.get_map().width):
            for y in range(rc.get_map().height):
                if rc.get_map().is_tile_type(x, y, Tile.WATER):
                    if rc.can_build_building(BuildingType.PORT, x, y):
                        rc.build_building(BuildingType.PORT, x, y)

        # Spawn water units
        for building in rc.get_buildings(rc.get_ally_team()):
            if rc.can_spawn_unit(UnitType.SAILOR, building.id):
                rc.spawn_unit(UnitType.SAILOR, building.id)
            if rc.can_spawn_unit(UnitType.GALLEY, building.id):
                rc.spawn_unit(UnitType.GALLEY, building.id)
