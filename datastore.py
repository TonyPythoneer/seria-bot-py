# -*- coding: utf-8 -*-
import config
from redis import ConnectionPool, StrictRedis

redis_connection_pool = ConnectionPool.from_url(config.REDIS_URL, db=0, charset='utf-8', decode_responses=True)
redis_db = StrictRedis(connection_pool=redis_connection_pool)
