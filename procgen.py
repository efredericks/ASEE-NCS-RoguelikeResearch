from __future__ import annotations

import random
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING

import numpy.random
import tcod

import entity_factories
from game_map import GameMap
import tile_types

# for simplex noise integration
import opensimplex

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor

max_items_by_floor = [
    (1, (2, 3)),
    (5, (3, 5)),
    (8, (5, 8)),
]

max_monsters_by_floor = [
    (1, (2, 3)),
    (3, (3, 5)),
    (5, (4, 6)),
    (8, (5, 7)),
    (10, (7, 9))
]

item_chances: Dict[int, List[Tuple[Entity, Tuple[int, int]]]] = {
    1: [(entity_factories.health_potion, (25, 35)), (entity_factories.confusion_scroll, (15, 25)),
        (entity_factories.arrow, (5, 10)), (entity_factories.smite_scroll, (5, 10)),
        (entity_factories.poison_scroll, (5, 10))],

    2: [(entity_factories.health_potion, (25, 35)), (entity_factories.confusion_scroll, (15, 25)),
        (entity_factories.arrow, (5, 10)), (entity_factories.smite_scroll, (5, 10)),
        (entity_factories.poison_scroll, (5, 10)), (entity_factories.chain_lighting_scroll, (5, 10))],

    3: [(entity_factories.health_potion, (35, 40)), (entity_factories.confusion_scroll, (20, 25)),
        (entity_factories.arrow, (10, 13)), (entity_factories.poison_scroll, (10, 15)),
        (entity_factories.smite_scroll, (10, 15)), (entity_factories.chain_lighting_scroll, (10, 15)),
        (entity_factories.fireball_scroll, (5, 10))],

    5: [(entity_factories.health_potion, (15, 25)), (entity_factories.confusion_scroll, (25, 30)),
        (entity_factories.arrow, (20, 25)), (entity_factories.poison_scroll, (30, 40)),
        (entity_factories.smite_scroll, (35, 45)), (entity_factories.chain_lighting_scroll, (15, 30)),
        (entity_factories.fireball_scroll, (10, 15))],

    8: [(entity_factories.health_potion, (15, 30)), (entity_factories.confusion_scroll, (10, 30)),
        (entity_factories.arrow, (10, 35)), (entity_factories.poison_scroll, (15, 40)),
        (entity_factories.smite_scroll, (15, 55)), (entity_factories.chain_lighting_scroll, (15, 35)),
        (entity_factories.fireball_scroll, (10, 25))],
}

enemy_chances: Dict[int, List[Tuple[Entity, Tuple[int, int]]]] = {
    1: [(entity_factories.bat, (25, 35)), (entity_factories.spider, (5, 15)), (entity_factories.rat, (1, 5))],

    3: [(entity_factories.bat, (10, 25)), (entity_factories.spider, (25, 30)), (entity_factories.rat, (5, 10))],

    5: [(entity_factories.bat, (10, 15)), (entity_factories.spider, (25, 35)), (entity_factories.rat, (5, 15)),
        (entity_factories.marionette, (1, 5)), (entity_factories.skeleton, (1, 3))],

    7: [(entity_factories.bat, (10, 50)), (entity_factories.spider, (25, 55)), (entity_factories.rat, (10, 35)),
        (entity_factories.marionette, (5, 15)), (entity_factories.skeleton, (1, 10)),
        (entity_factories.serpent, (1, 5)),
        (entity_factories.troll, (1, 3))],

    9: [(entity_factories.bat, (10, 50)), (entity_factories.spider, (15, 60)), (entity_factories.rat, (15, 45)),
        (entity_factories.marionette, (5, 25)), (entity_factories.skeleton, (1, 15)),
        (entity_factories.serpent, (1, 10)),
        (entity_factories.troll, (1, 5)), (entity_factories.orc, (1, 3)), (entity_factories.knight, (1, 3))],

    10: [(entity_factories.bat, (10, 50)), (entity_factories.spider, (15, 60)), (entity_factories.rat, (15, 30)),
         (entity_factories.marionette, (5, 35)), (entity_factories.skeleton, (5, 20)),
         (entity_factories.serpent, (5, 15)),
         (entity_factories.troll, (3, 10)), (entity_factories.orc, (3, 10)), (entity_factories.knight, (3, 5)),
         (entity_factories.wraith, (1, 5)), (entity_factories.reaper_henchmen, (1, 3))],

    11: [(entity_factories.bat, (25, 35)), (entity_factories.spider, (40, 60)), (entity_factories.rat, (30, 75)),
         (entity_factories.marionette, (30, 50)), (entity_factories.skeleton, (20, 30)),
         (entity_factories.serpent, (10, 25)),
         (entity_factories.troll, (10, 20)), (entity_factories.orc, (5, 15)), (entity_factories.knight, (3, 10)),
         (entity_factories.wraith, (5, 15)), (entity_factories.reaper_henchmen, (5, 10))]
}

unique_entities_chances_by_floor: Dict[int, List[Tuple[Entity, Tuple[int, int]]]] = {
    1: [(entity_factories.fireball_scroll, (3, 5)), (entity_factories.chain_lighting_scroll, (3, 5)),
        (entity_factories.bow, (1, 5)), (entity_factories.twin_daggers, (1, 5)),
        (entity_factories.marionette, (1, 2)), (entity_factories.skeleton, (1, 2))],

    3: [(entity_factories.fireball_scroll, (5, 8)), (entity_factories.chain_lighting_scroll, (5, 8)),
        (entity_factories.serpents_fang, (3, 5)), (entity_factories.cyclops_club, (3, 5)),
        (entity_factories.cursed_thornail, (1, 3)), (entity_factories.viperlord_vesture, (1, 3)),
        (entity_factories.bow, (3, 5)), (entity_factories.twin_daggers, (3, 5)),
        (entity_factories.marionette, (2, 3)), (entity_factories.skeleton, (2, 3))],

    5: [(entity_factories.fireball_scroll, (5, 10)), (entity_factories.chain_lighting_scroll, (5, 10)),
        (entity_factories.serpents_fang, (3, 8)), (entity_factories.cyclops_club, (3, 8)),
        (entity_factories.cursed_thornail, (3, 5)), (entity_factories.viperlord_vesture, (3, 5)),
        (entity_factories.doombringer_axe, (1, 3)), (entity_factories.lunar_weaver, (1, 5)),
        (entity_factories.bow, (5, 10)), (entity_factories.twin_daggers, (5, 10)),
        (entity_factories.marionette, (3, 5)), (entity_factories.skeleton, (3, 5))],

    8: [(entity_factories.fireball_scroll, (5, 15)), (entity_factories.chain_lighting_scroll, (5, 15)),
        (entity_factories.serpents_fang, (5, 10)), (entity_factories.cyclops_club, (5, 10)),
        (entity_factories.cursed_thornail, (3, 8)), (entity_factories.viperlord_vesture, (3, 8)),
        (entity_factories.doombringer_axe, (3, 5)), (entity_factories.lunar_weaver, (3, 5)),
        (entity_factories.soulreaver_scythe, (1, 5)), (entity_factories.dragonscale_armor, (5, 10)),
        (entity_factories.bow, (5, 15)), (entity_factories.twin_daggers, (5, 10)),
        (entity_factories.marionette, (3, 10)), (entity_factories.skeleton, (3, 10))],

    9: [(entity_factories.fireball_scroll, (5, 25)), (entity_factories.chain_lighting_scroll, (5, 25)),
        (entity_factories.serpents_fang, (5, 10)), (entity_factories.cyclops_club, (5, 10)),
        (entity_factories.cursed_thornail, (5, 10)), (entity_factories.viperlord_vesture, (5, 10)),
        (entity_factories.doombringer_axe, (3, 5)), (entity_factories.lunar_weaver, (5, 10)),
        (entity_factories.soulreaver_scythe, (3, 5)), (entity_factories.dragonscale_armor, (1, 10)),
        (entity_factories.bow, (5, 20)), (entity_factories.twin_daggers, (5, 20)),
        (entity_factories.marionette, (3, 15)), (entity_factories.skeleton, (3, 15)),
        (entity_factories.reaper_henchmen, (1, 3))],

    10: [(entity_factories.fireball_scroll, (5, 25)), (entity_factories.chain_lighting_scroll, (5, 25)),
         (entity_factories.serpents_fang, (5, 10)), (entity_factories.cyclops_club, (5, 10)),
         (entity_factories.cursed_thornail, (5, 10)), (entity_factories.viperlord_vesture, (5, 10)),
         (entity_factories.doombringer_axe, (5, 10)), (entity_factories.lunar_weaver, (5, 10)),
         (entity_factories.soulreaver_scythe, (3, 5)), (entity_factories.dragonscale_armor, (3, 5)),
         (entity_factories.flamebrand_sword, (1, 3)), (entity_factories.flameshroud_regalia, (1, 3)),
         (entity_factories.bow, (5, 25)), (entity_factories.twin_daggers, (5, 25)),
         (entity_factories.marionette, (3, 15)), (entity_factories.skeleton, (3, 15)),
         (entity_factories.reaper_henchmen, (1, 5)), (entity_factories.grim_reaper, (3, 8))],

    13: [(entity_factories.fireball_scroll, (5, 25)), (entity_factories.chain_lighting_scroll, (5, 25)),
         (entity_factories.serpents_fang, (5, 10)), (entity_factories.cyclops_club, (5, 10)),
         (entity_factories.cursed_thornail, (5, 10)), (entity_factories.viperlord_vesture, (5, 10)),
         (entity_factories.doombringer_axe, (5, 10)), (entity_factories.lunar_weaver, (5, 10)),
         (entity_factories.soulreaver_scythe, (5, 10)), (entity_factories.dragonscale_armor, (5, 10)),
         (entity_factories.flamebrand_sword, (3, 5)), (entity_factories.flameshroud_regalia, (3, 5)),
         (entity_factories.thor_hammer, (1, 3)), (entity_factories.stormbreaker_plate, (1, 3)),
         (entity_factories.bow, (3, 25)), (entity_factories.twin_daggers, (5, 25)),
         (entity_factories.marionette, (3, 25)), (entity_factories.skeleton, (3, 25)),
         (entity_factories.reaper_henchmen, (3, 10)), (entity_factories.grim_reaper, (5, 10))],

    15: [(entity_factories.fireball_scroll, (5, 25)), (entity_factories.chain_lighting_scroll, (5, 25)),
         (entity_factories.serpents_fang, (5, 10)), (entity_factories.cyclops_club, (5, 10)),
         (entity_factories.cursed_thornail, (5, 10)), (entity_factories.viperlord_vesture, (5, 10)),
         (entity_factories.doombringer_axe, (5, 10)), (entity_factories.lunar_weaver, (5, 10)),
         (entity_factories.soulreaver_scythe, (5, 10)), (entity_factories.dragonscale_armor, (5, 10)),
         (entity_factories.flamebrand_sword, (5, 10)), (entity_factories.flameshroud_regalia, (5, 10)),
         (entity_factories.thor_hammer, (3, 5)), (entity_factories.stormbreaker_plate, (3, 5)),
         (entity_factories.bow, (3, 25)), (entity_factories.twin_daggers, (5, 25)),
         (entity_factories.marionette, (3, 25)), (entity_factories.skeleton, (3, 25)),
         (entity_factories.reaper_henchmen, (5, 15)), (entity_factories.grim_reaper, (5, 20))],
}


def get_max_value_for_floor(
        max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        lower_bound = value[0]
        upper_bound = value[1]
        if floor_minimum > floor:
            break
        else:
            current_value = random.randint(lower_bound, upper_bound)

    return current_value


def get_entities_at_random(
        weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int, int]]],
        number_of_entities: int,
        floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for floor_key in range(floor, -1, -1):
        if floor_key in weighted_chances_by_floor:
            entity_weighted_chances = dict(weighted_chances_by_floor[floor_key])
            break

    entities = []
    entity_weighted_chance_values = []
    for entity, value in entity_weighted_chances.items():
        lower_bound = value[0]
        upper_bound = value[1]
        chance = random.randint(lower_bound, upper_bound)

        entities.append(entity)
        entity_weighted_chance_values.append(chance)

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


def place_unique_entities(
        floor: int,
        accessible_tiles: List[Tuple[int, int]],
        dungeon: GameMap,
        unique_entities_chances: Dict[int, List[Tuple[Entity, int, int]]]
) -> None:
    unique_entity_weighted_chances = {}

    for floor_key in range(floor, -1, -1):
        if floor_key in unique_entities_chances:
            unique_entity_weighted_chances = dict(unique_entities_chances[floor_key])
            break

    for entity, value in unique_entity_weighted_chances.items():
        lower_bound = value[0]
        upper_bound = value[1]
        chance = random.randint(lower_bound, upper_bound)
        if random.random() < chance / 100:
            x, y = random.choice(accessible_tiles)
            accessible_tiles.remove((x, y))
            entity.place(x, y, dungeon)


def scale_entities(
        floor: int,
):
    if floor == 1:
        entity_factories.bat.fighter.scale_fighter(hp=True, defense=False, attack=False, amount=0)


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
                self.x1 <= other.x2
                and self.x2 >= other.x1
                and self.y1 <= other.y2
                and self.y2 >= other.y1
        )


class CellularAutomata:
    def __init__(self, width, height, chance_to_come_alive=0.4, birth_limit=4, death_limit=3):
        self.map_width = width
        self.map_height = height

        self.chance_to_come_alive = chance_to_come_alive
        self.birth_limit = birth_limit
        self.death_limit = death_limit

        self.map = []

    def initialize_map(self):
        for x in range(self.map_width):
            row = []
            for y in range(self.map_height):
                if random.random() <= self.chance_to_come_alive:
                    row.append(True)
                else:
                    row.append(False)
            self.map.append(row)
        return self.map

    def do_simulation_step(self):
        new_map = [[False] * self.map_height for _ in range(self.map_width)]

        for x in range(self.map_width):
            for y in range(self.map_height):
                nbs_count = self.count_alive_neighbors(self.map, x, y)
                # The new value is based on our simulation rules
                # First, if a cell is alive but has too few neighbours, kill it.
                if self.map[x][y]:
                    if nbs_count < self.death_limit:
                        new_map[x][y] = False
                    else:
                        new_map[x][y] = True
                # Otherwise, if the cell is dead now, check if it has the right number of neighbours to be 'born'
                else:
                    if nbs_count > self.birth_limit:
                        new_map[x][y] = True
                    else:
                        new_map[x][y] = False
        return new_map

    def count_alive_neighbors(self, map, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbour_x = x + i
                neighbour_y = y + j
                # If we're looking at the middle point
                if i == 0 and j == 0:
                    # Do nothing, we don't want to add ourselves in!
                    pass
                # In case the index we're looking at is off the edge of the map
                elif (
                        neighbour_x < 0
                        or neighbour_y < 0
                        or neighbour_x >= self.map_width
                        or neighbour_y >= self.map_height
                ):
                    count += 1
                # Otherwise, a normal check of the neighbour
                elif map[neighbour_x][neighbour_y]:
                    count += 1
        return count

    def generate_dungeon(self, number_of_steps):
        self.initialize_map()
        for i in range(number_of_steps):
            self.map = self.do_simulation_step()


class SimplexNoise:
    def __init__(self, width: int, height: int, seed: int):
        self.map_width = width
        self.map_height = height
        self.map = []

        self.seed = seed

    def initialize_map(self):
        rng = numpy.random.default_rng(seed=self.seed)
        ix = rng.random(self.map_width)
        iy = rng.random(self.map_height)
        self.map = opensimplex.noise2array(iy, ix).tolist()
        return self.map


def place_entities(dungeon: GameMap, floor_number: int, accessible_tiles: list[int]):
    accessible_tiles = list(accessible_tiles)

    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        x, y = random.choice(accessible_tiles)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)
            accessible_tiles.remove((x, y))

    place_unique_entities(floor_number, accessible_tiles, dungeon, unique_entities_chances_by_floor)


def tunnel_between(
        start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def flood_fill(player: Entity, dungeon: GameMap):
    start = (player.x, player.y)
    stack = [start]
    visited = set()
    accessible_tiles = set()

    while stack:
        x, y = stack.pop()
        visited.add((x, y))  # Mark the current coordinates as visited

        if dungeon.tiles[x][y] == tile_types.floor:
            accessible_tiles.add((x, y))

        # Add neighboring tiles to the stack if they are accessible and haven't been visited
        # only add neighboring tiles that are floor tiles, so that only the areas accessible to the player are
        # added.
        if x > 0 and (x - 1, y) not in visited and dungeon.tiles[x - 1][y] == tile_types.floor:
            stack.append((x - 1, y))
        if x < dungeon.width - 1 and (x + 1, y) not in visited and dungeon.tiles[x + 1][y] == tile_types.floor:
            stack.append((x + 1, y))
        if y > 0 and (x, y - 1) not in visited and dungeon.tiles[x][y - 1] == tile_types.floor:
            stack.append((x, y - 1))
        if y < dungeon.height - 1 and (x, y + 1) not in visited and dungeon.tiles[x][y + 1] == tile_types.floor:
            stack.append((x, y + 1))

    for x in range(dungeon.width):
        for y in range(dungeon.height):
            if (x, y) not in accessible_tiles:
                dungeon.tiles[x][y] = tile_types.wall

    accessible_tiles.remove((player.x, player.y))
    return accessible_tiles


def generate_rectangular_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)
    accessible_tiles = []

    scale_entities(floor=engine.game_world.current_floor)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

            center_of_last_room = new_room.center

        accessible_tiles = flood_fill(player, dungeon)
        place_entities(dungeon, engine.game_world.current_floor, accessible_tiles)

        # Finally, append the new room to the list.
        rooms.append(new_room)

    if engine.game_world.current_floor < 10:
        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

    if engine.game_world.current_floor > 1:
        center_of_first_room = rooms[0].center
        dungeon.tiles[center_of_first_room] = tile_types.up_stairs
        dungeon.upstairs_location = center_of_first_room

    return dungeon


def generate_cellular_automata_dungeon(
        map_width: int,
        map_height: int,
        engine: Engine,
        number_of_steps: int,
        max_rooms: int,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    accessible_tiles = []

    scale_entities(floor=engine.game_world.current_floor)

    while len(accessible_tiles) <= 1000:
        cellular_automata_floor = CellularAutomata(width=map_width, height=map_height)
        cellular_automata_floor.generate_dungeon(number_of_steps=number_of_steps)

        valid_spawn_locations = []

        for x in range(map_width):
            for y in range(map_height):
                # if it is False in the cellular automata, it is a floor tile. otherwise it is true and will
                # be a wall tile
                if not cellular_automata_floor.map[x][y]:
                    dungeon.tiles[x][y] = tile_types.floor
                    valid_spawn_locations.append((x, y))

        placement_x, placement_y = random.choice(valid_spawn_locations)
        player.place(placement_x, placement_y, dungeon)
        # cleans up the map
        accessible_tiles = flood_fill(player, dungeon)

        if engine.game_world.current_floor > 1:
            dungeon.tiles[placement_x][placement_y] = tile_types.up_stairs
            dungeon.upstairs_location = (placement_x, placement_y)

        placement_x, placement_y = accessible_tiles.pop()
        if engine.game_world.current_floor < 10:
            dungeon.tiles[placement_x][placement_y] = tile_types.down_stairs
            dungeon.downstairs_location = (placement_x, placement_y)

        for _ in range(max_rooms):
            place_entities(dungeon, engine.game_world.current_floor, accessible_tiles)

    return dungeon


def generate_simplex_noise_dungeon(map_width: int,
                                   map_height: int,
                                   engine: Engine,
                                   max_rooms: int,
                                   seed: int
                                   ) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    accessible_tiles = []

    scale_entities(floor=engine.game_world.current_floor)

    while len(accessible_tiles) <= 1000:
        simplex_noise_floor = SimplexNoise(width=map_width, height=map_height, seed=seed)
        simplex_noise_floor.initialize_map()

        valid_spawn_locations = []

        for x in range(map_width):
            for y in range(map_height):
                if simplex_noise_floor.map[x][y] >= -.5:
                    dungeon.tiles[x][y] = tile_types.floor
                    valid_spawn_locations.append((x, y))
                else:
                    dungeon.tiles[x][y] = tile_types.wall

        placement_x, placement_y = random.choice(valid_spawn_locations)
        player.place(placement_x, placement_y, dungeon)
        # cleans up the map
        accessible_tiles = flood_fill(player, dungeon)

        if engine.game_world.current_floor > 1:
            dungeon.tiles[placement_x][placement_y] = tile_types.up_stairs
            dungeon.upstairs_location = (placement_x, placement_y)

        placement_x, placement_y = accessible_tiles.pop()
        if engine.game_world.current_floor < 10:
            dungeon.tiles[placement_x][placement_y] = tile_types.down_stairs
            dungeon.downstairs_location = (placement_x, placement_y)

        for _ in range(max_rooms):
            place_entities(dungeon, engine.game_world.current_floor, accessible_tiles)

    return dungeon
