import color
import dynamic_messages
from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
import tcod

entity_tileset = tcod.tileset.load_tilesheet(
    "tileset.png", 16, 16, tcod.tileset.CHARMAP_TCOD
)

player_attributes, player_class = dynamic_messages.assign_player_stats()
hp = player_attributes[0]
defense = player_attributes[1]
power = player_attributes[2]

player = Actor(
    char="@",
    color=color.white,
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=hp, base_defense=defense, base_power=power),
    inventory=Inventory(capacity=8),
    level=Level(level_up_base=50),
)

# Enemies
bat = Actor(
    char="b",
    color=color.black,
    name="Bat",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=10),
)
spider = Actor(
    char="s",
    color=color.grey,
    name="Black Widow Spider",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=0, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=10),
)
rat = Actor(
    char="r",
    color=color.brown,
    name="Giant Rat",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=25, base_defense=3, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50),
)
marionette = Actor(
    char="M",
    color=color.red,
    name="Cursed Marionette",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=25, base_defense=2, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75),
)
skeleton = Actor(
    char="S",
    color=color.grey,
    name="Risen Skeleton",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=3, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
serpent = Actor(
    char="s",
    color=color.red,
    name="Serpent",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=35, base_defense=5, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=125),
)
troll = Actor(
    char="T",
    color=color.green,
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=40, base_defense=5, base_power=11),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=125),
)
orc = Actor(
    char="O",
    color=color.green,
    name="Giant Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=50, base_defense=6, base_power=12),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=150),
)
knight = Actor(
    char="K",
    color=color.silver,
    name="Undead Knight",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=60, base_defense=8, base_power=13),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=175),
)
wraith = Actor(
    char="W",
    color=color.grey,
    name="Wraith",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=75, base_defense=6, base_power=13),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=200),
)

# Boss Fight Enemies
reaper_henchmen = Actor(
    char="r",
    color=(0, 255, 0),
    name="Reaper's Henchmen",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=80, base_defense=7, base_power=13),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=250),
)
grim_reaper = Actor(
    char="R",
    color=(0, 255, 0),
    name="Grim Reaper",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=75, base_defense=8, base_power=15),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=300),
)

# Items
confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=5),
    stack_size=3
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=10, radius=3),
    stack_size=3
)
smite_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Smite Scroll",
    consumable=consumable.SmiteDamageConsumable(damage=15, maximum_range=5),
    stack_size=3
)
chain_lighting_scroll = Item(
    char="~",
    color=(230, 230, 0),
    name="Chain Lightning Scroll",
    consumable=consumable.ChainLightingDamageConsumable(damage=10, maximum_range=8),
    stack_size=3
)
poison_scroll = Item(
    char="~",
    color=(34, 139, 34),
    name="Poison Scroll",
    consumable=consumable.PoisonConsumable(damage=5, maximum_range=8, number_of_turns=3),
    stack_size=3
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=10),
    stack_size=5
)
arrow = Item(
    char="^",
    color=(255, 255, 255),
    name="Arrow",
    consumable=consumable.ArrowConsumable(damage=5, player_inventory=player.inventory),
    stack_size=10
)

# Equipment

# Class items (can also spawn in earlier levels)

# Knight
longsword = Item(char="/", color=(0, 191, 255), name="Longsword", equippable=equippable.Longsword())
knights_armor = Item(char="[", color=(139, 69, 19), name="Knight's Armor", equippable=equippable.KnightsArmor())

# Gladiator
bludgeon = Item(char='/', color=(0, 191, 255), name='Heavy Bludgeon', equippable=equippable.HeavyBludgeon())
lightweight_chest_plate = Item(char="[", color=(139, 69, 19), name="Gladiator's Chest-plate",
                               equippable=equippable.ChestPlate())

# Archer
bow = Item(char="}", color=(255, 255, 255), name="Longbow", equippable=equippable.Bow())
tunic = Item(char="[", color=(139, 69, 19), name='Lightweight Tunic', equippable=equippable.LightweightTunic())

# Rogue
twin_daggers = Item(char="/", color=(255, 255, 255), name='Twin Daggers', equippable=equippable.TwinDaggers())
shrouded_cloak = Item(char="[", color=(139, 69, 19), name='Shrouded Cloak', equippable=equippable.ShroudedCloak())

# Non-class based Equipment
serpents_fang = Item(char="/", color=(32, 186, 109), name="Serpent's Fang", equippable=equippable.SerpentsFang())
cyclops_club = Item(char="/", color=(101, 67, 33), name="Cyclops's Club", equippable=equippable.CyclopsClub())
doombringer_axe = Item(char="/", color=(181, 0, 0), name="Doombringer Axe", equippable=equippable.DoomBringerAxe())
soulreaver_scythe = Item(char='/', color=(70, 70, 70), name="Soulreaver Scythe",
                         equippable=equippable.SoulreaverScythe())
flamebrand_sword = Item(char='/', color=(255, 120, 0), name="Flamebrand Sword", equippable=equippable.FlamebrandSword())
thor_hammer = Item(char='/', color=(0, 102, 255), name="Thor Hammer", equippable=equippable.ThorHammer())

cursed_thornail = Item(char="[", color=(108, 31, 49), name="Cursed Thornail", equippable=equippable.CursedThornail())
viperlord_vesture = Item(char="[", color=(0, 102, 255), name="Viperlord Vesture",
                         equippable=equippable.ViperlordVesture())
lunar_weaver = Item(char="[", color=(150, 190, 255), name="Lunar Weaver", equippable=equippable.LunarweaverCloak())
dragonscale_armor = Item(char="[", color=(62, 38, 4), name="Dragonscale Armor",
                         equippable=equippable.DragonscaleArmor())
flameshroud_regalia = Item(char="[", color=(255, 0, 0), name="Flameshroud Regalia",
                           equippable=equippable.FlameshroudRegalia())
stormbreaker_plate = Item(char="[", color=(0, 204, 255), name="Stormbreaker Plate",
                          equippable=equippable.StormbreakerPlate())

# Starting classes for the player
if player_class == 'Archer':
    starting_items = [bow, tunic]
    item = arrow
    player.inventory.items[arrow.name] = [[arrow]]
    for _ in range(9):
        item = arrow
        player.inventory.items[arrow.name][-1].append(item)
        item.parent = player.inventory
elif player_class == 'Knight':
    starting_items = [longsword, knights_armor]
elif player_class == 'Gladiator':
    starting_items = [bludgeon, lightweight_chest_plate]
elif player_class == 'Rogue':
    starting_items = [twin_daggers, shrouded_cloak]

for item in starting_items:
    player.inventory.items[item.name] = [[item]]
    if item.equippable:
        player.equipment.toggle_equip(item, add_message=False)