from __future__ import annotations

import random
from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
            self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        # for placing stairs locations
        self.downstairs_location = (0, 0)
        self.upstairs_location = (0, 0)

        # for scrolling camera functionality
        self.x_start = 0
        self.y_start = 0

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
            self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int, ) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map through the scrolling camera.
        """
        # the width of the camera
        camera_width = 50
        # the height of the camera
        camera_height = 50

        # attempting to center the player in the screen
        x_start = self.engine.player.x - self.gamemap.width // 2
        y_start = self.engine.player.y - self.gamemap.height // 2

        # There is a chance that the camera is set out of bounds, and thus we
        # must correct it so that it can only be as far left as 0, the edge of the screen.

        # this provides the actual x_start so that if the player is too far left it snaps
        # the camera to the left/top of the map rather than going past it.
        x_start = max(0, x_start)
        y_start = max(0, y_start)

        # now we need to calculate where the camera ends
        # since the width of the camera, for now, is set here as camera_width and same for the height, we need to
        # calculate if adding this with would go over and if we should simply snap the camera to
        # the right/bottom of the map
        x_end = min(x_start + camera_width, self.gamemap.width)
        y_end = min(y_start + camera_height, self.gamemap.height)

        # now that we have where to begin the camera and where to end, we need to go about adding the appropriate
        # tiles

        # Fill the console with the shroud tile
        # console.tiles_rgb[:, :] = tile_types.SHROUD

        # loop through each coordinate in the camera and draw the appropriate tile
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                # Draw the tile on the console
                if self.visible[x, y]:
                    # where the tiles will be shifted to
                    console_x = x - x_start
                    console_y = y - y_start

                    if self.tiles[x, y] == tile_types.wall:
                        console.tiles_rgb[console_x, console_y] = tile_types.wall["light"]
                    elif self.tiles[x, y] == tile_types.floor:
                        console.tiles_rgb[console_x, console_y] = tile_types.floor["light"]
                    elif self.tiles[x, y] == tile_types.up_stairs:
                        console.tiles_rgb[console_x, console_y] = tile_types.up_stairs["light"]
                    elif self.tiles[x, y] == tile_types.down_stairs:
                        console.tiles_rgb[console_x, console_y] = tile_types.down_stairs["light"]

                elif self.explored[x, y]:
                    # where the tiles will be shifted to
                    console_x = x - x_start
                    console_y = y - y_start
                    if self.tiles[x, y] == tile_types.wall:
                        console.tiles_rgb[console_x, console_y] = tile_types.wall["dark"]
                    elif self.tiles[x, y] == tile_types.floor:
                        console.tiles_rgb[console_x, console_y] = tile_types.floor["dark"]
                    elif self.tiles[x, y] == tile_types.up_stairs:
                        console.tiles_rgb[console_x, console_y] = tile_types.up_stairs["dark"]
                    elif self.tiles[x, y] == tile_types.down_stairs:
                        console.tiles_rgb[console_x, console_y] = tile_types.down_stairs["dark"]

        # same as before, we sort all the entities so that the render order is correct.
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        # looping through each entity, if they are visible we must shift the location they are rendered
        # at as well.
        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                # Calculate the entity's rendering position
                render_x = entity.x - x_start
                render_y = entity.y - y_start

                console.print(
                    x=render_x, y=render_y, string=entity.char, fg=entity.color
                )

        self.x_start = x_start
        self.y_start = y_start


class GameWorld:
    """
    Holds the settings for the GameMap, generates new maps when moving down the stairs, and holds the previous
    maps to move up the stairs.
    """

    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

        self.upstairs_saves = []
        self.downstairs_saves = []

    def generate_floor(self) -> None:
        from procgen import generate_rectangular_dungeon, generate_cellular_automata_dungeon, \
            generate_simplex_noise_dungeon

        self.current_floor += 1

        if self.engine.procgen_type == "Rectangular Room":
            self.engine.game_map = generate_rectangular_dungeon(
                max_rooms=self.max_rooms,
                room_min_size=self.room_min_size,
                room_max_size=self.room_max_size,
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
            )

        elif self.engine.procgen_type == "Cellular Automata":
            self.engine.game_map = generate_cellular_automata_dungeon(
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
                number_of_steps=5,
                max_rooms=self.max_rooms
            )

        elif self.engine.procgen_type == "Simplex Noise":
            # may change later
            self.engine.seed = random.randint(0, 50)
            self.engine.game_map = generate_simplex_noise_dungeon(
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
                seed=self.engine.seed,
                max_rooms=self.max_rooms
            )

    def downstairs_floor(self) -> None:
        # deleting the previous upstairs save
        if len(self.upstairs_saves) > 1:
            self.upstairs_saves.pop()

        # save the current floor as upstairs, since we are going down
        self.save_floor_upstairs()

        if len(self.downstairs_saves) == 0:
            self.generate_floor()
        else:
            self.current_floor += 1
            self.engine.game_map = self.downstairs_saves.pop()
            self.engine.player.place(self.engine.game_map.upstairs_location[0],
                                     self.engine.game_map.upstairs_location[1],
                                     self.engine.game_map)

    def upstairs_floor(self) -> None:
        # deleting the previous downstairs save
        if len(self.downstairs_saves) > 1:
            self.downstairs_saves.pop()

        # save the current floor as downstairs since we are going up
        self.save_floor_downstairs()

        self.current_floor -= 1
        self.engine.game_map = self.upstairs_saves.pop()
        self.engine.player.place(self.engine.game_map.downstairs_location[0],
                                 self.engine.game_map.downstairs_location[1],
                                 self.engine.game_map)

    def save_floor_upstairs(self) -> None:
        self.upstairs_saves.append(self.engine.game_map)

    def save_floor_downstairs(self) -> None:
        self.downstairs_saves.append(self.engine.game_map)
