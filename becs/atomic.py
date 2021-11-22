# Inspired by: https://www.callicoder.com/distributed-unique-ID-sequence-number-generator/ # noqa: E501
# Which in turn is inspired by snowflake service

import datetime
import math
from time import time
from typing import Optional

from becs.exceptions import InvalidSystemClock

UNUSED_BITS = 1  # always 0
EPOCH_BITS = 41  # 2199023255551
NODE_ID_BITS = 10  # up to 1024 nodes
SEQUENCE_BITS = 12  # internal counter, up to 4095 max values
MAX_SEQUENCE = int(math.pow(2, SEQUENCE_BITS) - 1)


class AtomicID:
    _epoch: int = int(datetime.datetime(2021, 11, 20, 1, 0, 0, 0).timestamp()) * 1000
    _node_id: int = 1
    _last_timestamp: int = -1
    _sequence: int = 0

    def __init__(
        self, node_id: Optional[int] = None, custom_epoc: Optional[int] = None
    ):
        if custom_epoc:
            self._epoch = custom_epoc

        if node_id:
            self._node_id = node_id

    def _timestamp(self) -> int:
        return int(time() * 1000) - self._epoch

    def next(self) -> int:
        ts = self._timestamp()
        if ts < self._last_timestamp:
            raise InvalidSystemClock()

        if ts == self._last_timestamp:
            self._sequence = (self._sequence + 1) & MAX_SEQUENCE
            if self._sequence == 0:
                # block until we've moved one millisecond forward
                while ts == self._last_timestamp:
                    ts = self._timestamp()

        else:
            self._sequence = 0

        self._last_timestamp = ts

        id = ts << (NODE_ID_BITS + SEQUENCE_BITS)
        id |= self._node_id << SEQUENCE_BITS
        id |= self._sequence

        return id
