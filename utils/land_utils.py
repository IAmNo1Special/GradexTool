from typing import Any
import aiohttp
from typing import Dict, List, Union


async def get_land_info_for_ids(token_ids: List[Any]) -> List[Dict[str, Any]]:
    if len(token_ids) > 30:
        token_ids_list = [token_ids[i : i + 30] for i in range(0, len(token_ids), 30)]
    else:
        token_ids_list = [token_ids]

    land_info = []
    for token_ids in token_ids_list:
        token_ids_str = ""

        for token_id in token_ids:
            if token_ids.index(token_id) == 0:
                token_ids_str += f"?token_id={token_id}"
            else:
                token_ids_str += f"&token_id={token_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/collections/0x5c40eb1eaad2a96e383e3b0a986a5377fc1ee239/nfts{token_ids_str}&page_size=200"
            ) as response:
                nft_objs = await response.json()

        for nft_obj in nft_objs["result"]:
            biome = nft_obj["attributes"][0]["value"].lower()
            token_id = nft_obj["token_id"]
            entity_type = (
                nft_obj["attributes"][2]["value"].lower()
                if len(nft_obj["attributes"]) > 2
                else None
            )
            id = (
                nft_obj["attributes"][3]["value"]
                if len(nft_obj["attributes"]) > 2
                else None
            )
            rarity = (
                nft_obj["attributes"][4]["value"].lower()
                if len(nft_obj["attributes"]) > 2
                else None
            )
            size = (
                nft_obj["attributes"][5]["value"]
                if len(nft_obj["attributes"]) > 2
                else None
            )
            img_url = nft_obj["image"]
            land_info.append(
                {
                    "id": id,
                    "token_id": token_id,
                    "biome": biome,
                    "land_type": entity_type,
                    "rarity": rarity,
                    "size": size,
                    "img_url": img_url,
                }
            )
    return land_info


async def get_land_owners_and_ids() -> List[Dict[str, Any]]:
    print("Retrieving land owner with land ids data...")
    print("Retrieving raw land owner with land ids data...")
    base_url = "https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/collections/0x5c40eb1eaad2a96e383e3b0a986a5377fc1ee239/owners"
    page_cursor = None
    raw_data = list()
    async with aiohttp.ClientSession() as session:
        while True:
            url = (
                f"{base_url}?page_cursor={page_cursor}&page_size=200"
                if page_cursor
                else f"{base_url}?page_size=200"
            )
            async with session.get(url) as response:
                results = await response.json()

            for result in results["result"]:
                if (
                    result["account_address"]
                    == "0xbc56eb15427dc7ec6e46cb42715c8b3f28c57c8d"
                    or result["account_address"]
                    == "0x0000000000000000000000000000000000000000"
                ):
                    continue
                else:
                    raw_data.extend(results["result"])

            page_cursor = (
                results["page"]["next_cursor"]
                if results["page"]["next_cursor"]
                else None
            )
            if not page_cursor:
                break
        print("finished retrieving raw land owner with land ids data")

    print("Cleaning raw land owner with land ids data...")
    clean_data = list()
    owners = []
    for result in raw_data:
        if (
            result["account_address"] == "0xbc56eb15427dc7ec6e46cb42715c8b3f28c57c8d"
            or result["account_address"] == "0x0000000000000000000000000000000000000000"
        ):
            continue
        owners_address = result["account_address"]
        if owners_address not in owners:
            owners.append(owners_address)
        token_id = result["token_id"]
        clean_data.append({"owners_address": owners_address, "token_id": token_id})
    print("Raw land owner with land ids data cleaned")

    print("Finalizing land owner with land ids data...")
    final_data = []
    for owner in owners:
        owned_tokens = []
        for item in clean_data:
            if item["owners_address"] == owner and item["token_id"] not in owned_tokens:
                owned_tokens.append(item["token_id"])
        final_data.append({"owners_address": owner, "owned_tokens": owned_tokens})
    print("Land owner with land ids data finalized")

    return final_data


async def get_land_data() -> List[Dict[str, Any]]:
    print("Retrieving land data...")
    land_data = []
    owner_objs = await get_land_owners_and_ids()
    for owner_obj in owner_objs:
        token_data = []
        owned_tokens = owner_obj["owned_tokens"]
        land_info = await get_land_info_for_ids(owned_tokens)
        token_data.extend(land_info)
        land_data.append(
            {
                "owners_address": owner_obj["owners_address"],
                "land_info": token_data,
                "count": len(token_data),
            }
        )
    print("Land data retrieved")
    # sort land data by count key
    land_data.sort(key=lambda x: x["count"], reverse=True)
    print("Land data retrived")
    return land_data


async def get_lands_for_sale() -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/orders/listings?sell_item_contract_address=0x5C40Eb1Eaad2a96e383E3B0a986A5377fc1eE239&status=ACTIVE"
        ) as response:
            for_sale_land_objs = await response.json()
            return for_sale_land_objs["result"]  # type: ignore[no-any-return]


from typing import Optional

async def get_zkevm_token_data(token_address: str) -> Optional[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        url = f"https://immutable-mainnet.blockscout.com/api/v2/tokens/{token_address}"
        async with session.get(url) as response:
            if response.status == 200:
                token_obj = await response.json()
                return token_obj  # type: ignore[no-any-return]
            else:
                # Log the error and return None or a default dict
                print(
                    f"Error fetching token data for {token_address}: {response.status} {await response.text()}"
                )
                return None


async def get_lands_for_sale_amount() -> Dict[str, Dict[str, Union[str, float]]]:
    print("Fetching lands for sale amount...")
    for_sale_lands_data = await get_lands_for_sale()
    for_sale_lands_data_dict = {}
    for for_sale_land_data in for_sale_lands_data:
        token_id = for_sale_land_data["sell"][0]["token_id"]
        owners_address = for_sale_land_data["account_address"]
        try:
            token_address = for_sale_land_data["buy"][0]["contract_address"]
        except KeyError as e:
            if for_sale_land_data["buy"][0]["type"] == "NATIVE":
                token_address = "0x3a0c2ba54d6cbd3121f01b96dfd20e99d1696c9d"
            else:
                print(f"{for_sale_land_data}")
                raise e

        for_sale_amount_smallest = int(for_sale_land_data["buy"][0]["amount"])
        for fee in for_sale_land_data["fees"]:
            for_sale_amount_smallest += int(fee["amount"])

        token_data = await get_zkevm_token_data(token_address=token_address)
        if token_data is None:
            # Handle missing token data gracefully
            decimals = 18  # default
            token_symbol = "UNKNOWN"
            exchange_rate = 0.0
        else:
            decimals = token_data.get("decimals", 18)
            token_symbol = token_data.get("symbol", "UNKNOWN")
            if token_symbol == "WIMX":
                token_symbol = "IMX"
            exchange_rate = float(token_data.get("exchange_rate", 0.0))

        for_sale_amount = for_sale_amount_smallest / (10 ** int(decimals))
        for_sale_amount_usd = round(exchange_rate * for_sale_amount, 2)

        for_sale_lands_data_dict[token_id] = {
            "owners_address": owners_address,
            "for_sale_token": for_sale_amount,
            "token_symbol": token_symbol,
            "for_sale_usd": for_sale_amount_usd,
        }
    print("Fetched lands for sale amount")
    return for_sale_lands_data_dict


if __name__ == "__main__":
    pass
