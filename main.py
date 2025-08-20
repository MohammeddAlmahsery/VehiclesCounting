"""

Video Source: https://youtu.be/wqctLW0Hb_0?si=GB8ypeICIMigsnGQ

"""

from ikomia.dataprocess.workflow import Workflow
import cv2 as cv
from utils import draw_info, is_vehicle_entering, is_vehicle_leaving, INPUT_PATH, OUTPUT_PATH

wf = Workflow()
detector = wf.add_task(name="infer_yolo_v8", auto_connect=True)
tracking = wf.add_task(name="infer_deepsort", auto_connect=True)
tracking.set_parameters({
    "categories": "all",
    "conf_thres": "0.5",
})

stream = cv.VideoCapture(INPUT_PATH)
if not stream.isOpened():
    print("Error: Could not open video.")
    exit()

frame_width = int(stream.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(stream.get(cv.CAP_PROP_FRAME_HEIGHT))
frame_rate = stream.get(cv.CAP_PROP_FPS)

fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter(OUTPUT_PATH, fourcc, frame_rate, (frame_width, frame_height))

cars_inside = 0
cars_entered = 0
cars_left = 0
cars_status = {"entered": [], "left": []}

while True:

    ret, frame = stream.read()

    if not ret:
        print("Info: End of video or error.")
        break

    # Run the workflow on current frame
    wf.run_on(array=frame)

    # Get results
    image_out = tracking.get_output(0)
    obj_detect_out = tracking.get_output(1)
    objects = obj_detect_out.get_objects()

    for object in objects:
        
        if object.id not in cars_status['entered'] and object.id not in cars_status['left']:
            
            if is_vehicle_entering(object):
                
                cars_inside += 1
                cars_entered += 1
                cars_status['entered'].append(object.id)
            
            if is_vehicle_leaving(object):

                cars_inside -= 1
                cars_left += 1
                cars_status['left'].append(object.id)
    
    # Convert the result to BGR color space for displaying
    img_out = image_out.get_image_with_graphics(obj_detect_out)

    # Write details on frame
    img_out = draw_info(img_out, cars_inside, cars_entered, cars_left)
    
    # Save resulted frame
    out.write(img_out)

    resized_image = cv.resize(img_out, (int(frame_width*1.75), int(frame_height*1.75)), interpolation=cv.INTER_LINEAR)
    cv.imshow("Result", resized_image)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()    
out.release()
cv.destroyAllWindows()
