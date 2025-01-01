from threading import Lock

from loguru import logger

import IP2Location


class IP2LocationBackend:
    _database = None
    _lock = Lock()
    _is_initialized = False
    _logger = logger.bind(component="IP")

    @classmethod
    def initialize(cls, database_path: str) -> None:
        """
        初始化 IP2Location 数据库
        :param database_path: IP2Location 数据库文件路径
        """
        if cls._is_initialized:
            cls._logger.info("IP2Location database is already initialized.")

        with cls._lock:
            if cls._is_initialized:
                return

            try:
                cls._database = IP2Location.IP2Location(database_path)
                cls._is_initialized = True
                cls._logger.info(
                    f"IP2Location database initialized with: {database_path}"
                )
            except FileNotFoundError as e:
                cls._logger.error(f"IP2Location database not found: {e}")
                raise RuntimeError(
                    "IP2Location database initialization failed due to missing file."
                ) from e
            except Exception as e:
                cls._logger.error(f"Failed to initialize IP2Location database: {e}")
                raise RuntimeError("IP2Location database initialization failed.") from e

    @classmethod
    def get_ip_info(cls, ip_address: str) -> dict:
        """
        获取 IP 地址的地理位置信息
        :param ip_address: 需要查询的 IP 地址
        :return: 包含地理位置信息的字典
        """
        if not cls._is_initialized or cls._database is None:
            raise RuntimeError("IP2Location database is not initialized.")

        try:
            record = cls._database.get_all(ip_address)
            return {
                "country": record.country_long or "Unknown",  # 国家
                "country_code": record.country_short or "Unknown",  # 国家 ISO 代码
                "region": record.region or "Unknown",  # 省/州
                "city": record.city or "Unknown",  # 城市
                "latitude": record.latitude or 0.0,  # 纬度
                "longitude": record.longitude or 0.0,  # 经度
                "postal_code": record.zipcode or "Unknown",  # 邮编
                "time_zone": record.timezone or "Unknown",  # 时区
            }
        except ValueError as e:
            cls._logger.error(f"Invalid IP address '{ip_address}': {e}")
        except Exception as e:
            cls._logger.error(f"Error retrieving IP info for {ip_address}: {e}")

        return {
            "country": "Unknown",
            "country_code": "Unknown",
            "region": "Unknown",
            "city": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
            "postal_code": "Unknown",
            "time_zone": "Unknown",
        }

    @classmethod
    def is_initialized(cls) -> bool:
        """
        检查数据库是否已初始化
        :return: True 表示已初始化，False 表示未初始化
        """
        return cls._is_initialized
