from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
import dynamic_messages
import entity_factories
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def scale_consumable(self) -> None:
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            item_list = self.engine.player.inventory.items.get(entity.name)
            if item_list is not None:
                for stack in item_list:
                    if entity in stack:
                        stack.remove(entity)

                        if [] in item_list:
                            item_list.remove([])
                        if len(self.engine.player.inventory.items[entity.name]) == 0:
                            del self.engine.player.inventory.items[entity.name]
                        break


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The {target.name}'s" + dynamic_messages.entity_state_grammer.flatten('#confusion_effect#'),
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()

    def scale_consumable(self, number_of_turns: int):
        self.number_of_turns += number_of_turns


class ArrowConsumable(Consumable):
    def __init__(self, damage: int, player_inventory: list):
        self.damage = damage
        self.inventory = player_inventory

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        if "Longbow" in self.engine.player.inventory.items.keys():
            if self.engine.player.equipment.item_is_equipped(
                    self.engine.player.inventory.items["Longbow"][-1][-1]):
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#equip_bow#'), color.needs_target
                )
                return SingleRangedAttackHandler(
                    self.engine,
                    callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
                )
            else:
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#bow_not_equipped#'), color.needs_target
                )
                return
        else:
            self.engine.message_log.add_message(
                dynamic_messages.ranged_weapon_grammer.flatten('#no_bow#'),
                color.needs_target
            )
            return

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot shoot an area that you cannot see.")
        # if not target:
        #     raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible(dynamic_messages.ranged_weapon_grammer.flatten('#target_self_bow#'))

        if target:
            if random.random() <= .95:
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#arrow_fired_hit#') + f"{target.name}, dealing {self.damage} damage!",
                    color.player_atk,
                )
                target.fighter.take_damage(self.damage)
                if random.random() <= 85:
                    entity_factories.arrow.spawn(self.engine.game_map, action.target_xy[0], action.target_xy[1])
                    self.engine.message_log.add_message(
                        f"The {target.name}" + dynamic_messages.ranged_weapon_grammer.flatten('#arrow_pulled_out#'),
                        color.green,
                    )
                else:
                    self.engine.message_log.add_message(
                        f"The {target.name}" + dynamic_messages.ranged_weapon_grammer.flatten('#entity_breaks_arrow#'),
                        color.red,
                    )

            else:
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#close_miss_arrow_intact#') + f"{target.name}'s "
                                                                                                  f"head!",
                    color.red,
                )
                entity_factories.arrow.spawn(self.engine.game_map, action.target_xy[0], action.target_xy[1] + 1)
        else:
            if random.random() <= .25:
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#far_miss_arrow_break#'),
                    color.red,
                )
            else:
                self.engine.message_log.add_message(
                    dynamic_messages.ranged_weapon_grammer.flatten('#far_miss_arrow_intact#'),
                    color.green,
                )
                entity_factories.arrow.spawn(self.engine.game_map, action.target_xy[0], action.target_xy[1])
        self.consume()

    def scale_consumable(self, damage: int):
        self.damage += damage


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} {dynamic_messages.entity_state_grammer.flatten('#fire_effect#')} taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()

    def scale_consumable(self, damage: int, radius: int = 0):
        self.damage += damage
        self.radius += radius


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")

    def scale_consumable(self, amount: int):
        self.amount += amount


class SmiteDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"The {target.name} {dynamic_messages.entity_state_grammer.flatten('#lightning_effect#')} dealing {self.damage} damage!",
                color.yellow
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to smite.")

    def scale_consumable(self, damage: int, maximum_range: int = 0):
        self.damage += damage
        self.maximum_range += maximum_range


class ChainLightingDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        targets = [None] * 3
        closest_distances = [self.maximum_range + 1.0] * 3

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                for i, closest_distance_value in enumerate(closest_distances):
                    if distance < closest_distance_value:
                        closest_distances[i] = distance
                        targets.pop()
                        targets.insert(i, actor)
                        break

        targets_hit = False
        for i, target in enumerate(targets):
            if target:
                damage = self.damage - (3 * i)
                if i == 0:
                    self.engine.message_log.add_message(
                        f"{dynamic_messages.entity_state_grammer.flatten('#lightning_jump_effect#')} {target.name} for {damage} damage!",
                        color.yellow
                    )
                elif i == 1:
                    self.engine.message_log.add_message(
                        f"{dynamic_messages.entity_state_grammer.flatten('#lightning_jump_effect#')} {target.name}, dealing {damage} damage!",
                        color.yellow
                    )
                else:
                    self.engine.message_log.add_message(
                        f"{dynamic_messages.entity_state_grammer.flatten('#lightning_jump_effect#')} {target.name}, dealing {damage} damage!",
                        color.yellow
                    )
                target.fighter.take_damage(damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("No enemy is close enough to strike.")

        self.consume()

    def scale_consumable(self, damage: int, maximum_range: int = 0):
        self.damage += damage
        self.maximum_range += maximum_range


class PoisonConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int, number_of_turns: int):
        self.damage = damage
        self.maximum_range = maximum_range
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot poison yourself!")

        self.engine.message_log.add_message(
            f"The {target.name} {dynamic_messages.entity_state_grammer.flatten('#poison_effect_start#')}",
            color.status_effect_applied,
        )
        target.ai = components.ai.PoisonedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns, damage=self.damage
        )
        self.consume()

    def scale_consumable(self, damage: int, maximum_range: int = 0, number_of_turns: int = 0):
        self.damage += damage
        self.maximum_range += maximum_range
        self.number_of_turns += number_of_turns
