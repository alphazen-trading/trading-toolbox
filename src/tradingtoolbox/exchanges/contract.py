from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from decimal import Decimal as D
from typing import Union
import math
import msgspec


def normalize_fraction(decim: D) -> D:
    normalized = decim.normalize()
    sign, digit, exponent = normalized.as_tuple()
    return normalized if exponent <= 0 else normalized.quantize(1)


def decimal_from_value(value: Union[str, int, float]) -> D:
    return normalize_fraction(D(str(value)))


class Precision(msgspec.Struct):
    amount: float
    price: float
    cost: Optional[float] = None
    base: Optional[str] = None
    quote: Optional[str] = None


class Limits(msgspec.Struct):
    leverage: Dict[str, Optional[float]]
    amount: Dict[str, Optional[float]]
    price: Dict[str, Optional[float]]
    cost: Dict[str, Optional[float]]


class LotSizeFilter(msgspec.Struct):
    maxOrderQty: Optional[float] = None
    minOrderQty: float = 0
    maxOrderAmt: Optional[float] = None
    minOrderAmt: Optional[float] = None
    maxMktOrderQty: Optional[float] = None
    basePrecision: Optional[float] = None
    quotePrecision: Optional[float] = None
    qtyStep: float = 0
    postOnlyMaxOrderQty: Optional[float] = None
    minNotionalValue: Optional[float] = None

    def __post_init__(self, **kwargs):
        for key in kwargs:
            try:
                setattr(self, key, float(kwargs[key]))
            except ValueError:
                setattr(self, key, 0)

        if "qtyStep" not in kwargs and self.basePrecision:
            self.qtyStep = self.basePrecision


class PriceFilter(msgspec.Struct):
    minPrice: float = 0
    maxPrice: float = 0
    tickSize: float = 0

    def __post_init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, float(kwargs[key]))


class BybitInfo(msgspec.Struct):
    symbol: str
    baseCoin: str
    quoteCoin: str
    status: str
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    innovation: Optional[str] = None
    settleCoin: Optional[str] = None
    optionsType: Optional[str] = None
    launchTime: Optional[int] = None
    deliveryTime: Optional[int] = None
    deliveryFeeRate: Optional[str] = None


class OkxInfo(msgspec.Struct):
    symbol: str
    baseCoin: str
    quoteCoin: str
    status: str
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    innovation: Optional[str] = None
    settleCoin: Optional[str] = None
    optionsType: Optional[str] = None
    launchTime: Optional[int] = None
    deliveryTime: Optional[int] = None
    deliveryFeeRate: Optional[str] = None


class FeeSide(str, Enum):
    get = "get"


class Contract(msgspec.Struct, kw_only=True):
    id: str
    symbol: str
    base: str
    quote: str
    lowercaseId: Optional[str] = None
    settle: Optional[str] = None
    baseId: str
    quoteId: str
    settleId: Optional[str] = None
    type: str
    spot: bool
    margin: Optional[bool] = None
    swap: bool
    future: bool
    option: bool
    index: Optional[bool] = None
    active: bool
    contract: bool
    linear: Optional[bool] = None
    inverse: Optional[bool] = None
    subType: Optional[str] = None
    taker: float
    maker: float
    contractSize: Optional[float] = None
    expiry: Optional[int] = None
    expiryDatetime: Optional[datetime] = None
    strike: Optional[float] = None
    optionType: Optional[str] = None
    precision: Precision
    limits: Limits
    created: Optional[int] = None
    info: Any
    tierBased: Optional[bool] = None
    percentage: Optional[bool] = None
    feeSide: Optional[FeeSide] = None
    marginModes: dict

    def round_value(self, _value: float, _step: float, how: str = "down") -> float:
        value = decimal_from_value(_value)
        step = decimal_from_value(_step)
        if how == "down":
            return float(value // step * step)
        elif how == "up":
            return float(math.ceil(value / step) * step)
        else:
            return float(round(value / step) * step)

    def round_size(self, size: float) -> float:
        if self.limits.amount["min"] is None:
            return size

        if size < self.limits.amount["min"]:
            size = self.limits.amount["min"]
            print(
                f"Size is smaller than min size. Reverting to the min allowed which is {size}"
            )
        return self.round_value(size, self.limits.amount["min"])

    def round_price(self, price: float) -> float:
        return self.round_value(price, self.precision.price)
