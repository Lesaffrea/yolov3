#
#      The detect part of the analyser
#
import tensorflow
import numpy
import simplejson as json


inference_mock = [{"score":0.9, "detection": "person", "bb":[0,0,1,1]},{"score":0.57, "detection": "dog", "bb":[0.5,0.5,1,1]}]


class MicroEventDetection:
    decimals_count = 4
    message_type = '1011'

    def __init__(self,
                 timestamp,
                 bounding_box,
                 classification,
                 confidence,
                 context,
                 module_number,
                 frame_count,
                 sequence=0,
                 colors=None):
        self.eventid = 0, # TODO 
        self.timestamp = timestamp
        self.bounding_box = bounding_box
        self.classification = classification
        self.confidence = confidence
        self.context = context
        self.module_number = module_number
        self.frame_count = frame_count
        self.sequence = sequence
        self.colors = colors

    def todict(self):
        detection_as_dict = {
            "Context": self.context,
            "MessageType": self.message_type,
            "Module": self.module_number,
            "EventID": self.eventid,
            "Timestamp": self.timestamp,
            "BoundingBox": self.bounding_box,
            "Classification": [self.classification],
            "SampleImage": '/ingestion/{0}/frame/{1}'.format(self.context, self.frame_count),
            "SampleObject": '/ingestion/{0}/frame/{1}/{2}'.format(
                self.context,
                self.frame_count,
                json.dumps(self.bounding_box).replace(" ", "")),
            "Confidence": round(float(self.confidence), self.decimals_count),
            "Sequence": self.sequence
        }

        return detection_as_dict


# this is pseudo sample 
class VideoDetector:

    def __init__(self, context, module_number): # and your properties required for your detector
        # ....
        # Detector variables setup
        # code omitted
        # 
        self.context = context
        self.module_number = module_number
        print('Initialized!')

    def detect(self, image, timestamp, frame_count, fps=25):
        
        # ....
        # run iference with tensorflow session on given image
        # code omitted
        # 
        print('Run inference on the image.')
        # TODO your code with inference
        results = inference_mock

        # ....
        # collect detection with higher confidence score
        # code omitted
        #
        detections = []
        for result in results:
            if result['score'] > 0.6: # can be configured threshold
                print(result)
                
                # TODO map to MicroEvent and your ObjectDetected
                # ....
                # map to ObjectDetected which implements MicroEvent
                # 
                message = MicroEventDetection(
                    timestamp=timestamp,
                    bounding_box=result['bb'],
                    classification=result['detection'],
                    confidence=result['score'],
                    context=self.context,
                    module_number=self.module_number,
                    frame_count=frame_count
                )
                detections.append(message)

        # ....
        # update tracker
        #
        return detections

# once implemented you can call
# from tensorflow_detector import TensorflowDetector
# analyzer = TensorflowDetector(.....)
# analyzer.detect(.....)