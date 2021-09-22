class Car:

    # carId: current car id
    # xPos: the x coordinate of the car
    # yPos: the y coordinate of the car
    # firstXPos:
    # distance: the Euclidean distance from the last x and y coordinate
    # direction: the direction to which the car is heading (right or left)
    # nextXPosition: saves the next possible location of a car
    def __init__(self, carId, firstXPos, xPos, yPos, distance, direction, nextXPosition):
        self.carId = carId
        self.firstXPos = firstXPos
        self.xPos = xPos
        self.yPos = yPos
        self.distance = distance
        self.direction = direction
        self.nextXPosition = nextXPosition
