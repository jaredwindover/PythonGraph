import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cursor import *
from math import atan2, degrees, pi, sqrt, sin, cos

def norm(point):
    return sqrt(point.x()**2 + point.y()**2)

def pointAtAngle(angle):
    return QPointF(cos(angle),sin(angle))

def StretchyPath(qp,pos1,pos2,rad1,rad2,mFac,maxSep,minSep = 0):
    rAnglePos1toPos2 = atan2(pos2.y() - pos1.y(),pos2.x() - pos1.x() ) % (2*pi)
    distPos1toPos2 = norm(pos2 - pos1)
    mid = (pos1 + pos2) / 2
    leftAngle = rAnglePos1toPos2 + pi/2
    rightAngle = leftAngle + pi
    leftPoint = pointAtAngle(leftAngle)
    rightPoint = pointAtAngle(rightAngle)
    p1 = rad1*leftPoint + pos1
    p2 = min(mFac/distPos1toPos2 + minSep/2,maxSep/2)*leftPoint + mid
    p3 = rad2*leftPoint + pos2
    p4 = rad2*rightPoint + pos2
    p5 = min(mFac/distPos1toPos2 + minSep/2,maxSep/2)*rightPoint + mid
    p6 = rad1*rightPoint + pos1
    
    qp.setBrush(QColor(0,0,0,0))
    qp.drawEllipse(pos1,rad1,rad1)
    qp.drawEllipse(pos2,rad2,rad2)
    qp.setPen(QColor(255,0,0))
    qp.drawEllipse(p1,5,5)
    qp.setPen(QColor(0,255,0))
    qp.drawEllipse(p2,5,5)
    qp.setPen(QColor(0,0,255))
    qp.drawEllipse(p3,5,5)
    qp.setPen(QColor(255,255,0))
    qp.drawEllipse(p4,5,5)
    qp.setPen(QColor(0,255,255))
    qp.drawEllipse(p5,5,5)
    qp.setPen(QColor(255,255,255))
    qp.drawEllipse(p6,5,5)
    p = QPen(Qt.DashDotDotLine)
    p.setColor(QColor(255,0,0,255))
    qp.setPen(p)
    path = QPainterPath()
    path.moveTo(p6)
    rect1 = QRectF(pos1.x() - rad1, pos1.y() - rad1,2*rad1,2*rad1)
    path.arcTo(rect1,degrees(-rightAngle),180)
    sc = 15
    C1 = 1.0*sc
    c1 = 5.0*sc
    C2 = 0.8*sc
    c2 = 3*sc
    up2to1 = (pos2 - pos1)/distPos1toPos2
    conP1 = QPointF(p1 + up2to1*C1)
    conP2a = QPointF(p2 -up2to1*c1)
    path.cubicTo(conP1,conP2a,p2)
    conP2b = QPointF(p2 + up2to1*c2)
    conP3 = QPointF(p3 -up2to1*C2)
    path.cubicTo(conP2b,conP3,p3)
    rect2 = QRectF(pos2.x() - rad2, pos2.y() - rad2,2*rad2,2*rad2)
    path.arcTo(rect2,degrees(-leftAngle),180)
    conP4 = p4 - p3 + conP3
    conP5a = p5 - p2 + conP2b
    path.cubicTo(conP4,conP5a,p5)
    conP5b = p5 - p2 + conP2a
    conP6 = p6 - p1 +conP1
    path.cubicTo(conP5b,conP6,p6)
    qp.drawPath(path)
    
    qp.setPen(QColor(255,0,0))
    qp.setBrush(QColor(255,0,0))
    qp.drawEllipse(conP1,2,2)
    
    qp.setPen(QColor(0,255,0))
    qp.setBrush(QColor(0,255,0))
    qp.drawEllipse(conP2a,2,2)
    
    qp.drawEllipse(conP2b,2,2)
    
    qp.setPen(QColor(0,0,255))
    qp.setBrush(QColor(0,0,255))
    qp.drawEllipse(conP3,2,2)
    
    qp.setPen(QColor(255,255,0))
    qp.setBrush(QColor(255,255,0))
    qp.drawEllipse(conP4,2,2)
    
    qp.setPen(QColor(0,255,255))
    qp.setBrush(QColor(0,255,255))
    qp.drawEllipse(conP5a,2,2)
    
    qp.setPen(QColor(0,255,255))
    qp.setBrush(QColor(0,255,255))
    qp.drawEllipse(conP5b,2,2)
    
    qp.setPen(QColor(255,255,255))
    qp.setBrush(QColor(255,255,255))
    qp.drawEllipse(conP6,2,2)
    
class Window(QWidget):

    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0,0,600,600)
        self.show()
    
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        for i in range(36):
            StretchyPath(qp,QPointF(300.0,300.0),QPointF(300.0,300.0) + QPointF(250*sin(i*pi/18),250*cos(i*pi/18)),25,25,10,50,30)
        qp.end()
    

def main():
    app = QApplication(sys.argv)
    window = Window()
    app.exec_()


if __name__ == '__main__':
    main()
