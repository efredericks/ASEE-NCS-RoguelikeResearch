import tracery

synopsis_rules = {
    "player_adjective": ["brave", "scared", "terrified", "strong", "tough", "capable"],
    "player_description": ["hero", "adventurer", "warrior", "misfit", "traveler"],
    # "game_name": ["Delve the Dungeon", "Reap the Reaper", "Slay the Reaper", ""]
    "entrance_type": ["undead army", "pit of lava", "main gate", "treacherous drawbridge", "royal guards", "ghouls"],
    "enemy_descriptor": ["various", "ghastly", "enraged", "haunted", "powerful", "magical", "horde of"],
    "location_descriptor": ["wretched", "mysterious", "bountiful"],
    "treasure_descriptor": ["loot", "treasure", "glory", "honor", "fame"],
    "death_descriptor": ["slain", "killed", "brought to death", "removed from this mortal coil", "defeated",
                         "stopped in your tracks"],
    "search_type": ["tirelessly", "endlessly", "quickly"],
    "desire_to_return": ["keep your life", "retain your honor", "win endless glory", "evade your death"],
    "life_descriptor": ["existence", "travels", "journey", "life", "looting", "adventuring", "slaying"],
    "battle_descriptor": ["epic", "heroic"],
    "player_attribute": ["strength", "resolve", "courage", "might", "intellect", "battle-skills"],
    "boss_location": ["somewhere in", "at the pit of", "within the depths of", "in the shadows of", "in the arena of"],
    "good_luck_wish": ["and may the odds be in your favor.", "you'll need it.", "although I'm sure you won't need it.",
                       "you've got this!", "and tread carefully!", "and go forth valiantly!",
                       "and slay those who stand in your way!", "and slay those beasts!"],

    # Starting Classes
    "player_class_message": [
        "a knight, you embody valor and chivalry. You are bestowed with a formidable sword and a suit of armor that symbolizes your noble lineage.",
        "a rogue, you excel in stealth and finesse. You are equipped with a set of razor-sharp daggers and a cloak that shrouds you in darkness.",
        "a gladiator, you are skilled in close combat. You are equipped with a heavy bludgeon and a lightweight chest-plate",
        "an archer, you possess remarkable precision and accuracy. You are provided with a reliable bow and a lightweight tunic.",
        # "As a mage, you command the forces of magic. You are granted a staff infused with immense power and a spellbook containing powerful spells."\
    ],

    "game_synopsis": ["#[player_attribute1:#player_attribute#][player_attribute2:#player_attribute#]["
                      "player_starting_class: #player_class_message#]intro#"],
    "intro": [f"""Greetings #player_adjective# #player_description#, welcome to Delve the Dungeon!

Congratulations on making your way past the #entrance_type# and entering the dungeon itself, I know it was no easy task. 
However, there is no time to catch your breath, as you've alerted the forces of the Grim Reaper, alongside
the #enemy_descriptor# enemies that inhabit this #location_descriptor# place. 

Having cheated death to make your way inside in the persuit of treasure, the Grim Reaper wishes to claim your soul.
He's not alone either, as he's brought plenty of help to search for you within the dungeon's many floors, and he's
even enlisted the help of those native to this dungeon to trust that you are #death_descriptor#. 

Not only must you scour through the dungeon to find a great treasure, but also search #search_type# to locate and 
slay the Grim Reaper, provided you wish to #desire_to_return#. He will stop at nothing to ensure that your 
#life_descriptor# ends here, and the only way to persuade him to stop his attempts on your life are to beat him in a 
battle of #battle_descriptor# proportions!

Rumor has it he awaits your presence #boss_location# the dungeon, as he wishes to test your #player_attribute1# and 
#player_attribute2#. In order to beat him, you'll need to scavenge for weapons and gear from slain travelers and 
enemies that you discover along the way, as this is the only way to become powerful enough to stand a chance against 
him.

As#player_starting_class#

Good luck traveler, #good_luck_wish# Now go forth and Delve the Dungeon!
"""]
}

synopsis_grammer = tracery.Grammar(synopsis_rules)
dynamic_synopsis = synopsis_grammer.flatten('#game_synopsis#')
player_starting_class = synopsis_grammer.flatten('#player_classes#')
player_class_description = f'#{player_starting_class}#'
player_class_description = synopsis_grammer.flatten(player_class_description)

player_class_type = synopsis_grammer.flatten('#player_starting_class#').split()[1]

ranged_weapon_rules = {
    "no_arrows": [
        "You don't have any arrows!",
        "You seemed to have misplaced all of your arrows!",
        "No arrows to be found here!",
        "You misplaced your quiver and can't seem to find any arrows!",
        "You can't seem to find any arrows!",
        "You remember the time when you still had arrows...",
        ""
    ],
    "no_ranged_weapon": [
        "You don't have a ranged weapon equipped.",
        "No ranged weapon equipped!",
        "I bet you wish you had a ranged weapon equipped right now!",
        "Maybe one day you'll equip a ranged weapon...",
        "You must first equip a ranged weapon!"
    ],
    "no_bow": [
        "You don't have a bow!",
        "You can't seem to find a bow in your inventory.",
        "A bow is nowhere to be found.",
        "Need to find a bow first.",
        "In order to use these arrows, you'll need a bow!",
        "These arrows are no use without a bow."
    ],
    "bow_not_equipped": [
        "The bow is not currently equipped.",
        "Equip your bow first!",
        "You need to equip your bow to use it.",
        "Bow not currently equipped!"
    ],
    "equip_bow": [
        "You draw back the bow and take a deep breath.",
        "You inhale deeply and hold, pulling back the longbow's drawstring.",
        "You quickly draw back the bow and scan the room for a target."
    ],
    "target_self_bow": [
        "You cannot shoot yourself!",
        "I used to be an adventurer like you, then I took an arrow in the knee.",
    ],
    "arrow_fired_hit": [
        "You breathe deeply and hold, firing the arrow at the",
        "You quickly release the bow's drawstring and the arrow tears into the",
        "You quickly send an arrow flying into the",
        "After taking a deep breath, you release the arrow and it rips into the"
    ],
    "arrow_pulled_out":
        [
            "pulls out the arrow and throws it to the ground.",
            "angrily yanks out the arrow and tosses it aside.",
            "cries out in pain as it pulls out the arrow and drops it.",
            "wails as it digs out the arrow and drops it to the ground.",
            "laughs as he easily removes the arrow and lets it fall to the ground.",
        ],
    "entity_breaks_arrow":
        [
            "pulls out the arrow and snaps it in half!",
            "laughs as he breaks the arrow off its body!",
            "yanks out the arrow and crushes it beneath its feat.",
            "completely ignores the arrow that's stuck in it!",
            "screams as he pulls out the arrow and breaks it over its knee."
        ],
    "close_miss_arrow_intact":
        [
            "Your aim was shaky and the arrow flies past the ",
            "You trip over a rock and the arrow whizzes by the ",
            "You completely whiff and the arrow is miles off the ",
            "Your arrow seems to have a mind of its own and flies right past the ",
        ],
    "far_miss_arrow_break":
        [
            "You shoot and miss!, the arrow breaks upon impact.",
            "You trip over a rock and fall on your face. The arrow snaps at your feet.",
            "You completely whiff and the arrow is shattered upon impact."
        ],
    "far_miss_arrow_intact":
        [
            "You shoot the arrow but miss! the arrow falls to the ground.",
            "You trip over a rock and the arrow goes flying into the dirt.",
            "You completely whiff and the arrow falls to the floor!",
            "The arrow strikes nothing and falls to the ground.",
            "The arrow tears through the air but finds no target."
        ]
}
ranged_weapon_grammer = tracery.Grammar(ranged_weapon_rules)

entity_state_rules = {
    "level_up": [
        "You've advanced to the next level!",
        "You've just leveled up!",
        "You've earned an upgrade!",
        "You've ascended to a higher level!",
        "You've progressed to the next tier!",
        "You've achieved a level-up milestone!",
        "You've reached a higher level of mastery!",
        "You've successfully leveled up!",
        "You've gained a level boost!",
        "You've risen to a higher rank!",
        "You've advanced to a new tier!",
        "You've earned a promotion!",
        "You've leveled up, raising the bar!",
    ],
    "player_death": [
        "You died!",
        "You were slain!",
        "The Reaper takes your soul.",
        "Your soul is vanquished by the reaper."
        "Your journey has come to an end.",
        "Defeat has claimed you.",
        "The light within you fades away.",
        "The battle has taken its toll on you.",
        "The world mourns your loss.",
        "Your spirit has departed from this realm.",
        "Death's embrace tightens its grip on you.",
        "The shadows consume your essence.",
        "Your legacy ends here.",
        "The echoes of your existence fade into nothingness.",
        "The cycle of life and death claims another victim.",
        "Your last breath escapes you.",
        "The realm mourns the loss of a valiant warrior.",
        "Your name shall be remembered, even in death.",
        "The weight of defeat settles upon you.",
        "Your tale reaches its final chapter.",
        "Your fate has been sealed.",
        "The forces of darkness prevail over you.",
        "Your flame has been extinguished.",
        "Your soul drifts into the eternal abyss.",
        "The world grows dim as you slip into oblivion.",
        "Your time in this realm has reached its limit."
    ],
    "enemy_death": [
        "has been slain!",
        "is dead!",
        "has been vanquished!",
        "falls as you strike them down!",
        "bites the dust as you claim victory!",
        "meets their end as you emerge victorious!",
        "crumbles beneath your might!",
        "is no match for you!",
        "falls before you, and you emerge victorious!",
        "meets a swift demise at your hands!",
        "is defeated on the battlefield!",
        "meets their inevitable defeat in the face of your power!",
        "is slain by your triumph!",
        "crumbles beneath your might!",
        "meets their end as you strike them down!",
        "falls as you leave a trail of victory!",
        "meets their demise, and your triumph prevails!",
        "draws their last breath in the face of your might!",
        "leaves no enemy standing, including them!",
        "becomes a part of your legendary legacy!",
        "cannot withstand your might!",
        "is no more, thanks to your prowess!",
        "meets their end, lying lifeless on the ground!",
        "is defeated, and victory is yours!"
    ],
    "dead_enemy": [
        "remains of",
        "corpse of",
        "carcass of",
        "husk of",
        "skeleton of",
    ],
    "boss_defeated": [
        "has been beaten in combat and have won your right to live. Congratulations adventurer, the treasure is yours!",
        "has been vanquished, and you emerge victorious! Congratulations on your triumph!",
        "meets their end in combat, and you stand as the victor! Well done!",
        "falls before your might, and you claim victory as your rightful prize!",
        "has been defeated in battle, and you prove yourself as the ultimate conqueror!",
        "succumbs to your strength and skill, and you emerge as the triumphant warrior!",
        "meets their final fate at your hands, and you secure your right to live! Well played!",
        "is no match for your prowess, and you emerge as the champion! Congratulations!",
        "falls to your relentless assault, and you claim your well-deserved victory!",
        "meets their ultimate demise, and you stand as the victor in this battle!",
        "has been conquered by your unwavering determination, and you emerge triumphant!",
        "succumbs to your power, and you seize the treasure that is rightfully yours!",
        "meets their end in combat, and you emerge victorious! The spoils of war are yours!",
        "falls before your might, and you claim victory as your just reward! Well done!",
        "has been defeated in battle, and you prove yourself as the ultimate conqueror!",
        "succumbs to your strength and skill, and you emerge as the triumphant warrior!",
        "meets their final fate at your hands, and you secure your right to live! Well played!",
        "is no match for your prowess, and you emerge as the champion! Congratulations!",
        "falls to your relentless assault, and you claim your well-deserved victory!",
        "meets their ultimate demise, and you stand as the victor in this battle!",
        "has been conquered by your unwavering determination, and you emerge triumphant!",
        "succumbs to your power, and you seize the treasure that is rightfully yours!",
    ],
    "auto-explore_no_health": [
        "Health levels critical! Auto-Exploring would result in death.",
        "Can't auto-explore due to low health!",
        "Health too low to auto-explore right now.",
        "Heal up to use auto-explore again.",
        "Auto-exploring would result in death.",
    ],
    "full_inventory": [
        "Inventory is full!",
        "You can't hold anymore items!",
        "Not enough inventory space",
        "You can't carry anymore items!",
        # "Your backpack is full, find a better one to hold more items!"
        # "Upgrade your inventory space to hold more items!"
    ],
    "item_found": [
        "Item found!",
        "You found an item!",
        "An item has been discovered!"
    ],
    "exploration_complete": [
        "Nothing else to explore!",
        "You've explored this level completely!",
        "Nothing else on this level!",
        "Nothing left here!",
        "Head downstairs to progres",
        "This level is fully looted!",
        "You've found all the treasure on this level!"
    ],
    "confusion_effect": [
        " eyes look vacant, as it starts to stumble around!",
        " eyes go blank, and it begins to move erratically.",
        " eyes glaze over, as their movements become uncoordinated.",
        " feet stumble around, as they become increasingly unaware of their surroundings.",
        " feet become heavy, as they enter a state of utter confusion.",
    ],
    "fire_effect": [
        "is engulfed in a fiery explosion,",
        "is lit ablaze,",
        "is set aflame,",
        "bursts into flames,",
        "is roasted by the fire,",
        "is charred by the flames,",
        "spontaneously combusts,",
    ],
    "lightning_effect": [
        "is smitten with a bolt of lightning,",
        "is struck down with lightning,",
        "is zapped with lighting,",
        "is electrified",
        "is fried by electricity,",
    ],
    "lightning_jump_effect": [
        "You shoot lightning from your fingertips, hitting",
        "Lightning strikes down and jumps to the",
        "The lightning crashes upon the",
        "lightning chains onto the",
        "A large burst of lightning shocks the",
        "Electricity emanates from your fingertips, connecting with",
        "Bolts of lightning descend and leap towards the",
        "The thunderous lightning crashes upon the",
        "Arcs of lightning chain onto the",
        "A massive burst of lightning shocks the",
        "Electricity surges from your fingertips, striking",
        "A powerful surge of lightning electrifies the",
        "The thunderous lightning smashes into the",
    ],
    "poison_effect_start": [
        "is jabbed with a poison needle!",
        "is contaminated with a toxic substance!",
        "is injected with a venomous solution!",
        "is struck by a poisonous stinger!",
        "is tainted with a lethal poison!",
        "is exposed to a noxious toxin!"
        "succumbs to a toxic affliction!",
        "is overwhelmed by venomous toxins!",
        "is ensnared in a web of poisonous tendrils!",
        "is consumed by a debilitating poison!",
        "is inflicted with a noxious curse!",
        "is paralyzed by a venomous bite!",
        "is enveloped in a cloud of poisonous gas!",
        "is weakened by a potent venom!",
        "is plagued by a venomous onslaught!",
        "is overcome by a venomous miasma!",
    ],
    "poison_effect_ongoing": [
        "The poison weakens the",
        "Poison deteriorates the",
        "Poison courses through the veins of",
        "The venom enfeebles the",
        "Toxicity ravages the",
        "A lethal toxin undermines the",
        "The noxious substance saps the strength of",
        "Venomous tendrils afflict the",
        "A poisonous brew corrodes the",
        "Corrosive venom eats away at the"
    ],
}
entity_state_grammer = tracery.Grammar(entity_state_rules)


def assign_player_stats():
    if player_class_type == 'archer,':
        return (150, 1, 5), 'Archer'
    elif player_class_type == 'knight,':
        return (80, 3, 8), 'Knight'
    elif player_class_type == 'rogue,':
        return (125, 1, 7), 'Rogue'
    elif player_class_type == 'gladiator,':
        return (100, 5, 5), 'Gladiator'
