from typing import Any

"""Script to process item data from source items.json and save to gradex items.json."""

import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402

from helpers import to_sentence_case  # noqa: E402

logger = logging.getLogger(__name__)


OUTPUT_PATH = Path("data/items.json")
ITEMS = [
    {
        "name": "accuracy up",
        "description": "raises accuracy by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 1000,
    },
    {
        "name": "attack up",
        "description": "raises attack by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 1000,
    },
    {
        "name": "barka fruity",
        "description": "consumed when struck by a super-effective toxic-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "blue orb",
        "description": "tries to catch a wild revomon. success rate is 1.5x",
        "obtained_from": "revocenter",
        "cost": 600,
    },
    {
        "name": "burning cure",
        "description": "cures a burn.",
        "obtained_from": "revocenter",
        "cost": 300,
    },
    {
        "name": "cassius fruity",
        "description": "consumed at 1/2 max hp to recover 1/4 max hp.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "chamo fruity",
        "description": "consumed when struck by a super-effective spirit-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "choda fruity",
        "description": "consumed when struck by a super-effective sky-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "clan gem",
        "description": "a gem that allows you to create your own clan.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "cozi fruity",
        "description": "consumed at 1/4 max hp when using a move to go first.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "critic up",
        "description": "increases the chance of a critical hit in battle.",
        "obtained_from": "revocenter",
        "cost": 1000,
    },
    {
        "name": "dabip fruity",
        "description": "consumed when struck by a super-effective electric-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "defense up",
        "description": "raises defense by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 2000,
    },
    {
        "name": "defo fruity",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike bitter flavor.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "derlu fruity",
        "description": "drops special attack effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "ebla fruity",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike sweet flavor.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "effect guard",
        "description": "prevents stat changes in battle for five turns in battle.",
        "obtained_from": "revocenter",
        "cost": 1500,
    },
    {
        "name": "ertha fruity",
        "description": "when the holder is hit by a special move, increases it's special defense by one stage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "freezing cure",
        "description": "cures freezing.",
        "obtained_from": "revocenter",
        "cost": 100,
    },
    {
        "name": "frin fruity",
        "description": "consumed when struck by a super-effective draconic-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "frizy fruity",
        "description": "consumed to deal 1/8 attacker's max hp when holder is struck by a special attack.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "full cure",
        "description": "cures any status ailment and confusion.",
        "obtained_from": "revocenter",
        "cost": 400,
    },
    {
        "name": "full mixture",
        "description": "restores pp to full for each move.",
        "obtained_from": "revocenter",
        "cost": 4500,
    },
    {
        "name": "full potion",
        "description": "restores hp to full.",
        "obtained_from": "revocenter",
        "cost": 2500,
    },
    {
        "name": "full pp aid",
        "description": "restores pp to full for one move.",
        "obtained_from": "revocenter",
        "cost": 2000,
    },
    {
        "name": "full recovery",
        "description": "restores hp to full and cures any status ailment and confusion.",
        "obtained_from": "revocenter",
        "cost": 3000,
    },
    {
        "name": "glandu fruity",
        "description": "consumed at 1/4 max hp to boost defense.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "globop fruity",
        "description": "consumed when struck by a super-effective attack to restore 1/4 max hp.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "golmon fruity",
        "description": "consumed when struck by a super-effective time-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "golu fruity",
        "description": "consumed when frozen to cure frozen.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "green orb",
        "description": "tries to catch a wild revomon. success rate is 2x",
        "obtained_from": "revocenter",
        "cost": 800,
    },
    {
        "name": "gunko fruity",
        "description": "consumed when struck by a super-effective fire-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "gupon fruity",
        "description": "consumed when struck by a super-effective ice-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "hyper potion",
        "description": "restores 200 hp.",
        "obtained_from": "revocenter",
        "cost": 1500,
    },
    {
        "name": "inchu fruity",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike spicy flavor.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "iota fruity",
        "description": "consumed at 1/4 max hp to boost attack.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "issou fruity",
        "description": "drops speed effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "jadwa fruity",
        "description": "consumed when confused to cure confusion.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "juiti fruity",
        "description": "consumed when paralyzed to cure paralysis.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "kanda fruity",
        "description": "consumed when a move runs out of pp to restore it's pp by 10.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "kankoo fruity",
        "description": "drops attack effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "karoto fruity",
        "description": "drops hp effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "lee fruity",
        "description": "when the holder is hit by a physical move, increases it's defense by one stage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "liech fruity",
        "description": "consumed at 1/4 max hp to boost special attack.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "miopi fruity",
        "description": "consumed at 1/4 max hp to boost a random stat by two stages.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "mitsi fruity",
        "description": "consumed at 1/4 max hp to boost accuracy of next move by 20%.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "mixture",
        "description": "restores 10 pp for each move.",
        "obtained_from": "revocenter",
        "cost": 3000,
    },
    {
        "name": "move 01",
        "description": "teaches work up to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 02",
        "description": "teaches draconic claw to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 03",
        "description": "teaches psyshock to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 04",
        "description": "teaches calm mind to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 05",
        "description": "teaches roar to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 06",
        "description": "teaches toxic to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 07",
        "description": "teaches hail to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 08",
        "description": "teaches bulk up to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 09",
        "description": "teaches venoshock to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 10",
        "description": "teaches hidden power to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 100",
        "description": "teaches confide to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 5000,
    },
    {
        "name": "move 11",
        "description": "teaches sunny day to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 12",
        "description": "teaches taunt to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 13",
        "description": "teaches ice beam to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 14",
        "description": "teaches blizzard to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 15",
        "description": "teaches hyper beam to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 16",
        "description": "teaches light screen to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 17",
        "description": "teaches protect to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 18",
        "description": "teaches rain dance to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 19",
        "description": "teaches roost to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 20",
        "description": "teaches safeguard to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 21",
        "description": "teaches frustration to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 22",
        "description": "teaches solarbeam to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 23",
        "description": "teaches smack down to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 24",
        "description": "teaches thunderbolt to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 25",
        "description": "teaches thunder to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 26",
        "description": "teaches earthquake to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 27",
        "description": "teaches return to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 28",
        "description": "teaches leech life to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 29",
        "description": "teaches time to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 30",
        "description": "teaches shadow ball to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 31",
        "description": "teaches brick break to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 32",
        "description": "teaches double team to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 33",
        "description": "teaches reflect to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 34",
        "description": "teaches sludge wave to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 35",
        "description": "teaches flamethrower to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 36",
        "description": "teaches sludge bomb to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 37",
        "description": "teaches sandstorm to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 38",
        "description": "teaches fire blast to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 39",
        "description": "teaches stone tomb to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 40",
        "description": "teaches aerial ace to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 41",
        "description": "teaches torment to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 42",
        "description": "teaches facade to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 43",
        "description": "teaches flame charge to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 44",
        "description": "teaches rest to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 45",
        "description": "teaches attract to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 46",
        "description": "teaches thief to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 47",
        "description": "teaches low sweep to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 48",
        "description": "teaches round to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 49",
        "description": "teaches echoed voice to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 50",
        "description": "teaches overheat to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 80000,
    },
    {
        "name": "move 51",
        "description": "teaches metal wing to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 52",
        "description": "teaches focus blast to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 53",
        "description": "teaches energy ball to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 54",
        "description": "teaches false swipe to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 55",
        "description": "teaches scald to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 56",
        "description": "teaches fling to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 57",
        "description": "teaches charge beam to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 58",
        "description": "teaches sky drop to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 59",
        "description": "teaches brutal swing to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 60",
        "description": "teaches quash to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 61",
        "description": "teaches will-o-wisp to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 62",
        "description": "teaches acrobatics to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 63",
        "description": "teaches embargo to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 64",
        "description": "teaches explosion to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 65",
        "description": "teaches shadow claw to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 66",
        "description": "teaches payback to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 67",
        "description": "teaches smart strike to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 68",
        "description": "teaches giga impact to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 69",
        "description": "teaches stone polish to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 70",
        "description": "teaches aurora veil to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 71",
        "description": "teaches stone edge to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 72",
        "description": "teaches volt switch to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 73",
        "description": "teaches thunder wave to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 5000,
    },
    {
        "name": "move 74",
        "description": "teaches gyro ball to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 75",
        "description": "teaches swords dance to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 76",
        "description": "teaches fly to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 77",
        "description": "teaches psych up to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 78",
        "description": "teaches bulldoze to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 79",
        "description": "teaches frost breath to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 80",
        "description": "teaches stone slide to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 81",
        "description": "teaches x-scissor to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 82",
        "description": "teaches draconic tail to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 83",
        "description": "teaches infestation to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 84",
        "description": "teaches toxic jab to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 85",
        "description": "teaches dream eater to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 86",
        "description": "teaches forest knot to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 87",
        "description": "teaches swagger to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 88",
        "description": "teaches sleep talk to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 89",
        "description": "teaches u-turn to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 90",
        "description": "teaches substitute to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 91",
        "description": "teaches flash cannon to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 92",
        "description": "teaches trick room to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 93",
        "description": "teaches wild charge to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 50000,
    },
    {
        "name": "move 94",
        "description": "teaches surf to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 95",
        "description": "teaches snarl to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 96",
        "description": "teaches nature power to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 97",
        "description": "teaches twilight pulse to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "move 98",
        "description": "teaches waterfall to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 30000,
    },
    {
        "name": "move 99",
        "description": "teaches dazzling gleam to a compatible revomon.",
        "obtained_from": "capsule shop",
        "cost": 10000,
    },
    {
        "name": "nonomi fruity",
        "description": "consumed when struck by a super-effective stone-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "osef fruity",
        "description": "consumed when asleep to cure sleep.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "paia fruity",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike sour flavor.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "papille fruity",
        "description": "drops defense effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "papou fruity",
        "description": "consumed at 1/4 max hp to boost critical hit ratio by two stages.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "paralysis cure",
        "description": "cures paralysis.",
        "obtained_from": "revocenter",
        "cost": 300,
    },
    {
        "name": "peachu fruity",
        "description": "consumed when toxiced to cure toxic.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "potion",
        "description": "restores 20 hp.",
        "obtained_from": "revocenter",
        "cost": 200,
    },
    {
        "name": "pp aid",
        "description": "restores 10 pp for one move.",
        "obtained_from": "revocenter",
        "cost": 1200,
    },
    {
        "name": "pritcha fruity",
        "description": "consumed when struck by a super-effective metal-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "psiro fruity",
        "description": "consumed when struck by a super-effective battle-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "red orb",
        "description": "tries to catch a wild revomon.",
        "obtained_from": "revocenter",
        "cost": 200,
    },
    {
        "name": "ruka fruity",
        "description": "consumed when struck by a super-effective earth-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "sleeping cure",
        "description": "cures sleep.",
        "obtained_from": "revocenter",
        "cost": 100,
    },
    {
        "name": "sp atk up",
        "description": "raises special attack by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 1000,
    },
    {
        "name": "sp def up",
        "description": "raises special defense by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 2000,
    },
    {
        "name": "speed up",
        "description": "raises speed by one stage in battle.",
        "obtained_from": "revocenter",
        "cost": 1000,
    },
    {
        "name": "super potion",
        "description": "restores 50 hp.",
        "obtained_from": "revocenter",
        "cost": 700,
    },
    {
        "name": "tavaa fruity",
        "description": "consumed when struck by a super-effective bug-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "terter fruity",
        "description": "consumed when struck by a super-effective forest-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "tibli fruity",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike dry flavor.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "tipli fruity",
        "description": "consumed when struck by a super-effective phantom-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "toktok fruity",
        "description": "consumed at 1/4 max hp to boost special defense.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "toxic cure",
        "description": "cures toxic.",
        "obtained_from": "revocenter",
        "cost": 200,
    },
    {
        "name": "trars fruity",
        "description": "consumed when struck by a super-effective twilight-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "trigo fruity",
        "description": "consumed at 1/4 max hp to boost speed.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "truduku fruity",
        "description": "consumed when struck by a super-effective water-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "vilvi fruity",
        "description": "consumed to cure any status condition or confusion.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "vrio fruity",
        "description": "consumed at 1/2 max hp to recover 10 hp.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "wilso fruity",
        "description": "drops special defense effort values by 10 and raises happiness.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "wiltu fruity",
        "description": "consumed when burned to cure a burn.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "yannoi fruity",
        "description": "consumed to deal 1/8 attacker's max hp when holder is struck by a physical attack.",
        "obtained_from": "battle reward",
        "cost": None,
    },
    {
        "name": "yululu fruity",
        "description": "consumed when struck by a neutral-type attack to halve the damage.",
        "obtained_from": "battle reward",
        "cost": None,
    },
]


def get_items() -> None:
    items: list[dict[str, Any]] = [dict(item) for item in ITEMS]  # type: ignore
    logger.info(f"Found {len(items)} items. Processing...")

    # Process each item
    for item in items:
        # Lowercase name
        if "name" in item and item["name"] is not None:
            item["name"] = item["name"].lower()
        # Lowercase obtained_from
        if "obtained_from" in item and item["obtained_from"] is not None:
            item["obtained_from"] = item["obtained_from"].lower()
        # Sentence case description
        if "description" in item and item["description"] is not None:
            item["description"] = to_sentence_case(item["description"])

    # Sort alphabetically by name
    items.sort(key=lambda x: x.get("name", ""))

    # Assign sequential IDs and build dict
    items_dict = {}
    for i, item in enumerate(items, start=1):
        item["idItem"] = i
        items_dict[str(i)] = item

    logger.info(f"Saving {len(items_dict)} items to {OUTPUT_PATH}...")
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items_dict, f, indent=2, ensure_ascii=False)

    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    get_items()
