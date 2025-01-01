import multiprocessing
import os


# 获取当前进程的 Worker ID (0-31)
def get_unique_worker_id():
    """
    基于进程 ID 生成唯一的 Worker ID。
    范围：0-31，保证合法性。
    """
    return os.getpid() % 32  # 取进程 ID 模 32，确保范围在 0-31


def on_starting(server):
    """
    Gunicorn 服务启动时运行的钩子函数。
    为每个 Worker 动态分配 CLICKHOUSE_WORKER_ID 和 CLICKHOUSE_DATACENTER_ID。
    """
    datacenter_id = 1  # 固定数据中心 ID
    worker_id = get_unique_worker_id()
    os.environ["WORKER_ID"] = str(worker_id)
    os.environ["DATACENTER_ID"] = str(datacenter_id)
    print(
        f"[Gunicorn] Initialized Worker ID: {worker_id}, Datacenter ID: {datacenter_id}"
    )


def post_fork(server, worker):
    """
    在每个 Worker 进程创建后执行。
    """
    worker_id = get_unique_worker_id()
    os.environ["WORKER_ID"] = str(worker_id)
    os.environ["DATACENTER_ID"] = "1"
    print(f"[Gunicorn Worker] Worker ID: {worker_id} started with PID: {os.getpid()}")


# Gunicorn 配置参数
workers = multiprocessing.cpu_count() * 2 + 1  # 根据 CPU 核心数计算 Worker 数量
threads = 4  # 每个工作进程有 4 个线程
worker_class = "sync"  # Worker 类型
bind = "0.0.0.0:8000"  # 监听端口
timeout = 60  # 请求超时时间
loglevel = "info"  # 日志级别
accesslog = "-"  # 访问日志，"-" 表示输出到标准输出
errorlog = "-"  # 错误日志
max_requests = 10000  # 每个工作进程最大处理请求数，超出后会重启进程
max_requests_jitter = 1000  # 在 max_requests 基础上增加随机波动，以防止进程在完全相同的时间重启，避免大规模并发重启
graceful_timeout = 30
