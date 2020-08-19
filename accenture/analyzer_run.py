#!/usr/bin/env python3
#   This is the starting point of the analyser
#

import time
import argparse
import simplejson as json
from   kafka import KafkaProducer

#   The script with the special functions for interface to Redis and Kafka
from detector import VideoDetector
from connectors import RedisConnector

parser = argparse.ArgumentParser(description="VideoDetector description")
parser.add_argument('-g', "--IngestionId", default='00AA00AA00AA00AA', action="store",
                    help="ingestion id to be processed")
parser.add_argument('-s', "--RedisConnection", default='redis:6379', action="store",
                    help="Redis server URL and port. "
                         "Additional servers and ports separated by ',' or ';', format: server[:port],[server:port].")
parser.add_argument("--KafkaConnection", default='kafka:9092', action="store",
                    help="Kafka address. Default kafka:9092")
parser.add_argument("--KafkaTopic", default='vaMicroEvents', action="store",
                    help="KafkaTopic for the object detection messages. Default vaMicroEvents.")

module_name = "VideoDetector"
module_number = "1" # TODO


def main():
    properties = parser.parse_args()

    redis = RedisConnector(ingestion=properties.IngestionId, redis_connection=properties.RedisConnection)
    kafka_producer = KafkaProducer(bootstrap_servers=properties.KafkaConnection)
    redis.wait_for_first_frame()
    detector = VideoDetector(context=properties.IngestionId, module_number=module_number)

    while True:  # main loop
        watch = time.time()
        image, timestamp = redis.get_frame()

        if not timestamp:
            time.sleep(.1)
            continue
        #  We call the method detect of the VideoDetector
        detections = detector.detect(image=image, timestamp=timestamp, frame_count=redis.last_count)
        for detection in detections:
            print(detection.todict())
            kafka_producer.send(topic=properties.KafkaTopic, value=str.encode(json.dumps(detection.todict())))

        fps = 1/(time.time()-watch)
        print("fps {}".format(fps))


if __name__ == "__main__":
    main()
