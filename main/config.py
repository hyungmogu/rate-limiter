import os

class BaseConfig(object):
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST= os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT= os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB= os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL= os.environ['CACHE_REDIS_URL']
    CACHE_REDIS_PASSWORD= os.environ['CACHE_REDIS_PASSWORD']