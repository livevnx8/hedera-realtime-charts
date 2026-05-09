# CoinGecko API Tier Support

The hedera-realtime-charts library supports multiple CoinGecko API tiers, allowing you to leverage your subscription for enhanced features and higher rate limits.

## Supported Tiers

### Free Tier
- **Rate Limit**: 50 calls/minute
- **Features**: Basic price data, market data, global stats
- **API Key**: Not required
- **Best For**: Testing, development, personal projects

### Hobby Tier
- **Rate Limit**: 100 calls/minute
- **Features**: More data points, historical data
- **API Key**: Required
- **Best For**: Small projects, hobbyist trading
- **Pricing**: ~$11/month

### Pro Tier
- **Rate Limit**: 500 calls/minute
- **Features**: Advanced market data, historical charts, technical indicators
- **API Key**: Required
- **Best For**: Professional applications, production use
- **Pricing**: ~$79/month

### Pro+ Tier
- **Rate Limit**: 1,000 calls/minute
- **Features**: Full API access, priority support, advanced analytics
- **API Key**: Required
- **Best For**: Enterprise applications, high-frequency data
- **Pricing**: ~$299/month

### Enterprise Tier
- **Rate Limit**: 2,000+ calls/minute (custom)
- **Features**: Custom limits, dedicated support, SLA
- **API Key**: Required
- **Best For**: Large-scale enterprise deployments
- **Pricing**: Custom

## Configuration

### Using config.py

```python
from config import CoinGeckoConfig, CoinGeckoTier, get_config

# Get global config
config = get_config()

# Update CoinGecko settings
config.coingecko.api_key = "your_api_key_here"
config.coingecko.tier = CoinGeckoTier.PRO
```

### Using Environment Variables

```python
import os
from config import CoinGeckoConfig, CoinGeckoTier

config = CoinGeckoConfig(
    tier=CoinGeckoTier.PRO,
    api_key=os.getenv("COINGECKO_API_KEY"),
)
```

### Direct Configuration

```python
from coingecko_client import CoinGeckoClient, CoinGeckoConfig, CoinGeckoTier

config = CoinGeckoConfig(
    tier=CoinGeckoTier.PRO,
    api_key="your_api_key_here",
    enable_cache=True,
    cache_ttl=60,
)

client = CoinGeckoClient(config)
```

## Usage Examples

### Basic Price Query

```python
from coingecko_client import CoinGeckoClient, CoinGeckoConfig, CoinGeckoTier
import asyncio

async def get_btc_price():
    config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key="your_key")
    async with CoinGeckoClient(config) as client:
        price_data = await client.get_price("bitcoin")
        print(f"BTC Price: ${price_data['bitcoin']['usdt']:.2f}")

asyncio.run(get_btc_price())
```

### Multiple Coins

```python
async def get_multiple_prices():
    config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key="your_key")
    async with CoinGeckoClient(config) as client:
        coin_ids = ["bitcoin", "ethereum", "binancecoin"]
        prices = await client.get_prices(coin_ids)
        for coin_id, data in prices.items():
            print(f"{coin_id}: ${data['usdt']:.2f}")

asyncio.run(get_multiple_prices())
```

### Market Data

```python
async def get_market_data():
    config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key="your_key")
    async with CoinGeckoClient(config) as client:
        market_data = await client.get_coin_market_data("bitcoin", days=7)
        print(f"Retrieved {len(market_data['prices'])} price points")

asyncio.run(get_market_data())
```

### Top Coins

```python
async def get_top_coins():
    config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key="your_key")
    async with CoinGeckoClient(config) as client:
        top_coins = await client.get_top_coins(per_page=50)
        for coin in top_coins[:10]:
            print(f"{coin['symbol']}: ${coin['current_price']:.2f}")

asyncio.run(get_top_coins())
```

## Tier Comparison

| Feature | Free | Hobby | Pro | Pro+ | Enterprise |
|---------|------|-------|-----|------|------------|
| Rate Limit | 50/min | 100/min | 500/min | 1,000/min | 2,000+/min |
| API Key | Not required | Required | Required | Required | Required |
| Basic Price Data | ✓ | ✓ | ✓ | ✓ | ✓ |
| Market Data | ✓ | ✓ | ✓ | ✓ | ✓ |
| Historical Data | Limited | Extended | Full | Full | Full |
| Technical Indicators | ✗ | Limited | ✓ | ✓ | ✓ |
| Advanced Analytics | ✗ | ✗ | ✓ | ✓ | ✓ |
| Priority Support | ✗ | ✗ | ✗ | ✓ | ✓ |
| Custom Rate Limits | ✗ | ✗ | ✗ | ✗ | ✓ |

## Rate Limiting

The library automatically handles rate limiting based on your tier:

```python
# Automatic rate limiting
config = CoinGeckoConfig(tier=CoinGeckoTier.PRO)
async with CoinGeckoClient(config) as client:
    # Will automatically respect 500 calls/minute limit
    for i in range(1000):
        price = await client.get_price("bitcoin")
        # Automatically sleeps if rate limit approached
```

### Call Statistics

```python
async def check_stats():
    config = CoinGeckoConfig(tier=CoinGeckoTier.PRO, api_key="your_key")
    async with CoinGeckoClient(config) as client:
        # Make some requests
        await client.get_price("bitcoin")
        await client.get_price("ethereum")
        
        # Check stats
        stats = client.get_call_stats()
        print(f"Total calls: {stats['total_calls']}")
        print(f"Cache size: {stats['cache_size']}")

asyncio.run(check_stats())
```

## Caching

The library includes built-in caching to reduce API calls:

```python
# Enable caching (default: enabled)
config = CoinGeckoConfig(
    tier=CoinGeckoTier.PRO,
    api_key="your_key",
    enable_cache=True,
    cache_ttl=60,  # Cache for 60 seconds
)
```

### Cache Benefits
- Reduces API calls
- Improves response time
- Respects rate limits
- Saves on API quota

## Getting an API Key

1. Visit https://www.coingecko.com/en/api/pricing
2. Choose your tier
3. Sign up and get your API key
4. Configure in your application

```python
# Set your API key
config.coingecko.api_key = "your_api_key_here"
```

## Best Practices

### 1. Use Appropriate Tier
- **Free**: For testing and development
- **Hobby**: For small personal projects
- **Pro**: For production applications
- **Pro+**: For high-frequency data needs
- **Enterprise**: For large-scale deployments

### 2. Enable Caching
```python
config = CoinGeckoConfig(enable_cache=True, cache_ttl=60)
```

### 3. Batch Requests
```python
# Instead of multiple single requests
# Do this:
prices = await client.get_prices(["btc", "eth", "bnb"])

# Not this:
btc = await client.get_price("bitcoin")
eth = await client.get_price("ethereum")
bnb = await client.get_price("binancecoin")
```

### 4. Monitor Usage
```python
stats = client.get_call_stats()
print(f"Calls made: {stats['total_calls']}")
```

### 5. Handle Rate Limits
The library handles rate limits automatically, but you can monitor:

```python
tier_info = client.get_tier_info()
print(f"Rate limit: {tier_info['rate_limit_calls']}/{tier_info['rate_limit_period']}s")
```

## Integration with CryptoCharts

```python
from src import CryptoCharts
from config import CoinGeckoConfig, CoinGeckoTier

# Configure CoinGecko tier
config = CoinGeckoConfig(
    tier=CoinGeckoTier.PRO,
    api_key="your_api_key_here"
)

# Use with CryptoCharts (future integration)
charts = CryptoCharts()
# charts.set_coingecko_config(config)
```

## Troubleshooting

### Rate Limit Errors
If you see rate limit errors:
- Check your tier configuration
- Enable caching
- Reduce request frequency
- Upgrade your tier if needed

### API Key Errors
If you see authentication errors:
- Verify your API key is correct
- Ensure your tier matches your subscription
- Check that your subscription is active

### Missing Features
If features are missing:
- Verify your tier supports the feature
- Check CoinGecko documentation
- Consider upgrading your tier

## Examples

See `examples/coingecko_tier_example.py` for complete examples of all tiers and features.

## Support

- CoinGecko API Docs: https://www.coingecko.com/en/api
- CoinGecko Support: support@coingecko.com
- GitHub Issues: https://github.com/livevnx8/hedera-realtime-charts/issues
