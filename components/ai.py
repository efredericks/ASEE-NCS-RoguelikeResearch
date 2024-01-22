from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

import color
import dynamic_messages
from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction, PickupAction

if TYPE_CHECKING:
    from entity import Actor, Item


class BaseAI(Action):

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
            self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y, ).perform()


class PoisonedEnemy(BaseAI):
    """
    A Poisoned enemy will behave as normal, simply taking poison damage.
    """

    def __init__(
            self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int, damage: int,
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining
        self.damage = damage

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer poisoned!"
            )
            self.entity.ai = self.previous_ai
        else:
            self.previous_ai.perform()
            self.engine.message_log.add_message(
                f"{dynamic_messages.entity_state_grammer.flatten('#poison_effect_ongoing')} {self.entity.name}, doing {self.damage} damage!",
                color.green
            )
            self.entity.fighter.take_damage(self.damage)


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()


class AutoExploring(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.flood_fill = None
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        if self.engine.player.fighter.hp <= 25 and self.are_enemies_on_map():
            self.engine.player.ai = HostileEnemy(self.engine.player)
            self.engine.message_log.add_message(dynamic_messages.entity_state_grammer.flatten('#auto-explore_no_health#'),
                                                color.red)
            return False
        elif len(self.engine.player.inventory.items) == self.engine.player.inventory.capacity:
            self.engine.message_log.add_message(dynamic_messages.entity_state_grammer.flatten('#full_inventory#'), color.red)
            self.engine.player.ai = HostileEnemy(self.engine.player)
            return False

        closest_item = self.find_closest_item()
        if closest_item is not None:
            dx = closest_item.x - self.engine.player.x
            dy = closest_item.y - self.engine.player.y
            distance = max(abs(dx), abs(dy))  # Chebyshev distance.

            if self.engine.game_map.visible[closest_item.x, closest_item.y]:
                if distance == 0:
                    self.engine.message_log.add_message(dynamic_messages.entity_state_grammer.flatten('#item_found#'), color.green)
                    PickupAction(self.engine.player).perform()
                    return True

            self.path = self.get_path_to(closest_item.x, closest_item.y)

        for enemy in set(self.engine.game_map.actors) - {self.engine.player}:
            if enemy.is_alive:
                dx = enemy.x - self.engine.player.x
                dy = enemy.y - self.engine.player.y
                distance = max(abs(dx), abs(dy))  # Chebyshev distance.
                if self.engine.game_map.visible[enemy.x, enemy.y]:
                    if distance <= 1:
                        MeleeAction(self.engine.player, dx, dy).perform()
                        return True
                self.path = self.get_path_to(enemy.x, enemy.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            MovementAction(
                self.engine.player, dest_x - self.engine.player.x, dest_y - self.engine.player.y,
            ).perform()
            self.engine.update_fov()
            return True

        self.engine.message_log.add_message(dynamic_messages.entity_state_grammer.flatten('#exploration_complete#'), color.green)
        self.engine.player.ai = HostileEnemy(self.engine.player)
        return False

    def find_closest_item(self) -> Optional[Item]:
        closest_item = None
        closest_distance = float("inf")
        for item in self.engine.game_map.items:
            dx = item.x - self.engine.player.x
            dy = item.y - self.engine.player.y
            distance = max(abs(dx), abs(dy))
            if distance < closest_distance:
                closest_item = item
                closest_distance = distance
        return closest_item

    def are_enemies_on_map(self) -> bool:
        for actor in self.engine.game_map.actors:
            if actor is not self.engine.player and actor.is_alive:
                return True
        return False




