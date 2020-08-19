#
#  Example of skeleton for the analyser we use pytorch instead of tensorflow
#
#
import tensorflow
import numpy

from vaspy import ObjectDetected, ObjectTracker, non_maxima_suppression 

# this is pseudo sample 
class TensorflowDetector:

    def __init__(self, model_path, threshold, categories, context, module_number, gpu):
        # ....
        # Detector variables setup
        # support advanced tracking
        # code omitted
        # 
        self.tracker = ObjectTracker()

        detection_graph = tensorflow.Graph()
        
        # ....
        # graph setup
        # code omitted
        # 

        self.graph = detection_graph

        # ....
        # gpu initialization and setup
        # code omitted
        # 

    def detect(self, image, timestamp, frame_count, fps=25):
        
        # ....
        # run iference with tensorflow session on given image
        # code omitted
        # 
        output_dict = self.sess.run(
             # code omitted
        )

        # ....
        # types convertion as appropriate
        # code omitted
        #
        output_dict['num_detections'] = int(output_dict['num_detections'][0])
        output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(numpy.uint8)
        output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
        output_dict['detection_scores'] = output_dict['detection_scores'][0]
        if 'detection_masks' in output_dict:
            output_dict['detection_masks'] = output_dict['detection_masks'][0]

        # ....
        # collect detection with higher confidence score
        # code omitted
        #
        detections = []
        for score, label, bbox in zip(output_dict['detection_scores'], output_dict['detection_classes'],
                                      output_dict['detection_boxes']):
            if score > self.threshold:
                ymin, xmin, ymax, xmax = [coordinate.item() for coordinate in bbox]


                # ....
                # map to ObjectDetected which implements MicroEvent
                # 
                message = ObjectDetected(
                    timestamp=timestamp,
                    bounding_box=[xmin, ymin, xmax, ymax],
                    classification=self.categories[label.item()],
                    confidence=score,
                    context=self.context,
                    module_number=self.module_number,
                    frame_count=frame_count
                )
                detections.append(message)

        # ....
        # update tracker
        #
        detections = non_maxima_suppression(detections)
        self.tracker.track(detections, fps=fps)
        return detections


### --------------------------------------------------------- ###
#      once implemented you can call
#
#      # runners.py
#      from tensorflow_detector import TensorflowDetector
#      analyzer = TensorflowDetector(.....)
#
#
#      # InfiniteRunner
#      while True:  
#        detections = analyzer.detect(
#            image=image,
#            timestamp=timestamp,
#            frame_count=redis.last_count,
#            fps=fps
#        )
#        
#        # send JSON data to kafka
#        for message in detections:
#          kafka_producer.send(topic=vaMicroEvents_topic, value=str.encode(json.dumps(message.todict()))) 
#     
#     
#        # send stream with detection boundingboxes as overlays
#        annotated_image = draw_on_image(fps=fps, image=image, detections=detections)  # draw_on_image from vasp-ai or custom draw_on_image
#        success, encoded_image = cv2.imencode('.jpg', annotated_image)
#        self.kafka_producer.send(stream_topic, encoded_image.tobytes())