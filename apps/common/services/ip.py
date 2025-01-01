from common.ip2location import IP2LocationBackend


class IPService:
    backend = IP2LocationBackend()

    @staticmethod
    def get_ip_info(ip_address: str) -> dict:
        """
        获取 IP 地址的地理位置信息
        :param ip_address: 待查询的 IP 地址
        :return: 包含地理位置信息的字典
        """
        if not IP2LocationBackend.is_initialized():
            raise RuntimeError("IP2LocationBackend is not initialized.")

        return IP2LocationBackend.get_ip_info(ip_address)
