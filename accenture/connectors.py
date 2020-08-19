from redis import StrictRedis
from rediscluster import StrictRedisCluster
import cv2
import numpy
import re
import time


class RedisConnector:
    count_key_format = '{{ingestion/{0}}}/frame/count'
    image_key_format = '{{ingestion/{0}}}/frame/{1}'
    timestamp_key_format = '{{ingestion/{0}}}/frame/{1}/timestamp'

    @staticmethod
    def create_redis(redis_connection):
        redis_address = list(map(str.strip, re.split('[,;]', redis_connection)))

        if len(redis_address) == 1:  # only one redis address is specified
            redis_host = redis_address[0].split(':')[0]
            redis_port = redis_address[0].split(':')[1]
            return StrictRedis(redis_host, redis_port)
        else:  # multiple redis addresses are specified
            parsed_addresses = list(map(lambda address:
                                        {"host": address.split(':')[0], "port": address.split(':')[1]},
                                        redis_address))
            # TODO handle if the instance is not cluster, but i'm trying to connect to a cluster
            return StrictRedisCluster(startup_nodes=parsed_addresses, decode_responses=False)

    def __init__(self, ingestion, redis_connection, expiration=600):
        self.redis = self.create_redis(redis_connection)
        self.ingestion = ingestion
        self.last_count = 0
        self.new_count = 0
        self.count_key = self.count_key_format.format(ingestion)
        self.expiration = expiration

    def wait_for_first_frame(self):
        while True:
            image, timestamp = self.get_frame()
            if not timestamp:
                print("Image not found, sleeping.")
                time.sleep(.1)
            else:
                height, width, channels = image.shape
                print("Video width: {}, height: {}, channels:{}".format(width, height, channels))
                break

    def get_frame(self):
        new_count = self.redis.get(self.count_key)

        if not new_count:  # count is not in redis
            print('Unable to get last frame count from redis')
            return [None, None]
        else:
            new_count = int(new_count.decode('utf-8'))

        if new_count == self.last_count:  # I already processed this image
            return [None, None]

        timestamp = self.redis.get(self.timestamp_key_format.format(self.ingestion, new_count))
        if not timestamp:
            print("Found count without timestamp, skipping.")
            return [None, None]
        else:
            timestamp = timestamp.decode('utf-8')
        image_bytes = self.redis.get(self.image_key_format.format(self.ingestion, new_count))
        if len(image_bytes) == 1:  # end of the stream
            exit(0)  # end of the stream means end of the detection

        image = cv2.imdecode(numpy.frombuffer(image_bytes, numpy.uint8), 1)
        self.last_count = new_count

        return [image, timestamp]

    def set_frame(self, frame_number, frame):
        self.redis.setex(self.image_key_format.format(self.ingestion, frame_number), self.expiration, frame)

    def set_timestamp(self, frame_number, timestamp):
        self.redis.setex(self.timestamp_key_format.format(self.ingestion, frame_number), self.expiration, timestamp)

    def set_count(self, count):
        self.redis.setex(self.count_key_format.format(self.ingestion), self.expiration, count)

    def newcount(self):
        count = self.redis.get(self.count_key_format.format(self.ingestion))
        if not count:
            return 0
        return int(count.decode('utf-8')) + 1

    def increment_and_set_frame(self, frame, timestamp):
        count = self.newcount()
        self.set_frame(frame_number=count, frame=frame)
        self.set_timestamp(frame_number=count, timestamp=timestamp)
        self.set_count(count=count)

        return count

    def specific_frame(self, frame_number):
        timestamp = self.redis.get(self.timestamp_key_format.format(self.ingestion, frame_number))
        if not timestamp:
            print("Unable to get frame at key /ingestion/{}/frame/{}.".format(self.ingestion, frame_number))
            return [None, None]
        else:
            timestamp = timestamp.decode('utf-8')
        image_bytes = self.redis.get(self.image_key_format.format(self.ingestion, frame_number))
        if len(image_bytes) == 1:  # end of the stream
            exit(0)  # end of the stream means end of the detection

        image = cv2.imdecode(numpy.frombuffer(image_bytes, numpy.uint8), 1)

        return [image, timestamp]
