"""CoinGecko API tier example demonstrating different subscription tiers.

This example shows how to use different CoinGecko API tiers (Free, Hobby, Pro, Pro+, Enterprise)
to access enhanced features and higher rate limits.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coingecko_client import CoinGeckoClient, CoinGeckoConfig, CoinGeckoTier
import asyncio


async def demo_free_tier():
    """Demonstrate free tier usage."""
    print("=" * 70)
    print("🎯 Demo 1: Free Tier (No API Key Required)")
    print("-" * 70)
    
    config = CoinGeckoConfig(
        tier=CoinGeckoTier.FREE,
        api_key=None,
        enable_cache=True,
    )
    
    async with CoinGeckoClient(config) as client:
        print(f"\n📊 Tier Info:")
        tier_info = client.get_tier_info()
        print(f"   Tier: {tier_info['tier']}")
        print(f"   Rate Limit: {tier_info['rate_limit_calls']} calls / {tier_info['rate_limit_period']}s")
        print(f"   API Key: {'Configured' if tier_info['api_key_configured'] else 'Not configured'}")
        
        # Get Bitcoin price
        print(f"\n💰 Getting BTC Price...")
        price_data = await client.get_price("bitcoin")
        btc_price = price_data.get('bitcoin', {}).get('usd', 0)
        print(f"   BTC Price: ${btc_price:.2f}")
        
        # Get top coins
        print(f"\n📈 Getting Top 10 Coins...")
        top_coins = await client.get_top_coins(per_page=10)
        print(f"   Retrieved {len(top_coins)} coins")
        for coin in top_coins[:5]:
            print(f"   {coin['symbol']}: ${coin['current_price']:.2f}")
        
        # Call stats
        stats = client.get_call_stats()
        print(f"\n📊 Call Stats: {stats['total_calls']} API calls made")


async def demo_pro_tier():
    """Demonstrate Pro tier usage (requires API key)."""
    print("\n" + "=" * 70)
    print("🎯 Demo 2: Pro Tier (API Key Required)")
    print("-" * 70)
    
    print("\n⚠️  To use Pro tier, set your API key:")
    print("   config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key='YOUR_API_KEY')")
    
    config = CoinGeckoConfig(
        tier=CoinGeckoTier.PRO,
        api_key=None,  # Set your API key here
        enable_cache=True,
    )
    
    async with CoinGeckoClient(config) as client:
        print(f"\n📊 Tier Info:")
        tier_info = client.get_tier_info()
        print(f"   Tier: {tier_info['tier']}")
        print(f"   Rate Limit: {tier_info['rate_limit_calls']} calls / {tier_info['rate_limit_period']}s")
        print(f"   Base URL: {tier_info['base_url']}")
        
        print("\n📋 Pro Tier Benefits:")
        print("   ✓ 500 calls/minute (vs 50 for free)")
        print("   ✓ Access to Pro API endpoints")
        print("   ✓ Advanced market data")
        print("   ✓ Historical data with higher resolution")
        print("   ✓ No rate limiting issues")


async def demo_enterprise_tier():
    """Demonstrate Enterprise tier usage."""
    print("\n" + "=" * 70)
    print("🎯 Demo 3: Enterprise Tier (Custom Limits)")
    print("-" * 70)
    
    config = CoinGeckoConfig(
        tier=CoinGeckoTier.ENTERPRISE,
        api_key=None,  # Set your Enterprise API key here
        enable_cache=True,
    )
    
    async with CoinGeckoClient(config) as client:
        print(f"\n📊 Tier Info:")
        tier_info = client.get_tier_info()
        print(f"   Tier: {tier_info['tier']}")
        print(f"   Rate Limit: {tier_info['rate_limit_calls']} calls / {tier_info['rate_limit_period']}s")
        
        print("\n📋 Enterprise Tier Benefits:")
        print("   ✓ 2000+ calls/minute")
        print("   ✓ Dedicated support")
        print("   ✓ Custom rate limits")
        print("   ✓ All API features")
        print("   ✓ Priority access")


async def demo_multiple_coins():
    """Demonstrate getting multiple coins efficiently."""
    print("\n" + "=" * 70)
    print("🎯 Demo 4: Multiple Coins (Efficient Batch Request)")
    print("-" * 70)
    
    config = CoinGeckoConfig(tier=CoinGeckoTier.FREE)
    
    async with CoinGeckoClient(config) as client:
        # Get multiple coins in one request
        coin_ids = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana"]
        print(f"\n💰 Getting prices for {len(coin_ids)} coins...")
        
        prices = await client.get_prices(coin_ids)
        
        print("\n📊 Current Prices:")
        for coin_id, data in prices.items():
            price = data.get('usd', 0)
            print(f"   {coin_id.capitalize()}: ${price:.2f}")
        
        # Get market data
        print(f"\n📈 Getting BTC market data (7 days)...")
        market_data = await client.get_coin_market_data("bitcoin", days=7)
        print(f"   Retrieved {len(market_data['prices'])} price points")


async def demo_global_data():
    """Demonstrate global market data."""
    print("\n" + "=" * 70)
    print("🎯 Demo 5: Global Market Data")
    print("-" * 70)
    
    config = CoinGeckoConfig(tier=CoinGeckoTier.FREE)
    
    async with CoinGeckoClient(config) as client:
        print(f"\n🌍 Getting Global Market Data...")
        global_data = await client.get_global_data()
        
        print(f"\n📊 Global Market Stats:")
        print(f"   Total Market Cap: ${global_data['data']['total_market_cap']['usd']:.0f}")
        print(f"   24h Volume: ${global_data['data']['total_volume']['usd']:.0f}")
        print(f"   BTC Dominance: {global_data['data']['market_cap_percentage']['btc']:.2f}%")
        print(f"   Active Cryptocurrencies: {global_data['data']['active_cryptocurrencies']}")


async def main():
    """Run all demos."""
    print("\n" + "🎬" * 35)
    print("\n")
    
    await demo_free_tier()
    await demo_pro_tier()
    await demo_enterprise_tier()
    await demo_multiple_coins()
    await demo_global_data()
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)
    
    print("\n📚 CoinGecko Tier Comparison:")
    print("   Free:     50 calls/minute, basic data")
    print("   Hobby:    100 calls/minute, more data")
    print("   Pro:      500 calls/minute, advanced features")
    print("   Pro+:     1000 calls/minute, full features")
    print("   Enterprise: 2000+ calls/minute, custom limits")
    
    print("\n🔑 Get Your API Key:")
    print("   https://www.coingecko.com/en/api/pricing")
    
    print("\n⚙️  Configuration:")
    print("   # In config.py or your code:")
    print("   coingecko = CoinGeckoConfig(")
    print("       tier=CoinGeckoTier.PRO,")
    print("       api_key='your_api_key_here'")
    print("   )")
    
    print("\n📖 Learn more:")
    print("   - Read COINGECKO_TIER.md for detailed documentation")
    print("   - Check examples/ directory for more examples")


if __name__ == "__main__":
    asyncio.run(main())
