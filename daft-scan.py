#!/usr/bin/env python3
"""Daft.ie scanner using the internal API via daftlistings library.
Usage: python daft-scan.py --mode rent --county dublin --max-price 1300 --min-size 30
       python daft-scan.py --listing 6244317
"""

import argparse
import json
import sys
from daftlistings import Daft, Location, SearchType, PropertyType, SortType, Ber

def scan_listings(mode, county, max_price, min_size=None, min_beds=None):
    """Search Daft.ie for listings matching criteria."""
    daft = Daft()

    # Map county string to Location enum
    location_map = {
        "dublin": Location.DUBLIN,
        "cork": Location.CORK,
        "galway": Location.GALWAY,
        "limerick": Location.LIMERICK,
        "waterford": Location.WATERFORD,
        "kildare": Location.KILDARE,
        "wicklow": Location.WICKLOW,
        "meath": Location.MEATH,
    }

    loc = location_map.get(county.lower())
    if not loc:
        print(f"Unknown county: {county}. Available: {', '.join(location_map.keys())}", file=sys.stderr)
        sys.exit(1)

    daft.set_location(loc)

    if mode == "rent":
        daft.set_search_type(SearchType.RESIDENTIAL_RENT)
        daft.set_max_price(max_price)
    else:
        daft.set_search_type(SearchType.RESIDENTIAL_SALE)
        daft.set_max_price(max_price)

    if min_size:
        daft.set_min_floor_size(min_size)

    if min_beds:
        daft.set_min_beds(min_beds)

    daft.set_sort_type(SortType.PUBLISH_DATE_DESC)

    listings = daft.search()

    results = []
    for listing in listings:
        try:
            result = {
                "id": listing.id,
                "title": listing.title,
                "url": listing.daft_link,
                "price": listing.price,
                "monthly_price": listing.monthly_price if hasattr(listing, 'monthly_price') else None,
                "bedrooms": listing.bedrooms,
                "bathrooms": listing.bathrooms,
                "size_meters_squared": listing.size_meters_squared,
                "ber_rating": listing.ber_code,
                "property_type": listing.property_type,
                "address": listing.title,
                "latitude": listing.latitude,
                "longitude": listing.longitude,
                "publish_date": str(listing.publish_date) if listing.publish_date else None,
                "category": listing.category if hasattr(listing, 'category') else None,
            }
            results.append(result)
        except Exception as e:
            print(f"Error processing listing: {e}", file=sys.stderr)
            continue

    return results


def get_listing(listing_id):
    """Fetch a single listing by ID using the API directly."""
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "brand": "daft",
        "platform": "web",
        "Origin": "https://www.daft.ie",
        "Referer": "https://www.daft.ie/",
    }

    url = f"https://gateway.daft.ie/api/v2/listing/{listing_id}"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 410:
        return {"error": "expired", "status": 410, "id": listing_id}
    elif resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "status": resp.status_code, "id": listing_id}

    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Daft.ie scanner")
    parser.add_argument("--mode", choices=["rent", "buy"], default="rent")
    parser.add_argument("--county", default="dublin")
    parser.add_argument("--max-price", type=int, default=1300)
    parser.add_argument("--min-size", type=int, default=None)
    parser.add_argument("--min-beds", type=int, default=None)
    parser.add_argument("--listing", type=int, help="Fetch a single listing by ID")
    parser.add_argument("--limit", type=int, default=50, help="Max results")

    args = parser.parse_args()

    if args.listing:
        result = get_listing(args.listing)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        results = scan_listings(args.mode, args.county, args.max_price, args.min_size, args.min_beds)
        if args.limit:
            results = results[:args.limit]
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
