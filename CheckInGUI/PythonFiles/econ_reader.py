import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
frame_count = 0
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
 
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    #frame_down = cv.pyrDown(frame)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #img = cv.adaptiveThreshold(gray_blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 31, 2)
    (thresh, thresh_img) = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    img = cv.medianBlur(thresh_img, 3)
    #img = cv.bilateralFilter(thresh_img, 27, 101, 101)
    kernel = np.ones((5,5), np.uint8)
    image = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
    image = cv.morphologyEx(image, cv.MORPH_OPEN, kernel)
    image = cv.bitwise_not(image)

    # Rectangle
    height, width = image.shape[:2]
    box_w, box_h = 300, 300 
    x1 = (width // 2) - (box_w // 2)
    y1 = (height // 2) - (box_h // 2)
    x2 = (width // 2) + (box_w // 2)
    y2 = (height // 2) + (box_h // 2)
    cv.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv.imshow('Postprocessed', image)
    cv.imshow('Color', frame)
    if frame_count % 100 == 0:
        snapshot = image[y1+3:y2-3,x1+3:x2-3]
        cv.imshow('Snapshot', cv.pyrDown(snapshot))
    if cv.waitKey(1) == ord('q'):
        break
    frame_count+=1

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

