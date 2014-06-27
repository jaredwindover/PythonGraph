import sys
import pygraphviz as pgv
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cursor import *


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

def gPS2floatT(x):
    return tuple([float(y) for y in x.split(',')])

def gPS2intT(x):
    return tuple([int(float(y)) for y in x.split(',')])

def T2gPS(x):
    return reduce(lambda x,y: unicode(x) + ',' + unicode(y), x)
    
def unselect():
    global selectedNode
    try:
        selectedNode.attr['selected'] = 'False'
    except:
        pass
    selectedNode = None

def unhold():
    global heldNode
    try:
        heldNode.attr['held'] = 'False'
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

def hold(node):
    global heldNode
    unhold()
    unhover()
    node.attr['held'] = 'True'
    heldNode = node

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
        qp.setPen(QColor(0,0,0,0))#'black'))
        pString = e[0].attr['pos']
        pos1 = QPoint(*gPS2intT(pString))
        pString = e[1].attr['pos']
        pos2 = QPoint(*gPS2intT(pString))
        path = QPainterPath(pos1)
        path.lineTo(pos2)
        stroker = QPainterPathStroker()
        stroker.setWidth(5)
        path2 = stroker.createStroke(path)
        lg = QLinearGradient(pos1,pos2)
        lg.setColorAt(0,QColor(e[0].attr['color']))
        lg.setColorAt(0.5,QColor(0,0,0,0))
        lg.setColorAt(1,QColor(e[1].attr['color']))
        qp.setBrush(lg)
        qp.drawPath(path2)

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
        qp.setPen(QColor(0,0,0,0))#qc)
        qp.drawEllipse(p,nodeRad,nodeRad)
        
            
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
    maxNode = 3
    G.get_node(1).attr['color'] = 'red'
    G.get_node(2).attr['color'] = 'blue'
    G.get_node(3).attr['color'] = 'green'
    G.get_node(1).attr['hoverColor'] = 'darkRed'
    G.get_node(2).attr['hoverColor'] = 'darkBlue'
    G.get_node(3).attr['hoverColor'] = 'darkGreen'
    G.get_node(1).attr['selectedColor'] = 'white'
    G.get_node(2).attr['selectedColor'] = 'white'
    G.get_node(3).attr['selectedColor'] = 'white'
    G.get_node(1).attr['heldColor'] = 'black'
    G.get_node(2).attr['heldColor'] = 'black'
    G.get_node(3).attr['heldColor'] = 'black'
    G.get_node(1).attr['held'] = 'False'
    G.get_node(2).attr['held'] = 'False'
    G.get_node(3).attr['held'] = 'False'
    G.get_node(1).attr['selected'] = 'False'
    G.get_node(2).attr['selected'] = 'False'
    G.get_node(3).attr['selected'] = 'False'
    G.get_node(1).attr['hover'] = 'False'
    G.get_node(2).attr['hover'] = 'False'
    G.get_node(3).attr['hover'] = 'False'
    G.layout()
    app = QApplication(sys.argv)
    window = Window()
    app.exec_()

if __name__ == '__main__':
    main()
