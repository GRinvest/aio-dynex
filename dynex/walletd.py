from aiohttp import ClientSession
import ujson
from .utils import convert_bytes_to_hex_str, parse_amount


class Walletd:

    def __init__(self,
                 username: str | None = None,
                 password: str | None = None,
                 port=8070,
                 host='127.0.0.1',
                 prefix: str | None = 'json_rpc',
                 session: ClientSession | None = None):
        self.url = 'http://'
        if username:
            self.url += f'{username}:{password}@'
        self.url += f'{host}:{port}'
        if prefix:
            self.url += f'/{prefix}'
        self.id = 0
        self.session = session
        self.headers = {'Content-Type': 'application/json'}

    async def _make_request(self, method, **kwargs):
        self.id += 1
        data = {
            "url": self.url,
            "headers": self.headers,
            "data": ujson.dumps({
                'method': method,
                'params': dict(kwargs),
                'id': self.id,
                'jsonrpc': '2.0',
            })
        }

        async def __response(resp_):
            try:
                json_obj = await resp_.json()
                if json_obj.get('error', None):
                    raise Exception(json_obj.get('error', None))
            except Exception as e:
                print(e)
            else:
                return json_obj

        if self.session is None:
            async with ClientSession() as session:
                async with session.post(**data) as resp:
                    return await __response(resp)
        else:
            async with self.session.post(**data) as resp:
                return await __response(resp)

    async def save(self):
        """
        Save the wallet
        """
        return await self._make_request('save')

    async def reset(self, view_secret_key):
        """
        Re-syncs the wallet
        Note:
            If the view_secret_key parameter is not specified, the reset() method resets the
            wallet and re-syncs it. If the view_secret_key argument is specified, reset()
            method substitutes the existing wallet with a new one with a specified
            view_secret_key and creates an address for it.

        """
        params = {'viewSecretKey': view_secret_key}
        return await self._make_request('reset', **params)

    async def export(self, file_name):
        params = {'fileName': file_name}
        return await self._make_request('export', **params)

    async def create_address(self, spend_secret_key='', spend_public_key='') -> dict:
        """ **Create a new address**
        Args:
            spend_secret_key: str
            spend_public_key: str
        Returns:
            str: the hash of the new address
        """
        params = {
            'spendSecretKey': spend_secret_key,
            'spendPublicKey': spend_public_key
        }
        return await self._make_request('createAddress', **params)

    async def create_address_list(self, spend_secret_keys, scan_heights: int) -> dict:
        params = {
            'spendSecretKeys': spend_secret_keys,
            'scanHeights': scan_heights
        }
        return await self._make_request('createAddressList', **params)

    async def delete_address(self, address):
        """**Delete address from wallet**
        Args:
            address: (str) the address to delete
        Returns:
            bool: True if successful
        """
        params = {'address': address}
        return await self._make_request('deleteAddress', **params)

    async def get_spend_keys(self, address):
        """**Returns spend keys**
        Args:
            address: (str) Valid and existing in this container address
        Returns:
            dict: A dictionary with the secret and public spend keys
        Note:
            {
                'spendPublicKey': '3550a41b004520030941183b7f3e5ec075042cdde492044ea5064e4a1d99a3ba',
                'spendSecretKey': 'f66997b99f9a8444417f09b4bca710e7afe9285d581a5aa641cd4ac0b29f5d00'
            }
        """
        params = {'address': address}
        return await self._make_request('getSpendKeys', **params)

    async def get_balance(self, address=''):
        """
        Returns the balance of an address
        Note:
            Amount needs to be divided by 1000000000 to get decimal places.
            If balance returned is 10000000000 it means 10.00 DNX
        Args:
            address (str): (optional) The address for which to return
                the balance. Must exist in this wallet.
        Returns:
            dict: available balance (int) and locked amount (int)::
            {
                'availableBalance': 10000000000,
                'lockedAmount': 0
            }
        """
        params = {'address': address}
        return await self._make_request('getBalance', **params)

    async def get_status(self):
        return await self._make_request('getStatus')

    async def get_addresses(self):
        return await self._make_request('getAddresses')

    async def get_view_key(self):
        """
        Returns the view key
        Returns:
            str: Private view key
        """
        return await self._make_request('getViewKey')

    async def get_unconfirmed_transaction_hashes(self, addresses=[]):
        """
        Returns the current unconfirmed transaction pool for addresses
        Args:
            addresses (list): (optional) List of addresses.
                If not set, all addresses of this wallet will be used.
        Returns:
            list: Hashes of unconfirmed transactions
        """
        params = {'addresses': addresses}
        return await self._make_request('getUnconfirmedTransactionHashes', **params)

    async def get_block_hashes(self, first_block_index, block_count):
        params = {'firstBlockIndex': first_block_index,
                  'blockCount': block_count}
        return await self._make_request('getBlockHashes', **params)

    async def get_transaction(self, transaction_hash):
        """
        Returns information about a particular transaction
        Args:
            transaction_hash (str): Hash of the requested transaction
        Returns:
            dict: information about the transaction::
            {'amount': -110,
             'blockIndex': 274123,
             'extra': '013ffd7e8481121a427a01e034cc9f4604d7b474412186ddd9fc56361dc0eafb72',
             'fee': 10,
             'isBase': False,
             'paymentId': '',
             'state': 0,
             'timestamp': 1521641265,
             'transactionHash': 'dc1221181e5745b9016fed2970bf002d14fe2ad8c90d7a55456d0eb459c7c2b8',
             'transfers': [{'address': 'Xwmy9ChFUsefEpU1Dv8we7N1BhG9iHsrX7mnsRw7abHc7F8dyNxdvYxe1xS1fEqgWFarx9Dcz2MMsDT3YJMpJ3Qe1zTdQ2k8k',
                            'amount': 100,
                            'type': 0},
                           {'address': 'XwnKeHS5Ah718BevbZGE12R5ZYk4pGnwNZBKV2GcVwDzhCbnErdF7Kee1xS1fEqgWFarx9Dcz2MMsDT3YJMpJ3Qe1zTbMe634',
                            'amount': 790,
                            'type': 2},
                           {'address': 'XwnGYVuu1j3duMe9Zoz1ttDHRTh66vXZV6XKu1PU2b1K7Ye5yUcKKRAe1xS1fEqgWFarx9Dcz2MMsDT3YJMpJ3Qe1zTZZ3yWx',
                            'amount': -900,
                            'type': 0}],
             'unlockTime': 0}
        """
        params = {'transactionHash': transaction_hash}
        return await self._make_request('getTransaction', **params)

    async def get_transactions(self, addresses, block_hash, block_count,
                               payment_id):
        params = {'addresses': addresses,
                  'blockHash': block_hash,
                  'blockCount': block_count,
                  'paymentId': payment_id}
        return await self._make_request('getTransactions', **params)

    async def get_transaction_hashes(self, addresses, block_hash, block_count,
                                     payment_id):
        params = {'addresses': addresses,
                  'blockHash': block_hash,
                  'blockCount': block_count,
                  'paymentId': payment_id}
        return await self._make_request('getTransactionHashes', **params)

    async def send_transaction(self,
                               transfers: list[dict],
                               payment_id: str | None = None,
                               address_from: str | None = None,
                               anonymity=3,
                               fee=parse_amount(0.005),
                               change_address: str | None = None,
                               extra: bytes | None = None,
                               unlock_time=0) -> dict:
        """
        Send a transaction to one or multiple addresses.
        Note:
            The amount/fee need to be multiplied by 100 to get DNX amount.
            If you want to transfer 100000000000 DNX with a fee of 0.01 DNX you should
            set transfer amount to 1000000 and fee to 0.01
        Params:
            anonymity: mixin amount
            transfers: address where to send the funds to. (address, amount)
            fee: transaction fee (default 1000000 (0.01 DNX))
            source_addresses: addresses from which to take the funds from.
            change_address: address where to send the change to.
            extra (bytes): extra data to include
            payment_id: can be given to receiver to identify transaction
            unlock_time (int)
        Example::
            wallet.send_transaction(
                anonymity=3,
                transfers=[
                    {'address': 'TRTL...',
                     'amount': 500}],
                fee=10
            )
            {'transactionHash': '1b87a........'}
        """
        params = {'transfers': transfers,
                  'fee': fee,
                  'anonymity': anonymity,
                  'unlockTime': unlock_time}
        if address_from:
            params['sourceAddresses'] = address_from
        if change_address:
            params['changeAddress'] = change_address

        # payment_id and extra cannot be present at the same time
        # either none of them is included, or one of them
        if payment_id and extra:
            raise ValueError('payment_id and extra cannot be set together')
        elif payment_id:
            params['paymentId'] = payment_id
        elif extra:
            params['extra'] = convert_bytes_to_hex_str(extra)
        return await self._make_request('sendTransaction', **params)

    async def get_delayed_transaction_hashes(self):
        """
        Returns a list of delayed transaction hashes
        """
        return await self._make_request('getDelayedTransactionHashes')

    async def create_delayed_transaction(self, transfers, anonymity=3, fee=10,
                                         addresses='', change_address='',
                                         extra='', payment_id='', unlock_time=0):
        params = {'addresses': addresses,
                  'transfers': transfers,
                  'changeAddress': change_address,
                  'fee': fee,
                  'anonymity': anonymity,
                  'unlockTime': unlock_time}

        # payment_id and extra cannot be present at the same time
        # either none of them is included, or one of them
        if payment_id and extra:
            raise ValueError('payment_id and extra cannot be set together')
        elif payment_id:
            params['paymentId'] = payment_id
        elif extra:
            params['extra'] = convert_bytes_to_hex_str(extra)

        return await self._make_request('createDelayedTransaction', **params)

    async def send_delayed_transaction(self, transaction_hash):
        """
        Send a delayed transaction
        Example::
            >>> wallet.send_delayed_transaction('8dea3...')
        Raises:
            ValueError: {
                'code': -32000,
                'data': {'application_code': 15},
                'message': 'Transaction transfer impossible'
            }
        """
        params = {'transactionHash': transaction_hash}
        return await self._make_request('sendDelayedTransaction', **params)

    async def delete_delayed_transaction(self, transaction_hash):
        """
        Delete a delayed transaction
        Example:
            >>> wallet.delete_delayed_transaction('8dea3....')
        """
        params = {'transactionHash': transaction_hash}
        return await self._make_request('deleteDelayedTransaction', **params)

    async def send_fusion_transaction(self, threshold, anonymity, addresses,
                                      destination_address):
        """
        Send a fusion transaction, by taking funds from selected addresses and
        transferring them to the destination address.
        Returns:
            str: hash of the sent transaction
        """
        params = {'threshold': threshold,
                  'anonymity': anonymity,
                  'addresses': addresses,
                  'destinationAddress': destination_address}
        return await self._make_request('sendFusionTransaction', **params)

    async def estimate_fusion(self, threshold, addresses=[]):
        """
        Counts the number of unspent outputs of the specified addresses and
        returns how many of those outputs can be optimized.
        """
        params = {'threshold': threshold,
                  'addresses': addresses}
        return await self._make_request('estimateFusion', **params)

    async def get_mnemonic_seed(self, address):
        """
        Returns the mnemonic seed for the given address
        Args:
            address (str): Valid and existing in this container address
        Returns:
            str: mnemonic seed
        """
        params = {'address': address}
        return await self._make_request('getMnemonicSeed', **params)

    async def create_integrated_address(self, address, payment_id):
        """
        Creates a unique 236 char long address which corresponds to given
        address and paymentID
        Args:
            address (str): valid DNX address
            payment_id (str): valid payment id
        Returns:
            str: integrated address
        """
        params = {'address': address, 'paymentId': payment_id}
        return await self._make_request('createIntegratedAddress', **params)

    async def validate_address(self, address) -> dict:
        """
        Validate Address

        :param address:
        :type address: str
        :return: {'address': '',
            'isvalid': True,
            'spendPublicKey': '',
            'viewPublicKey': ''}
        :rtype:
        """

        return await self._make_request('validateAddress', address=address)
