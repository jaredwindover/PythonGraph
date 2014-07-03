###
##Cursor class:
#_stores information about the current
#_state of the mouse
###

class Cursor():
    def __init__(self):
        self.x = 0
        self.y = 0
        self._px = 0
        self._py = 0
        self.leftDown = False
        self.rightDown = False
        self.midDown = False
        self.hasMoved = False
        self.moving = False
        
    def setX(self,a):
        if self.x != a:
            self._px = self.x
            self.x = a

    def setY(self,a):
        if self.y != a:
            self._py = self.y
            self.y = a

    def setButtons(self,b):
        b = int(b)
        a = b % 2
        self.leftDown = (a == 1)
        b = (b - a) / 2
        a = b % 2
        self.rightDown = (a == 1)
        b = (b - a) / 2
        a = b % 2
        self.midDown = (a == 1)

    def update(self,e):
        self.setX(e.x())
        self.setY(e.y())
        self.setButtons(e.buttons())
