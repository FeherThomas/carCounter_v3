import cv2
import Car as Car
import databaseConnector as db
import math


# calculate euclidean distance for each on current frame and car on last frame
def calculate_euclidean_distance(cars_on_current_frame, car_x):
    distance = car_x.distance

    for x_cor_of_car, y_cor_of_car in cars_on_current_frame:

        # calculate euclidean distance to get direction of car
        if math.sqrt(pow(car_x.xPos - x_cor_of_car, 2) + pow(car_x.yPos - y_cor_of_car, 2)) < distance:
            car_x.xPos = xCorOfCar
            car_x.yPos = yCorOfCar

    return car_x.xPos, car_x.yPos


if __name__ == '__main__':

    # only drop table uncomment if you want to drop the database and/or create a new database
    db.drop_table()
    db.create_table()

    # vehicleCount is always 0, it will not be transferred to the database which is on auto increment
    vehicleCount = db.get_current_vehicle_count()

    # cap = cv2.VideoCapture(2)
    cap = cv2.VideoCapture('/home/thomas/outDo.mp4')

    # Object detection
    # object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=15, detectShadows=False)
    object_detector = cv2.createBackgroundSubtractorKNN(history=200, dist2Threshold=1200, detectShadows=False)

    carsOnLastImage = []
    carsOnCurrentImage = []
    area = 1000.0

    # while stream is open
    while cap.isOpened():
        ret, frame = cap.read()

        # Object Detection
        mask = object_detector.apply(frame)
        mask_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # object detection
        for contour in contours:

            if not cv2.contourArea(contour) < 1000:
                pass

            # calculate area and remove small elements
            if not 10000 < cv2.contourArea(contour) < 39000:
                continue

            xCorOfCar, yCorOfCar, width, height = cv2.boundingRect(contour)

            # rectangle around each car
            cv2.rectangle(frame, (xCorOfCar, yCorOfCar), (xCorOfCar + width, yCorOfCar + height), (0, 255, 0), 2)

            # red dot
            xMiddle = int((xCorOfCar + (xCorOfCar + width)) / 2)
            yMiddle = int((yCorOfCar + (yCorOfCar + height)) / 2)
            cv2.circle(frame, (xMiddle, yMiddle), 5, (0, 0, 255), 5)

            # ignore y values greater than 220
            if yMiddle > 220:
                carsOnCurrentImage.append((xMiddle, yMiddle))

        for xCorOfCar, yCorOfCar in carsOnCurrentImage:

            # if there are no cars on last frame or if on current frame are more cars than on last frame
            # create a new Car object
            if not carsOnLastImage or len(carsOnCurrentImage) > len(carsOnLastImage):

                vehicleCount += 1
                print('possible car detected, vehicleCount: ', vehicleCount)
                car = Car.Car(vehicleCount, xCorOfCar, xCorOfCar, yCorOfCar, 3000.0, 'unknown', 0)
                carsOnLastImage.append(car)

        # delete all cars from carsOnLastImage which are not updated any more
        # Cars are not updated if carsOnCurrentImage has fewer elements than carsOnLastImage
        # First elements (or cars) in carsOnLastImage are the oldest and therefore not updated anymore
        # Example: Length carsOnLastImage is 3 and length of carsOnCurrentImage is 2. This means, that
        # one car is not in the image anymore and therefore can be deleted. Cars can not vanish from the
        # road, so it has to be the oldest entry, which is on index 0 in carsOnLastImage
        if len(carsOnLastImage) > len(carsOnCurrentImage):
            diff = len(carsOnLastImage) - len(carsOnCurrentImage) - 1

            if diff > -1:
                while diff >= 0:
                    if carsOnLastImage[diff].direction == 'unknown':
                        print('Direction is unknown. Car could not be detected. Car count will be reduced'
                              ' by one')
                        vehicleCount -= 1
                        print('Updated vehicleCount:', vehicleCount)

                    carsOnLastImage.pop(diff)

                    diff = diff - 1

        # tracking of cars
        for car in carsOnLastImage:
            originalXCor = car.xPos
            originalYCor = car.yPos

            car.xPos, car.yPos = calculate_euclidean_distance(carsOnCurrentImage, car)

            # set direction of new car
            if car.xPos < originalXCor \
                    and car.direction == 'unknown' \
                    and len(carsOnLastImage) == len(carsOnCurrentImage):

                car.direction = 'left'
                print('car confirmed, moves left')
                db.insert_into_db(car.direction)

            elif car.xPos > originalXCor \
                    and car.direction == 'unknown' \
                    and len(carsOnLastImage) == len(carsOnCurrentImage):

                car.direction = 'right'
                print('car confirmed, moves right')
                db.insert_into_db(car.direction)

            if car.direction == 'left' \
                    and car.xPos > originalXCor \
                    and len(carsOnLastImage) == len(carsOnCurrentImage):

                print('Correcting cars direction. Car is moving to the right')
                car.direction = 'right'
                db.update_car_direction(car)

            if car.direction == 'right' \
                    and car.xPos < originalXCor \
                    and len(carsOnLastImage) == len(carsOnCurrentImage):

                print('Correcting cars direction. Car is moving to the left')
                car.direction = 'left'
                db.update_car_direction(car)

            cv2.putText(frame, 'CarId: ' + str(car.carId), (car.xPos, car.yPos), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

            # calculate next possible position of car
            if car.direction != 'unknown':
                if car.direction == 'left':
                    car.nextXPosition = car.xPos - (originalXCor - car.xPos)

                elif car.direction == 'right':
                    car.nextXPosition = car.xPos + (car.xPos - originalXCor)

        carsOnCurrentImage = []

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

        # key 27 is S
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
