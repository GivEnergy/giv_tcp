import os, redis, logging
from rq import Worker, Queue, Connection
from GivLUT import GivQueue
from settings import GiV_Settings
listen = ['GivTCP_'+str(GiV_Settings.givtcp_instance)]


redis_url = 'redis://127.0.0.1:6379'
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(listen)
        worker.work(with_scheduler=True,logging_level=logging.CRITICAL)