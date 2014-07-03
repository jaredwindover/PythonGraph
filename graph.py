import sys
import pygraphviz as pgv
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cursor import *
from math import atan2, degrees, pi, sqrt, sin, cos
from time import clock

windowTitle = "Mouse Controlled Graph"
geometry = (300,300,500,500)

app = 0
window = 0
G = pgv.AGraph()
nodeRad = 25
selectedNode = None
hoverNode = None
heldNode = None
maxNode = 0

fps = 30

cKinetic = 80
cStatic = 100
baseForce = 0.0001
thresholdVelocity = 0.1
maxVelocity = 1000

def mixColors(qcol1,qcol2,per1,per2):
    r = (qcol1.redF()*per1 + qcol2.redF()*per2)/(per1 + per2)
    b = (qcol1.blueF()*per1 + qcol2.blueF()*per2)/(per1 + per2)
    g = (qcol1.greenF()*per1 + qcol2.greenF()*per2)/(per1 + per2)
    a = (qcol1.alphaF()*per1 + qcol2.alphaF()*per2)/(per1 + per2)
    return QColor.fromRgbF(r,g,b,a)
    
def norm(point):
    return sqrt(point.x()**2 + point.y()**2)

def dot(qp1,qp2):
    return qp1.x()*qp2.x() + qp1.y()*qp2.y()

def proj(qp1,qp2):
    m2 = norm(qp2)
    qp2hat = qp2/m2
    return dot(qp1,qp2hat)*qp2hat
    
def pointAtAngle(angle):
    return QPointF(cos(angle),sin(angle))

def gPS2floatT(x):
    return tuple([float(y) for y in x.split(',')])

def gPS2intT(x):
    return tuple([int(float(y)) for y in x.split(',')])

def T2gPS(x):
    return reduce(lambda x,y: unicode(x) + ',' + unicode(y), x)

def gPS2floatQp(x):
    return QPointF(*gPS2floatT(x))

def gPS2intQp(x):
    return QPoint(*gPS2intT(x))

def Qp2gPS(qp):
    return unicode(qp.x()) + ',' + unicode(qp.y())
    
def unselect():
    global selectedNode
    try:
        selectedNode.attr['selected'] = 'False'
    except:
        pass
    selectedNode = None

def unhold():
    global heldNode
    global window
    mouse2nodeVel = 10
    try:
        heldNode.attr['held'] = 'False'
        vel = QPointF(window.cursor.x - window.cursor._px,window.cursor.y - window.cursor._py)
        print vel.x(), ' ',vel.y()
        heldNode.attr['velocity'] = Qp2gPS(mouse2nodeVel*vel)
    except:
        pass
    heldNode = None

def unhover():
    global hoverNode
    try:
        hoverNode.attr['hover'] = 'False'
    except:
        pass
    hoverNode = None
    
def select(node):
    global selectedNode
    unhover()
    same = (node == selectedNode)
    unselect()
    if not same:
        selectedNode = node
        selectedNode.attr['selected'] = 'True'
        selectedNode.attr['velocity'] = u'0,0'

def hold(node):
    global heldNode
    unhold()
    unhover()
    heldNode = node
    heldNode.attr['held'] = 'True'
    heldNode.attr['velocity'] = u'0,0'

def hover(node):
    global hoverNode
    unhover()
    hoverNode = node
    hoverNode.attr['hover'] = 'True'
    
def min2(a,b):
    if (a[1] < b[1]):
        return a
    else:
        return b

def StretchyPath(pos1,pos2,rad1,rad2,mFac,maxSep,minSep = 0):
    rAngle = atan2(pos2.y()-pos1.y(),pos2.x()-pos1.x() )%(2*pi)
    distPos1toPos2 = norm(pos2 - pos1)
    mid = (pos1 + pos2) / 2
    leftAngle = rAngle + pi/2
    rightAngle = leftAngle + pi
    leftPoint = pointAtAngle(leftAngle)
    rightPoint = pointAtAngle(rightAngle)
    p1 = rad1*leftPoint + pos1
    if (distPos1toPos2 == 0):
        p2 = (maxSep/2)*leftPoint + mid
    else:
        p2 = min(mFac/distPos1toPos2+minSep/2,maxSep/2)*leftPoint+mid
    p3 = rad2*leftPoint + pos2
    p4 = rad2*rightPoint + pos2
    if (distPos1toPos2 == 0):
        p5 =(maxSep/2)*rightPoint + mid
    else:
        p5 =min(mFac/distPos1toPos2+minSep/2,maxSep/2)*rightPoint+mid
    p6 = rad1*rightPoint + pos1
    path = QPainterPath()
    path.moveTo(p6)
    rect1 = QRectF(pos1.x()- rad1, pos1.y()- rad1,2*rad1,2*rad1)
    path.arcTo(rect1,degrees(-rightAngle),180)
    sc = 0.05*distPos1toPos2
    C1 = 1.0*sc
    c1 = 3.0*sc
    C2 = 1.0*sc
    c2 = 3.0*sc
    up2to1 = (pos2 - pos1)/distPos1toPos2
    conP1 = QPointF(p1 + up2to1*C1)
    conP2a = QPointF(p2 -up2to1*c1)
    path.cubicTo(conP1,conP2a,p2)
    conP2b = QPointF(p2 + up2to1*c2)
    conP3 = QPointF(p3 -up2to1*C2)
    path.cubicTo(conP2b,conP3,p3)
    rect2 = QRectF(pos2.x()-rad2, pos2.y()-rad2, 2*rad2, 2*rad2)
    path.arcTo(rect2,degrees(-leftAngle),180)
    conP4 = p4 - p3 + conP3
    conP5a = p5 - p2 + conP2b
    path.cubicTo(conP4,conP5a,p5)
    conP5b = p5 - p2 + conP2a
    conP6 = p6 - p1 +conP1
    path.cubicTo(conP5b,conP6,p6)
    return path

def initNode(node,color,hoverColor,selectedColor='white',heldColor='black',held='False',selected='False',hover='False'):
    node.attr['color'] = color
    node.attr['hoverColor'] = hoverColor
    node.attr['selectedColor'] = selectedColor
    node.attr['heldColor'] = heldColor
    node.attr['held'] = 'False'
    node.attr['selected'] = 'False'
    node.attr['hover'] = 'False'
    node.attr['force'] = u'0,0'
    node.attr['acceleration'] = u'0,0'
    node.attr['velocity'] = u'0,0'
    node.attr['position'] = u'0,0'
    node.attr['mass'] = u'1'

    
def updateForce(node):
    global G
    global cKinetic
    global cStatic
    if (node.attr['held'] == 'False' and node.attr['selected'] == 'False'):
        F = QPointF(0,0)
        for other in G.neighbors(node):
            pnode = gPS2floatQp(node.attr['pos'])
            pother = gPS2floatQp(other.attr['pos'])
            dist = norm(pnode - pother)
            F = F + baseForce*(pother-pnode)*(dist**2)
        node.attr['force'] = Qp2gPS(F)
        
def updateAcceleration(node):
    global G
    if (node.attr['held'] == 'False' and node.attr['selected'] == 'False'):
        F = gPS2floatQp(node.attr['force'])
        Fm = norm(F)
        V = gPS2floatQp(node.attr['velocity'])
        Vm = norm(V)
        m = float(node.attr['mass'])
        if Vm > 0:
            Ff = -(cKinetic/Vm)*V
            FdirFf = proj(F,Ff)
            Fr = F - FdirFf
            Fg = FdirFf + Ff
            if norm(Fg) <= 0:
                A = Fr/m
            else:
                A = (Fr + Fg)/m
        elif not Fm == 0:
            
            Ff = (-cStatic/Fm)*F
            if Fm > cStatic:
                A = (F+Ff)/m
            else:
                A = QPointF(0,0)
        else:
            A = QPointF(0,0)
        node.attr['acceleration']=Qp2gPS(A)

def updateVelocity(node):
    global G
    if (node.attr['held'] == 'False' and node.attr['selected'] == 'False'):
        V = gPS2floatQp(node.attr['velocity'])
        V = V + gPS2floatQp(node.attr['acceleration'])/30
        Vm = norm(V)
        if Vm > thresholdVelocity:
            if Vm > maxVelocity:
                node.attr['velocity'] = Qp2gPS((maxVelocity/Vm)*V)
            else:
                node.attr['velocity'] = Qp2gPS(V)
        else:
            node.attr['velocity'] = u'0,0'

def checkCollide(node):
    global window
    size = window.size()
    width = size.width() - nodeRad
    height = size.height() - nodeRad
    pos = gPS2floatQp(node.attr['pos'])
    vel = gPS2floatQp(node.attr['velocity'])
    if (pos.x() < 0 + nodeRad):
        vel.setX(-vel.x())
        pos.setX(nodeRad)
    elif (pos.x() > width):
        vel.setX(-vel.x())
        pos.setX(width)
    if (pos.y() < 0 + nodeRad):
        vel.setY(-vel.y())
        pos.setY(nodeRad)
    elif (pos.y() > height):
        vel.setY(-vel.y())
        pos.setY(height)
    node.attr['velocity'] = Qp2gPS(vel)
    node.attr['pos'] = Qp2gPS(pos)
            
def updatePosition(node):
    global G
    if (node.attr['held'] == 'False' and node.attr['selected'] == 'False'):
        P = gPS2floatQp(node.attr['pos'])
        V = gPS2floatQp(node.attr['velocity'])
        P = P + V/30
        node.attr['pos'] = Qp2gPS(P)

        
class Window(QWidget):
    
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        self.leftClickOnRelease = False
        self.cursor = Cursor()

    def initUI(self):
        global windowTitle
        global geometry
        self.setGeometry(*geometry)
        self.setMouseTracking(True)
        self.setWindowTitle(windowTitle)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor('pink'))
        self.setPalette(pal)
        self.autoFillBackground = True
        self.show()

    def mousePressEvent(self, event):
        self.cursor.update(event)
        self.leftClickOnRelease = True
        self.onLeftPress()
        self.repaint()
        
    def mouseReleaseEvent(self, event):
        self.cursor.update(event)
        if self.leftClickOnRelease:
            self.onLeftClick()
        self.onLeftRelease()
        self.repaint()

    def mouseMoveEvent(self, event):
        self.cursor.update(event)
        self.leftClickOnRelease = False
        self.cursor.hasMoved = True
        self.cursor.moving = True
        if self.cursor.leftDown:
            self.onLeftDrag()
        else:
            self.onLeftHover()
        self.repaint()

    def onLeftClick(self):
        pos = (self.cursor.x,self.cursor.y)
        (node,dist) = self.getClosestNode(pos)
        if dist < nodeRad**2:
            select(node)
        else:
            unselect()
            
        
    def onLeftDrag(self):
        pos = (self.cursor.x,self.cursor.y)
        try:
            heldNode.attr['pos'] = T2gPS(pos)
        except:
            pass

    def onLeftHover(self):
        pos = (self.cursor.x,self.cursor.y)
        (node,dist) = self.getClosestNode(pos)
        if dist < nodeRad**2:
            hover(node)
        else:
            unhover()

    def onLeftPress(self):
        pos = (self.cursor.x,self.cursor.y)
        (node,dist) = self.getClosestNode(pos)
        if dist < nodeRad**2:
            hold(node)

    def onLeftRelease(self):
        unhold()
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.drawGraph( qp )
        qp.end()

    def drawGraph( self, qp ):
        global G
        for e in G.edges():
            self.drawEdge(qp,e)
        for n in G.nodes():
            self.drawNode(qp,n)

    def drawEdge( self, qp, e):
        #qp.setPen(QColor(0,0,0,0))
        qp.setPen(QColor('black'))
        pString = e[0].attr['pos']
        pos1 = QPointF(*gPS2intT(pString))
        pString = e[1].attr['pos']
        pos2 = QPointF(*gPS2intT(pString))
        path = StretchyPath(pos1,pos2,nodeRad,nodeRad,1000,50,10)
        lg = QLinearGradient(pos1,pos2)
        qcol1 = QColor(e[0].attr['color'])
        qcol2 = QColor(e[1].attr['color'])
        qcolm = mixColors(qcol1,qcol2,1,1)
        qcolm.setAlphaF(0.7)
        lg.setColorAt(0,qcol1)
        lg.setColorAt(0.5,qcolm)
        lg.setColorAt(1,qcol2)
        qp.setBrush(lg)
        qp.drawPath(path)

    def drawNode( self, qp, n):
        pString = n.attr['pos']
        p = QPoint(*gPS2intT(pString))
        rg = QRadialGradient(p,nodeRad,p)
        rg.setCenter(p)
        if (n.attr['hover'] == 'True'):
            qc = QColor(n.attr['hoverColor'])
        elif (n.attr['held'] == 'True'):
            qc = QColor(n.attr['heldColor'])
        elif (n.attr['selected'] == 'True'):
            qc = QColor(n.attr['selectedColor'])
        else:
            qc = QColor(n.attr['color'])
        rg.setColorAt(0,qc)
        rg.setColorAt(0.6,qc)
        rg.setColorAt(1,QColor(0,0,0,0))
        qp.setBrush(rg)
        qp.setPen(QColor(0,0,0,0))
        #qp.setPen(qc)
        qp.drawEllipse(p,nodeRad,nodeRad)
        

    def updateGraph(self):
        global fps
        t1 = clock()
        self.updateCursorVelocity()
        self.updateForces()
        self.updateAccelerations()
        self.updateVelocities()
        self.checkCollisions()
        self.updatePositions()
        self.repaint()
        QTimer.singleShot(max(0,1000/fps - (clock() - t1)),self.updateGraph)

    def checkCollisions(self):
        for n in G.nodes():
            checkCollide(n)
        
    def updateCursorVelocity(self):
        if self.cursor.hasMoved:
            self.cursor.hasMoved = False
        else:
            self.cursor.moving = False
        
    def updateForces(self):
        global G
        for n in G.nodes():
            updateForce(n)

    def updateAccelerations(self):
        global G
        for n in G.nodes():
            updateAcceleration(n)

    def updateVelocities(self):
        global G
        for n in G.nodes():
            updateVelocity(n)

    def updatePositions(self):
        global G
        for n in G.nodes():
            updatePosition(n)
        
    def getClosestNode(self,pos):
        global G
        positions = [(n,n.attr['pos']) for n in G.nodes()]
        numPos = [(n,gPS2floatT(s)) for (n,s) in positions]
        dVecs = [(n,x-pos[0], y-pos[1]) for (n,(x,y)) in numPos]
        distances = [(n,x**2 + y**2) for (n,x,y) in dVecs]
        r = reduce(min2,distances)
        return r

    def addNode(self,pos):
        global G
        maxNode = maxNode + 1
        G.add_node(maxNode)
        G.get_node(maxNode).attr['color'] = 'cyan'
        G.get_node(maxNode)
        
def main():
    global G
    global window
    global app
    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(3,1)
    #G.add_node(1)
    maxNode = 3
    initNode(G.get_node(1),'red','darkRed')
    initNode(G.get_node(2),'blue','darkBlue')
    initNode(G.get_node(3),'green','darkGreen')
    G.layout()
    app = QApplication(sys.argv)
    window = Window()
    window.updateGraph()
    app.exec_()

if __name__ == '__main__':
    main()
