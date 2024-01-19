import hmac
import json
import hashlib
import logging
import urllib.error
import urllib.parse
import urllib.request

# Set the logger for the current module, more info here https://docs.python.org/3/library/logging.html#logger-objects
logger: logging = logging.getLogger(name=__name__)


class CryptoPayments:
    """A class on working with crypto-payments."""

    __slots__: tuple[str] = ("publicKey", "privateKey", "ipn_url", "format", "version", "url")

    def __init__(self, publicKey: str, privateKey: str, ipn_url: str) -> None:
        """The magic method of data initialization."""

        self.publicKey = publicKey
        self.privateKey = privateKey
        self.ipn_url = ipn_url
        self.format = "json"
        self.version = 1
        self.url = "https://www.coinpayments.net/api.php"

    def createHmac(self, **params) -> tuple:
        """Creating Hmac using urllib for parsing and decoding."""

        encoded = urllib.parse.urlencode(params).encode("utf-8")

        return encoded, hmac.new(bytearray(self.privateKey, "utf-8"), encoded, hashlib.sha512).hexdigest()


    def Request(self, request_method: str, **params: dict) -> dict:
        """Function for creating a request by the specified method and parameters."""

        encoded, sig = self.createHmac(**params)
        headers: dict = {"hmac": sig}

        if request_method == "get":
            req = urllib.request.Request(url=self.url, headers=headers)

        elif request_method == "post":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            req = urllib.request.Request(url=self.url, data=encoded, headers=headers)

        try:
            response = urllib.request.urlopen(url=req)

            _response_body_decoded = json.loads(s=response.read())

        except urllib.error.HTTPError as error:
            logger.warning("Transaction parsing problem: " + str(error))

            _response_body_decoded = error.read()

        return _response_body_decoded

    def getTransactions(self, limit: int = 10) -> Request:
        """Receive transactions according to the specified parameters."""

        params: dict = {
            "cmd": "get_tx_ids",
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
            "limit": limit,
        }

        return self.Request(request_method="post", **params)

    def get_tx_id(self, limit: int = 10) -> Request:
        """Receive transaction id according to the specified parameters."""

        params: dict = {
            "cmd": "get_tx_ids",
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
            "limit": limit,
        }

        return self.Request(request_method="post", **params)

    def getTxid(self, txid, limit: int = 10):
        """Receive transaction id according to the specified parameters."""

        params: dict = {
            "cmd": "get_tx_info",
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
            "limit": limit,
            "txid": txid,
        }

        return self.Request(request_method="post", **params)


    def getAddress_Balance(self, limit: int = 10):
        """Receive address balance by the specified parameters."""

        params: dict = {
            "cmd": "balances",
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
            "limit": limit,
        }

        return self.Request(request_method="post", **params)

    def create_transaction(
        self, amount: int or str, currency1: str, currency2: str, buyer_email: str, item_name: str,success_url: str
    ):
        """Creating a transaction using parameters."""

        params = {
            "cmd": "create_transaction",
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
            "amount": amount,
            "currency1": currency1,
            "currency2": currency2,
            "buyer_email": buyer_email,
            "item_name": item_name,
            "success_url": success_url,
        }

        return self.Request(request_method="post", **params)

    def getMultiplePaymentInfo(self, txids: str) -> Request:
        """Get information for multiple transactions."""


        params: dict = {
            "cmd": "get_tx_info_multi",
            "txid": txids,
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,
        }

        return self.Request(request_method="post", **params)

    def getPaymentInfo(self, txid: str, full: int = 0) -> Request:
        """Get information for a single transaction."""

        params: dict = {
            "cmd": "get_tx_info",
            "txid": txid,
            "full": 1,
            "key": self.publicKey,
            "version": self.version,
            "format": self.format,

        }

        return self.Request(request_method="post", **params)
