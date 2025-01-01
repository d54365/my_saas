from typing import Any, Union

from common.cache.compressors import CompressorError
from diskcache import DjangoCache as _DjangoCache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.module_loading import import_string


class ExtendedDiskCache(_DjangoCache):
    def __init__(self, directory, params):
        super().__init__(directory, params)
        options = params.get("OPTIONS", {})

        self._serializer = None
        self._compressor = None

        serializer_path = options.get("SERIALIZER", None)
        if serializer_path:
            serializer_cls = import_string(serializer_path)
            self._serializer = serializer_cls(options)

        compressor_path = options.get("COMPRESSOR", None)
        if compressor_path:
            compressor_cls = import_string(compressor_path)
            self._compressor = compressor_cls(options)

    def add(
        self,
        key,
        value,
        timeout=DEFAULT_TIMEOUT,
        version=None,
        read=False,
        tag=None,
        retry=True,
    ) -> bool:
        value = self.encode(value)
        return super().add(key, value, timeout, version, read, tag, retry)

    def get(
        self,
        key,
        default=None,
        version=None,
        read=False,
        expire_time=False,
        tag=False,
        retry=False,
    ):
        value = super().get(key, default, version, read, expire_time, tag, retry)

        if value is None:
            return value

        return self.decode(value)

    def read(self, key, version=None):
        return super().read(key, version)

    def set(
        self,
        key,
        value,
        timeout=DEFAULT_TIMEOUT,
        version=None,
        read=False,
        tag=None,
        retry=True,
    ):
        value = self.encode(value)
        return super().set(key, value, timeout, version, read, tag, retry)

    def encode(self, value: Any) -> Union[bytes, Any]:
        if isinstance(value, bool) or not isinstance(value, int):
            if self._serializer is not None:
                value = self._serializer.dumps(value)
            if self._compressor is not None:
                value = self._compressor.compress(value)
            return value

        return value

    def decode(self, value: Union[bytes, int]) -> Any:
        try:
            value = int(value)
        except (ValueError, TypeError):
            if self._compressor:
                try:
                    value = self._compressor.decompress(value)
                except CompressorError:
                    # Handle little values, chosen to be not compressed
                    pass
            if self._serializer:
                value = self._serializer.loads(value)
        return value
