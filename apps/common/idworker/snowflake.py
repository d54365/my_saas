import logging
import os
import random
import time

from .base import BaseIDWorker

logger = logging.getLogger(__name__)


class InvalidSystemClock(Exception):
    pass


# 64位ID的划分
WORKER_ID_BITS = 5
DATACENTER_ID_BITS = 5
SEQUENCE_BITS = 12

# 最大取值计算
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

# 移位偏移计算
WORKER_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 序号循环掩码
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# Twitter元年时间戳
TWEPOCH = 1288834974657


class SnowflakeIDWorker(BaseIDWorker):
    """Snowflake generate universal unique incremental id.
    Copy from https://www.cnblogs.com/oklizz/p/11865750.html
    """

    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 其实序号
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError("worker_id值越界")

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError("datacenter_id值越界")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_id(self):
        """
        获取新ID
        :return:
        """
        timestamp = self._gen_timestamp()

        # 时钟回拨
        if timestamp < self.last_timestamp:
            logging.error(
                "clock is moving backwards. Rejecting requests until {}".format(
                    self.last_timestamp
                )
            )
            raise InvalidSystemClock

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = (
            ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT)
            | (self.datacenter_id << DATACENTER_ID_SHIFT)
            | (self.worker_id << WORKER_ID_SHIFT)
            | self.sequence
        )
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


def get_environ_int(name, minium, maximum, default=None):
    value = os.environ.get(name)
    if value is not None:
        try:
            value = int(value)
        except ValueError:
            raise ValueError(
                '"%s" is not a valid %s. '
                "Hint: set value to an integer between %s and %s"
                % (value, name, minium, maximum)
            ) from ValueError
        if value < minium or value > maximum:
            raise ValueError(
                "%s must be an integer between %s and %s" % (name, minium, maximum)
            ) from ValueError
    else:
        value = default
    return value


def get_default_id_worker():
    """Default id worker for BigAutoField.

    If SnowflakeIDWorker is used, user should ensure worker id
    and datacenter id is unique among all server process.
    Use CLICKHOUSE_WORKER_ID and CLICKHOUSE_DATACENTER_ID
    environment variable to set them.
    :return: BaseIDWorker.
    """

    worker_id = get_environ_int("WORKER_ID", 0, MAX_WORKER_ID, 0)
    datacenter_id = get_environ_int("DATACENTER_ID", 0, MAX_DATACENTER_ID)
    if datacenter_id is None:
        datacenter_id = random.randint(0, MAX_DATACENTER_ID)  # nosec
    return SnowflakeIDWorker(datacenter_id=datacenter_id, worker_id=worker_id)


snowflake_worker = get_default_id_worker()
