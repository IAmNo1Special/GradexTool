from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class allmoves(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allmoves_embed(self) -> Any:
        embed = discord.Embed(
            title="Full Move List (Page 1)",
            description="""__**Move**__
Absorb
Acid
Acid Spray
Acrobatics
Aerial Ace
After You
Agility
Air Cutter
Air Slash
Amnesia
Ancient Power
Aqua Jet
Aqua Ring
Aqua Tail
Arobatics
Aromatherapy
Assurance
Astonish
Attack Order
Attract
Aura Sphere
Autotomize
Avalanche
Baby Doll Eyes
Barrier
Baton Pass
Beat Up
Belch
Belly Drum
Bestow
Bide
Bind
Bite
Blast Burn
Blizzard
Block
Body Slam
Bounce
Brave Bird
Brick Break
Brine
Brutal Swing
Bubble
Bubble Beam
Bug Bite
Bug Buzz
Bulk Up
Bulldoze
Bullet Punch
Bullet Seed
Burn Up
Calm Mind
Captivate
Charge
Charge Beam
Charm
Chip Away
Circle Throw
Clear Smog
Close Combat
Coil
Comet Punch
Confide
Confuse Ray
Confusion
Constrict
Copycat
Cotton Guard
Cotton Spore
Counter
Covet
Crabhammer
Crafty Shield
Cross Chop
Cross Toxic
Crunch
Crush Claw
Curse
Dazzling Gleam
Defend Order
Defense Curl
Defog
Destiny Bond
Detect
Dig
Disable
Disarming Voice
Discharge
Dizzy Punch
Double Edge
Double Hit
Double Kick
Double Slap
Double Team
Draco Meteor
Dragon Breath
Dragon Claw
Dragon Dance
Dragon Hammer
Dragon Pulse
Dragon Rage
Dragon Rush
Dragon Tail
Drain Punch
Draining Kiss
Dream Eater
Drill Peck
Dual Chop
Dynamic Punch
Earth Power
Earthquake
Echoed Voice
Eerie Impulse
Egg Bomb
Electric Terrain
Electro Ball
Electroweb
Embargo
Ember
Encore
Endeavor
Endure
Energy Ball
Eruption
Explosion
Extrasensory
Extreme Speed
Facade
Fake Out
Fake Tears
Fakeout
False Swipe
Feather Dance
Feint
Feint Attack
Fell Stinger
Fiery Dance
Final Gambit
Fire Blast
Fire Fang
Fire Pledge
Fire Punch
Fire Spin
Fissure
Flail
Flame Burst
Flame Charge
Flame Wheel
Flamethrower
Flare Blitz
Flash Cannon
Flatter
Fling
Fly
Focus Blast
Focus Energy
Focus Punch
Follow Me
Force Palm
Foresight
Forest Knot
Forest Pledge
Forest Whistle
Foresty Terrain
Foul Play
Frenzy Plant
Frost Breath
Frustration
Fury Attack
Fury Cutter
Fury Swipes
Future Sight
Gastro Acid
Giga Drain
Giga Impact
Glare
Gravity
Growl
Growth
Grudge
Guard Swap
Guillotine
Gunk Shot
Gust
Gyro Ball
Hail
Hammer Arm
Harden
Haze
Headbutt
Heal Bell""",
            color=discord.Color.red(),
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class allmoves_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Page 2",
            style=discord.ButtonStyle.green,
            custom_id="All Moves 2",
        )
        async def allmoves_page2(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]  # noqa: N803
        ) -> None:
            allmoves2_embed = discord.Embed(
                title="Full Move List (Page 2)",
                description="""__**Move Name**__
Heal Block
Heal Order
Heal Pulse
Healing Wish
Heat Wave
Heavy Slam
Helping Hand
Hex
Hidden Power
High Horsepower
Hone Claws
Howl
Hurricane
Hydro Cannon
Hydro Pump
Hyper Beam
Hyper Fang
Hyper Voice
Hypnosis
Ice Ball
Ice Beam
Ice Fang
Ice Hammer
Ice Punch
Icicle Crash
Icy Wind
Imprison
Incinerate
Inferno
Infestation
Ingrain
Iron Defense
Iron Head
Iron Tail
Karate Chop
Knock Off
Last Resort
Lava Plume
Leaf Blade
Leaf Storm
Leaf Tornado
Leech Life
Leech Seed
Leer
Lick
Light Screen
Lock On
Low Kick
Low Sweep
Lucky Chant
Mach Punch
Magic Room
Magical Leaf
Magnet Rise
Magnetic Flux
Magnitude
Me First
Mean Look
Mediate
Meditate
Mega Drain
Mega Punch
Megahorn
Memento
Metal Burst
Metal Claw
Metal Sound
Metal Wing
Meteor Mash
Metronome
Mind Reader
Minimize
Miracle Eye
Mirror Coat
Mirror Move
Mirror Shot
Mist
Moonlight
Morning Sun
Mud Bomb
Mud Shot
Mud Slap
Mud Sport
Muddy Water
Nasty Plot
Natural Gift
Nature Power
Night Shade
Night Slash
Nightmare
Nuzzle
Odor Sleuth
Ominous Wind
Outrage
Overheat
Pain Split
Parting Shot
Payback
Peck
Perish Song
Petal Blizzard
Petal Dance
Phantom Force
Pin Missile
Play Nice
Play Rough
Pluck
Pound
Powder Snow
Power Gem
Power Swap
Power Trick
Power Trip
Power Up Punch
Power Whip
Present
Protect
Psybeam
Psych Up
Psycho Cut
Psycho Shift
Psyshock
Psywave
Punishment
Pursuit
Quash
Quick Attack
Quick Guard
Quiver Dance
Rage
Rage Powder
Rain Dance
Rapid Spin
Razor Leaf
Razor Wind
Recover
Recycle
Reflect
Reflect Type
Refresh
Rest
Return
Revenge
Reversal
Roar
Rolling Kick
Rollout
Roost
Rototiler
Round
Safeguard
Sand Attack
Sand Tomb
Sandstorm
Scald
Scary Face
Scratch
Screech
Secret Power
Seed Bomb
Seismic Toss
Self Destruct
Shadow Ball
Shadow Claw
Shadow Punch
Shift Gear
Shock Wave
Signal Beam
Silver Wind
Simple Beam
Sing
Skull Bash
Sky Attack
Sky Drop
Slam
Slash
Sleep Powder
Sleep Talk
Sludge
Sludge Bomb
Sludge Wave
Smack Down
Smart Strike
Smelling Salts
Smog
Smokescreen
Snarl
Snatch
Snore
Soak
Soft Boiled
Solar Beam
Spark
Spikes""",
                color=discord.Color.red(),
            )
            allmoves2_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=allmoves2_embed, ephemeral=True)

        @discord.ui.button(
            label="Page 3",
            style=discord.ButtonStyle.green,
            custom_id="All Moves 3",
        )
        async def allmoves_page3(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]  # noqa: N803
        ) -> None:
            allmoves3_embed = discord.Embed(
                title="Full Move List (Page 3)",
                description="""__**Move Name**__
Spirit Lock
Spirit Wind
Spit Up
Spite
Splash
Stealth Stone
Steamroller
Sticky Web
Stockpile
Stomp
Stomping Tantrum
Stone Blast
Stone Climb
Stone Edge
Stone Polish
Stone Slide
Stone Smash
Stone Throw
Stone Tomb
Stored Power
Strength
Strength Sap
String Shot
Struggle Bug
Stun Spore
Submission
Substitute
Sucker Punch
Sunny Day
Super Fang
Superpower
Supersonic
Surf
Swagger
Swallow
Sweet Kiss
Sweet Scent
Swift
Switcheroo
Swords Dance
Synchronoise
Synthesis
Tackle
Tail Whip
Tailwind
Take Down
Taunt
Teeter Dance
Thief
Thrash
Thunder
Thunder Fang
Thunder Punch
Thunder Shock
Thunder Wave
Thunderbolt
Tickle
Time
Torment
Toxic
Toxic Fang
Toxic Jab
Toxic Powder
Toxic Spikes
Toxic Sting
Toxic Tail
Tri Attack
Trick Room
Twilight Pulse
Twineedle
Twister
U Turn
Uproar
Venom Drench
Venoshock
Vice Grip
Vine Whip
Vital Throw
Volt Switch
Wake Up Slap
Water Gun
Water Pledge
Water Pulse
Water Sport
Water Spout
Waterfall
Whirlpool
Whirlwind
Wide Guard
Wild Charge
Will O Wisp
Wing Attack
Wish
Withdraw
Wonder Room
Work Up
Worry Seed
Wrap
Wring Out
X Scissor
Yawn
Zap Cannon
Zen Headbutt""",
                color=discord.Color.red(),
            )
            allmoves3_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=allmoves3_embed, ephemeral=True)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]  # noqa: N803
        ) -> None:
            if interaction.message:

                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(All Moves Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all moves" or prompt == "moves":
                embed = self.allmoves_embed()
                buttons = self.allmoves_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allmoves(gradex))
