from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: Dict[str, List[List[Item]]] = {}

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        item_list = self.engine.player.inventory.items.get(item.name)
        if item_list is not None:
            for stack in item_list:
                if item in stack:
                    stack.remove(item)
                    self.engine.message_log.add_message(f"You dropped the {item.name}.")
                    item.place(self.parent.x, self.parent.y, self.gamemap)

                    if [] in item_list:
                        item_list.remove([])
                    if len(self.engine.player.inventory.items[item.name]) == 0:
                        del self.engine.player.inventory.items[item.name]
                    break

    def scale_capacity(self, amount: int):
        self.capacity += amount
