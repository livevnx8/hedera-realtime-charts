# Data Disclaimer

## Important Notice

This infrastructure is designed for **developer tooling and research purposes only**. It is **NOT financial advice** and should **NOT be used for trading decisions**.

## Data Sources

### External APIs
- **Binance**: Public WebSocket API for real-time price data
- **CoinGecko**: Public REST API for market data
- **Kraken**: Public WebSocket API for price feeds

### Data Limitations
- **No guarantees** on data accuracy, completeness, or timeliness
- **Rate limits** may apply to public APIs
- **Latency varies** based on network conditions
- **No SLA** from external data providers
- **No responsibility** for data errors or omissions

## Use Cases

### Intended Use
- **Research**: Studying market patterns and correlations
- **Monitoring**: Real-time price tracking and visualization
- **Development**: Building and testing trading algorithms
- **Education**: Learning about real-time data infrastructure
- **Integration**: Providing data for custom applications

### NOT Intended For
- **Trading**: Making buy/sell decisions
- **Investment advice**: Recommending financial actions
- **Production trading**: High-frequency trading without additional validation
- **Risk management**: Sole source of risk calculations

## Hedera-Specific Data

### HBAR Metrics
- HBAR on-chain metrics are sourced from the **Hedera Mirror Node**
- Mirror Node data is **public and unauthenticated**
- **No guarantees** on data accuracy or completeness
- **Rate limits** may apply

### Integration with hedera-ml-pipeline
- Uses existing hedera-ml-pipeline for HBAR metrics
- Maintains the same public boundary
- **No private keys** or internal infrastructure exposed

## Professional Use

If you intend to use this infrastructure for professional or commercial purposes:

1. **Validate data** against multiple sources
2. **Implement proper error handling** and fallback mechanisms
3. **Add rate limiting** to avoid API bans
4. **Comply with terms of service** for all data sources
5. **Obtain proper licenses** if required for commercial use
6. **Implement your own risk controls** and validation
7. **Consider paid data feeds** for production use

## No Warranty

This software is provided **"AS IS"**, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

## Liability

In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## Data Attribution

When using data from external sources, please respect their terms of service and attribution requirements:

- **Binance**: Public data, subject to Binance terms of service
- **CoinGecko**: Public data, subject to CoinGecko terms of service
- **Kraken**: Public data, subject to Kraken terms of service
- **Hedera**: Public Mirror Node data, subject to Hedera terms of service

## Compliance

Users are responsible for ensuring their use of this infrastructure complies with:
- Applicable laws and regulations
- Terms of service of all data providers
- Securities and trading regulations in their jurisdiction
- Data privacy and protection laws

## Questions

If you have questions about appropriate use cases or data limitations, please:
- Review the documentation
- Consult with legal counsel for commercial use
- Contact data providers directly for licensing options
