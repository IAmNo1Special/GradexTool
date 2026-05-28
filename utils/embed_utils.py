from discord import Color, Embed


def intro(attributes: dict) -> Embed:
    embed = Embed(
        title=f"{attributes['name'].title()}",
        description=f"*{attributes['main_description'].capitalize()}*",
        color=Color.red(),
        url=f"https://revomon.online/revodex/revomon/{attributes['name']}/",
    )
    embed.add_field(
        name="__Tier__", value=attributes["cdex_tier"].upper(), inline=False
    )
    embed.add_field(
        name="__Rarity__", value=attributes["rarity"].title(), inline=False
    )
    if attributes["type2"] is None:
        embed.add_field(
            name="__Type__", value=attributes["type1"].title(), inline=False
        )
    else:
        embed.add_field(
            name="__Type__",
            value=f"{attributes['type1'].title()} | {attributes['type2'].title()}",
            inline=False,
        )
    embed.add_field(
        name="__Ability(1)__",
        value=attributes["ability1"].title(),
        inline=False,
    )
    if attributes["ability2"] is not None:
        embed.add_field(
            name="__Ability(2)__",
            value=attributes["ability2"].title(),
            inline=False,
        )
    if attributes["abilityh"] is not None:
        embed.add_field(
            name="__Ability(h)__",
            value=attributes["abilityh"].title(),
            inline=False,
        )
    if attributes["evolution"] is None:
        embed.add_field(
            name="__Evolution__", value="Final Evolution", inline=False
        )
    else:
        embed.add_field(
            name="__Evolution__",
            value=f"{attributes['evolution'].title()} -> {attributes['evolution_lvl']}",
            inline=False,
        )
    embed.add_field(
        name="__Evolution Tree__",
        value=attributes["evolution_tree"],
        inline=False,
    )
    if attributes["ev_gains2"] is not None:
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"{attributes['ev_gains1']} | {attributes['ev_gains2']}",
            inline=False,
        )
    else:
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"{attributes['ev_gains1']} | {attributes['ev_gains2']}",
            inline=False,
        )
    embed.set_thumbnail(url=attributes["profile_img"])
    embed.set_footer(text="The Elder's Library · Global Revomon Association")
    return embed


def land_intro(attributes: dict) -> Embed:
    embed = Embed(
        title=f"{attributes['land_type'].title()} in the {attributes['biome'].title()} Biome",
        color=Color.red(),
        url=f"https://tokentrove.com/collection/RevomonNovusLands/zkEVM-{attributes['token_id']}",
    )
    embed.add_field(
        name="__For Sale__", value=attributes["for_sale"], inline=False
    )
    embed.add_field(
        name="__Price__",
        value=f"{round(attributes['for_sale_token'], 4)} {attributes['token_symbol']} · (${attributes['for_sale_usd']})",
        inline=False,
    ) if attributes["for_sale"] else None
    embed.add_field(
        name="__Token ID__", value=attributes["token_id"], inline=False
    )
    embed.add_field(
        name="__Land Owner__",
        value=f"{attributes['owners_address']}",
        inline=False,
    )
    embed.add_field(
        name="__Rarity__", value=attributes["rarity"].title(), inline=False
    )
    embed.add_field(
        name="__Size__", value=attributes["size"].title(), inline=False
    )
    embed.set_thumbnail(url=attributes["img_url"])
    embed.set_footer(text="The Elder's Library · Global Revomon Association")
    return embed


def compare_intros(attributes: dict, attributes2: dict) -> Embed:
    embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}\n{attributes2['num']}. {attributes2['name'].title()}",
        description=f"__**Description**__\n- {attributes['num']}. {attributes['main_description'].capitalize()}\n\n- {attributes2['emoji']} | {attributes2['main_description'].capitalize()}",
        color=Color.red(),
    )
    embed.add_field(
        name="__Tier__",
        value=f"- {attributes['emoji']} | {attributes['cdex_tier'].upper()}\n- {attributes2['emoji']} | {attributes2['cdex_tier'].upper()}",
        inline=False,
    )
    embed.add_field(
        name="__Rarity__",
        value=f"- {attributes['emoji']} | {attributes['rarity'].title()}\n- {attributes2['emoji']} | {attributes2['rarity'].title()}",
        inline=False,
    )
    if attributes["type2"] is None and attributes2["type2"] is None:
        embed.add_field(
            name="__Type__",
            value=f"- {attributes['emoji']} | {attributes['type1'].title()}\n- {attributes2['emoji']} | {attributes2['type1'].title()}",
            inline=False,
        )
    elif attributes["type2"] is None and attributes2["type2"] != "None":
        embed.add_field(
            name="__Type__",
            value=f"- {attributes['emoji']} | {attributes['type1'].title()}\n- {attributes2['emoji']} | {attributes2['type1'].title()} • {attributes2['type2'].title()}",
            inline=False,
        )
    elif attributes["type2"] != "None" and attributes2["type2"] is None:
        embed.add_field(
            name="__Type__",
            value=f"- {attributes['emoji']} | {attributes['type1'].title()} | {attributes['type2'].title()}\n- {attributes2['emoji']} | {attributes2['type1'].title()}",
            inline=False,
        )
    else:
        embed.add_field(
            name="__Type__",
            value=f"- {attributes['emoji']} | {attributes['type1'].title()} • {attributes['type2'].title()}\n- {attributes2['emoji']} | {attributes2['type1'].title()} • {attributes2['type2'].title()}",
            inline=False,
        )
    embed.add_field(
        name="__Abilities__",
        value=f"- {attributes['emoji']} | {attributes['ability1'].title()}{' • ' + attributes['ability2'].title() if attributes['ability2'] is not None else ''}{' • ' + attributes['abilityh'].title() if attributes['abilityh'] is not None else ''}\n- {attributes2['emoji']} | {attributes2['ability1'].title()}{' • ' + attributes2['ability2'].title() if attributes2['ability2'] is not None else ''}{' • ' + attributes2['abilityh'].title() if attributes2['abilityh'] is not None else ''}",
        inline=False,
    )
    if attributes["evolution"] is None and attributes2["evolution"] is None:
        embed.add_field(
            name="__Evolution__",
            value=f"- {attributes['emoji']} | Final Evolution\n- {attributes2['emoji']} | Final Evolution",
            inline=False,
        )
    elif (
        attributes["evolution"] is not None and attributes2["evolution"] is None
    ):
        embed.add_field(
            name="__Evolution__",
            value=f"- {attributes['emoji']} | {attributes['evolution'].title()} -> {attributes['evolution_lvl']}\n- {attributes2['emoji']} | Final Evolution",
            inline=False,
        )
    elif (
        attributes["evolution"] is None and attributes2["evolution"] is not None
    ):
        embed.add_field(
            name="__Evolution__",
            value=f"- {attributes['emoji']} | Final Evolution\n- {attributes2['emoji']} | {attributes2['evolution'].title()} -> {attributes2['evolution_lvl']}",
            inline=False,
        )
    elif (
        attributes["evolution"] is not None
        and attributes2["evolution"] is not None
    ):
        embed.add_field(
            name="__Evolution__",
            value=f"- {attributes['emoji']} | {attributes['evolution'].title()} -> {attributes['evolution_lvl']}\n- {attributes2['emoji']} | {attributes2['evolution'].title()} -> {attributes2['evolution_lvl']}",
            inline=False,
        )
    embed.add_field(
        name="__Evolution Tree__",
        value=f"- {attributes['emoji']} | {attributes['evolution_tree']}\n- {attributes2['emoji']} | {attributes2['evolution_tree']}",
        inline=False,
    )
    if (
        attributes["ev_gains2"] is not None
        and attributes2["ev_gains2"] is not None
    ):
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"- {attributes['emoji']} | {attributes['ev_gains1']} • {attributes['ev_gains2']}\n- {attributes2['emoji']} | {attributes2['ev_gains1']} • {attributes2['ev_gains2']}",
            inline=False,
        )
    elif (
        attributes["ev_gains2"] is None and attributes2["ev_gains2"] is not None
    ):
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"- {attributes['emoji']} | {attributes['ev_gains1']}\n- {attributes2['emoji']} | {attributes2['ev_gains1']} • {attributes2['ev_gains2']}",
            inline=False,
        )
    elif (
        attributes["ev_gains2"] is not None and attributes2["ev_gains2"] is None
    ):
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"- {attributes['emoji']} | {attributes['ev_gains1']} • {attributes['ev_gains2']}\n- {attributes2['emoji']} | {attributes2['ev_gains1']}",
            inline=False,
        )
    elif attributes["ev_gains2"] is None and attributes2["ev_gains2"] is None:
        embed.add_field(
            name="__EV Gains From Battle__",
            value=f"- {attributes['emoji']} | {attributes['ev_gains1']}\n- {attributes2['emoji']} | {attributes2['ev_gains1']}",
            inline=False,
        )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
    )
    embed.set_footer(text="The Elder's Library · Global Revomon Association")
    return embed


def stats(attributes: dict):
    print("Stats embed is being created...")
    stats_embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}",
        description="*Base Stats*",
        color=Color.red(),
        url=f"https://revomon.online/revodex/revomon/{attributes['name']}/",
    )
    stats_embed.add_field(
        name="__HP__", value=attributes["base_hp"], inline=True
    )
    stats_embed.add_field(
        name="__Atk__", value=attributes["base_atk"], inline=True
    )
    stats_embed.add_field(
        name="__Def__", value=attributes["base_def"], inline=True
    )
    stats_embed.add_field(
        name="__SpA__", value=attributes["base_spa"], inline=True
    )
    stats_embed.add_field(
        name="__SpD__", value=attributes["base_spd"], inline=True
    )
    stats_embed.add_field(
        name="__Spe__", value=attributes["base_spe"], inline=True
    )
    stats_embed.add_field(name="", value="", inline=True)
    stats_embed.add_field(
        name="__Total__", value=attributes["total_stats"], inline=True
    )
    stats_embed.add_field(name="", value="", inline=True)
    stats_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    print("Stats embed has been created!")
    return stats_embed


def compare_stats(attributes: dict, attributes2: dict):
    compare_stats_embed = Embed(
        title=f"{attributes['emoji']} | {attributes['name'].title()}\n{attributes2['emoji']} | {attributes2['name'].title()}",
        description="__**Base Stats**__",
        color=Color.red(),
    )
    hp_difference = attributes["base_hp"] - attributes2["base_hp"]
    atk_difference = attributes["base_atk"] - attributes2["base_atk"]
    def_difference = attributes["base_def"] - attributes2["base_def"]
    spa_difference = attributes["base_spa"] - attributes2["base_spa"]
    spd_difference = attributes["base_spd"] - attributes2["base_spd"]
    spe_difference = attributes["base_spe"] - attributes2["base_spe"]
    total_difference = attributes["total_stats"] - attributes2["total_stats"]
    compare_stats_embed.add_field(
        name="__HP__",
        value=f"- {attributes['emoji']} | {attributes['base_hp']}({hp_difference})\n- {attributes2['emoji']} | {attributes2['base_hp']}({hp_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__Atk__",
        value=f"- {attributes['emoji']} | {attributes['base_atk']}({atk_difference})\n- {attributes2['emoji']} | {attributes2['base_atk']}({atk_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__Def__",
        value=f"- {attributes['emoji']} | {attributes['base_def']}({def_difference})\n- {attributes2['emoji']} | {attributes2['base_def']}({def_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__SpA__",
        value=f"- {attributes['emoji']} | {attributes['base_spa']}({spa_difference})\n- {attributes2['emoji']} | {attributes2['base_spa']}({spa_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__SpD__",
        value=f"- {attributes['emoji']} | {attributes['base_spd']}({spd_difference})\n- {attributes2['emoji']} | {attributes2['base_spd']}({spd_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__Spe__",
        value=f"- {attributes['emoji']} | {attributes['base_spe']}({spe_difference})\n- {attributes2['emoji']} | {attributes2['base_spe']}({spe_difference * -1})",
        inline=True,
    )
    compare_stats_embed.add_field(
        name="__Total__",
        value=f"- {attributes['emoji']} | {attributes['total_stats']}({total_difference})\n- {attributes2['emoji']} | {attributes2['total_stats']}({total_difference * -1})",
        inline=True,
    )
    compare_stats_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return compare_stats_embed


def spawns(attributes: dict):
    spawns_embed = Embed(
        title=f"{attributes['emoji']} | {attributes['name'].title()}",
        description="__**Spawn Info**__",
        color=Color.red(),
    )
    spawn_chart_img = "https://images-ext-2.discordapp.net/external/CvlcL_voeGtzAIdljcdlaC9ng6gZ16SpQMKTGMmJz8Q/https/s3.amazonaws.com/appforest_uf/f1674461101975x224187182516942140/Counterdexspawnchart.png?format=webp&quality=lossless&width=890&height=468"
    spawns_embed.set_image(url=spawn_chart_img)
    spawns_embed.add_field(
        name="__Rarity__",
        value=f"- {attributes['emoji']} | {attributes['rarity'].title()} ({attributes['spawn_rate']})",
    )
    spawns_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return spawns_embed


def compare_spawns(attributes: dict, attributes2: dict):
    compare_spawns_embed = Embed(
        title=f"{attributes['emoji']} | {attributes['name'].title()}\n{attributes2['emoji']} | {attributes2['name'].title()}",
        description="__**Spawn Info**__",
        color=Color.red(),
    )
    spawn_chart_img = "https://images-ext-2.discordapp.net/external/CvlcL_voeGtzAIdljcdlaC9ng6gZ16SpQMKTGMmJz8Q/https/s3.amazonaws.com/appforest_uf/f1674461101975x224187182516942140/Counterdexspawnchart.png?format=webp&quality=lossless&width=890&height=468"
    compare_spawns_embed.set_image(url=spawn_chart_img)
    compare_spawns_embed.add_field(
        name="__Rarity__",
        value=f"- {attributes['emoji']} | {attributes['rarity'].title()} ({attributes['spawn_rate']})\n- {attributes2['emoji']} | {attributes2['rarity'].title()} ({attributes2['spawn_rate']})",
    )
    compare_spawns_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return compare_spawns_embed


def moves(attributes: dict):
    move_list_str = "\n".join([f"- {move}" for move in attributes["move_list"]])

    moves_embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}",
        description=f"__**Move List**__\n\n{move_list_str}",
        color=Color.red(),
    )
    moves_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return moves_embed


# Update this function to include both revomon's move list
def compare_moves(attributes: dict, attributes2: dict):
    compare_moves_embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}",
        description=f"__**Move List**__\n\n{attributes['move_list']}",
        color=Color.red(),
    )
    compare_moves_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return compare_moves_embed


def types(attributes: dict):
    types_embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}",
        description="*Type Chart*",
        color=Color.red(),
        url=f"https://revomon.online/revodex/revomon/{attributes['name']}/",
    )
    types_embed.set_image(url=attributes["type_chart_img"])
    types_embed.set_footer(
        text="The Elder's Library · Global Revomon Association"
    )
    return types_embed


def compare_types(attributes: dict, attributes2: dict):
    type_chart_embed = Embed(
        title=f"{attributes['emoji']} | {attributes['name'].title()}",
        description="__**Type Chart**__",
        color=Color.red(),
    )
    type_chart2_embed = Embed(
        title=f"{attributes2['emoji']} | {attributes2['name'].title()}",
        description="__**Type Chart**__",
        color=Color.red(),
    )
    type_chart_embed.set_image(url=attributes["type_chart_img"])
    type_chart2_embed.set_image(url=attributes2["type_chart_img"])
    type_chart_embed.set_footer(
        text="Global Revomon Association · Global Revomon Association"
    )
    type_chart2_embed.set_footer(
        text="Global Revomon Association · Global Revomon Association"
    )
    return type_chart_embed, type_chart2_embed


def counterdex(attributes: dict):
    counterdex_embed = Embed(
        title=f"{attributes['num']}. {attributes['name'].title()}",
        description=f"*{attributes['cdex_description'].capitalize()}*",
        color=Color.red(),
        url=f"https://revomon.online/revodex/revomon/{attributes['name']}/",
    )
    counterdex_embed.add_field(
        name="__Tier__", value=attributes["cdex_tier"].upper(), inline=True
    )
    counterdex_embed.add_field(
        name="__Type Weakness__",
        value=attributes["weakness"].title(),
        inline=True,
    )
    counterdex_embed.add_field(
        name="__Meta-Builds__",
        value=attributes["meta_build"].title(),
        inline=True,
    )
    counterdex_embed.add_field(
        name="__Meta-Moves__",
        value=attributes["meta_moves"].title(),
        inline=True,
    )
    counterdex_embed.add_field(
        name="__Counters__", value=attributes["counters"].title(), inline=True
    )
    counterdex_logo = "https://s3.amazonaws.com/appforest_uf/f1674460627684x148979553672345730/Counterdexlogo.edit.png"
    counterdex_embed.set_image(url=counterdex_logo)
    counterdex_embed.set_footer(text="Counterdex · Global Revomon Association")
    return counterdex_embed


def compare_counterdexs(attributes: dict, attributes2: dict):
    compare_counterdex_embed = Embed(
        title=f"{attributes['emoji']} | {attributes['name'].title()}\n{attributes2['emoji']} | {attributes2['name'].title()}",
        description=f"__**Description**__\n- {attributes['emoji']} | *{attributes['cdex_description'].capitalize()}*\n\n- {attributes2['emoji']} | *{attributes2['cdex_description'].capitalize()}*",
        color=Color.red(),
    )
    compare_counterdex_embed.add_field(
        name="__Tier__",
        value=f"- {attributes['emoji']} | {attributes['cdex_tier'].upper()}\n\n- {attributes2['emoji']} | {attributes2['cdex_tier'].upper()}",
        inline=True,
    )
    compare_counterdex_embed.add_field(
        name="__Type Weakness__",
        value=f"- {attributes['emoji']}\n{attributes['weakness'].title()}\n\n- {attributes2['emoji']}\n{attributes2['weakness'].title()}",
        inline=True,
    )
    compare_counterdex_embed.add_field(
        name="__Meta-Builds__",
        value=f"- {attributes['emoji']}\n{attributes['meta_build'].title()}\n\n- {attributes2['emoji']}\n{attributes2['meta_build'].title()}",
        inline=True,
    )
    compare_counterdex_embed.add_field(
        name="__Meta-Moves__",
        value=f"- {attributes['emoji']}\n{attributes['meta_moves'].title()}\n\n- {attributes2['emoji']}\n{attributes2['meta_moves'].title()}",
        inline=True,
    )
    compare_counterdex_embed.add_field(
        name="__Counters__",
        value=f"- {attributes['emoji']}\n{attributes['counters'].title()}\n\n- {attributes2['emoji']}\n{attributes2['counters'].title()}",
        inline=True,
    )
    counterdex_logo = "https://s3.amazonaws.com/appforest_uf/f1674460627684x148979553672345730/Counterdexlogo.edit.png"
    compare_counterdex_embed.set_thumbnail(url=counterdex_logo)
    compare_counterdex_embed.set_footer(
        text="Counterdex · Global Revomon Association"
    )
    return compare_counterdex_embed
