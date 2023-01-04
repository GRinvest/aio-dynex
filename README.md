# aio-dynex
# Async library for connecting to the Dynex JSON-RPC API.

[![Python 3.7](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Aiohttp: 3.8.1](https://img.shields.io/badge/aiohttp-3.8.1-blue.svg)](https://github.com/aio-libs/aiohttp)
[![Loguru: 0.5.3](https://img.shields.io/badge/loguru-0.5.3-blue.svg)](https://github.com/Delgan/loguru)
[![Ujson: 0.5.3](https://img.shields.io/badge/ujson-5.1.0-blue.svg)](https://github.com/ultrajson/ultrajson)
[![Docstrings: Google](https://img.shields.io/badge/Docstrings-Google-black.svg)](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

It integrates with `Walletd` and works with Dynex 2.2.2.

## Installation

```bash
git clone https://github.com/GRinvest/aio-dynex.git
cd aio-dynex
pipenv install
```

## Getting started

### WALLETD REST API

Usage examples:
```python
import asyncio
from dynex.walletd import Walletd 

async def main():
    wallet = Walletd(user='<username>', password='<your password>')
    # Get addresses information
    res = await wallet.get_addresses()
    print(res)
    """
    {
        'id': 1,
        'jsonrpc': '2.0',
        'result': {
        'addresses': [
            'XwniB1VP5ts......',
            'XwnqcLpTDZY.......',
            ]
        }
    }
    """
    
    # Get balance info
    
    res = await wallet.get_balance()
    print(res)
    # {'id': 0, 'jsonrpc': '2.0', 'result': {'availableBalance': 50, 'lockedAmount': 0}}

    # Send transaction
    recipients = [{'address': 'XwniB1VP5ts......', 'amount': 50000000000}]
    res = await wallet.send_transaction(transfers=recipients)
    print(res)
    
    # {'id': 0, 'jsonrpc': '2.0', 'result': {'transactionHash': 'ae57e...'}}

asyncio.run(main())

```
