import asyncio
from typing import Any, cast

from utils.http import fetch_json

_COLLECTION_ADDRESS = "0x5c40eb1eaad2a96e383e3b0a986a5377fc1ee239"
_BURN_ADDRESSES = frozenset(
    {
        "0xbc56eb15427dc7ec6e46cb42715c8b3f28c57c8d",
        "0x0000000000000000000000000000000000000000",
    }
)


async def _fetch_json_404_ok(url: str, client: Any = None) -> Any | None:
    """Fetch JSON where a 404 is a valid 'missing' answer, not an error."""
    return await fetch_json(url, client=client, no_retry=frozenset({404}))


async def get_land_info_for_ids(token_ids: list[Any]) -> list[dict[str, Any]]:
    token_ids_list = (
        [token_ids[i : i + 30] for i in range(0, len(token_ids), 30)]
        if len(token_ids) > 30
        else [token_ids]
    )

    land_info: list[dict[str, Any]] = []
    for chunk in token_ids_list:
        query = "&".join(
            [
                ("token_id" if i == 0 else "&token_id") + f"={tid}"
                for i, tid in enumerate(chunk)
            ]
        )
        url = (
            f"https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/"
            f"collections/{_COLLECTION_ADDRESS}/nfts?{query}&page_size=200"
        )
        nft_objs = await _fetch_json_404_ok(url)

        if nft_objs and "result" in nft_objs:
            for nft_obj in nft_objs["result"]:
                # Build a dict keyed by trait_type for robust attribute lookup
                traits = {
                    attr["trait_type"]: attr["value"]
                    for attr in nft_obj.get("attributes", [])
                    if "trait_type" in attr
                }
                biome = traits.get("Biome", "").lower() or None
                token_id = nft_obj["token_id"]
                entity_type = traits.get("Entity", "").lower() or None
                id_ = traits.get("Id")
                rarity = traits.get("Scarcity", "").lower() or None
                size = traits.get("Size")
                img_url = nft_obj["image"]
                land_info.append(
                    {
                        "id": id_,
                        "token_id": token_id,
                        "biome": biome,
                        "land_type": entity_type,
                        "rarity": rarity,
                        "size": size,
                        "img_url": img_url,
                    }
                )
        # Add a small delay between requests to be nice to the API
        await asyncio.sleep(0.2)
    return land_info


async def get_land_owners_and_ids() -> list[dict[str, Any]]:
    print("Retrieving raw land owner with land ids data...")
    base_url = (
        f"https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/"
        f"collections/{_COLLECTION_ADDRESS}/owners"
    )
    page_cursor = None
    raw_data: list[dict[str, Any]] = []
    while True:
        url = (
            f"{base_url}?page_cursor={page_cursor}&page_size=200"
            if page_cursor
            else f"{base_url}?page_size=200"
        )
        results = await fetch_json(url)
        if not results or "result" not in results:
            break

        for result in results["result"]:
            if result["account_address"] in _BURN_ADDRESSES:
                continue
            raw_data.append(result)

        page_cursor = (
            results["page"]["next_cursor"]
            if results.get("page") and results["page"].get("next_cursor")
            else None
        )
        if not page_cursor:
            break

        # Pacing: wait 0.5s between pages to prevent rate limits
        await asyncio.sleep(0.5)
    print("Finished retrieving raw land owner with land ids data")

    print("Cleaning raw land owner with land ids data...")
    owners: list[str] = []
    clean_data: list[dict[str, Any]] = []
    for result in raw_data:
        owners_address = result["account_address"]
        if owners_address not in owners:
            owners.append(owners_address)
        clean_data.append(
            {"owners_address": owners_address, "token_id": result["token_id"]}
        )
    print("Raw land owner with land ids data cleaned")

    print("Finalizing land owner with land ids data...")
    final_data: list[dict[str, Any]] = []
    for owner in owners:
        owned_tokens: list[Any] = []
        for item in clean_data:
            if item["owners_address"] == owner and item["token_id"] not in owned_tokens:
                owned_tokens.append(item["token_id"])
        final_data.append({"owners_address": owner, "owned_tokens": owned_tokens})
    print("Land owner with land ids data finalized")

    return final_data


async def get_land_data() -> list[dict[str, Any]]:
    print("Retrieving land data...")
    land_data: list[dict[str, Any]] = []
    owner_objs = await get_land_owners_and_ids()
    for owner_obj in owner_objs:
        land_info = await get_land_info_for_ids(owner_obj["owned_tokens"])
        land_data.append(
            {
                "owners_address": owner_obj["owners_address"],
                "land_info": land_info,
                "count": len(land_info),
            }
        )
    print("Land data retrieved")
    # sort land data by count key
    land_data.sort(key=lambda x: x["count"], reverse=True)
    return land_data


async def get_lands_for_sale() -> list[dict[str, Any]]:
    url = (
        "https://api.immutable.com/v1/chains/imtbl-zkevm-mainnet/orders/listings"
        "?sell_item_contract_address=0x5C40Eb1Eaad2a96e383E3B0a986A5377fc1eE239"
        "&status=ACTIVE"
    )
    for_sale_land_objs = await _fetch_json_404_ok(url)
    if for_sale_land_objs and "result" in for_sale_land_objs:
        return cast(list[dict[str, Any]], for_sale_land_objs["result"])
    return []


async def get_zkevm_token_data(token_address: str) -> dict[str, Any] | None:
    url = f"https://explorer.immutable.com/api/v2/tokens/{token_address}"
    return cast("dict[str, Any] | None", await _fetch_json_404_ok(url))


async def get_lands_for_sale_amount() -> dict[str, dict[str, str | float]]:
    print("Fetching lands for sale amount...")
    for_sale_lands_data = await get_lands_for_sale()
    for_sale_lands_data_dict: dict[str, dict[str, str | float]] = {}

    # Token cache to prevent repeated explorer API queries
    token_cache: dict[str, Any] = {}

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

        # Retrieve from cache or request API
        if token_address in token_cache:
            token_data = token_cache[token_address]
        else:
            token_data = await get_zkevm_token_data(token_address=token_address)
            token_cache[token_address] = token_data

        for_sale_amount_smallest = int(for_sale_land_data["buy"][0]["amount"])
        for fee in for_sale_land_data["fees"]:
            for_sale_amount_smallest += int(fee["amount"])

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
