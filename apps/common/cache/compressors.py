from django_redis.compressors.lz4 import Lz4Compressor as _Lz4Compressor
from django_redis.exceptions import CompressorError as _CompressorError


class Lz4Compressor(_Lz4Compressor):
    pass


class CompressorError(_CompressorError):
    pass
