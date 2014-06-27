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

def gPS2floatT(x):
    return tuple([float(y) for y in x.split(',')])

def gPS2intT(x):
    return tuple([int(float(y)) for y in x.split(',')])

def T2gPS(x):
    return reduce(lambda x,y: unicode(x) + ',' + unicode(y), x)
    
def unselect():
    try:
        selectedNode.attr['selected'] = 'False'
    except:
        pass
    selectedNode = None

def unhold():
    try:
        heldNode.attr['held'] = 'False'
    except:
        pass
    heldNode = None

def unhover():
    try:
        hoverNode.attr['hover'] = 'False'
    except:
        pass
    hoverNode = None
    
def select(node):
    unselect()
    unhover()
    selectedNode = node
    selectedNode.attr['selected'] = 'True'

def hold(node):
    unhold()
    unhover()
    node.attr['held'] = 'True'
    heldNode = node

def hover(node):
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
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawGraph( qp )
        qp.end()

    def drawGraph( self, qp ):
        global G
        for e in G.edges():
            self.drawEdge(qp,e)
        for n in G.nodes():
            self.drawNode(qp,n)

    def drawEdge( self, qp, e):
        pString = e[0].attr['pos']
        pos1 = QPoint(*gPS2intT(pString))
        pString = e[1].attr['pos']
        pos2 = QPoint(*gPS2intT(pString))
        qp.drawLine(pos1,pos2)

    def drawNode( self, qp, n):
        pString = n.attr['pos']
        p = QPoint(*gPS2intT(pString))
        if (n.attr['hover'] == 'True'):
            qp.setPen(QColor(n.attr['hoverColor']))
        elif (n.attr['held'] == 'True'):
            qp.setPen(QColor(n.attr['heldColor']))
        elif (n.attr['selected'] == 'True'):
            qp.setPen(QColor(n.attr['selectedColor']))
        else:
            qp.setPen(QColor(n.attr['color']))
        qp.drawEllipse(p,nodeRad,nodeRad)
        
            
    def getClosestNode(self,pos):
        global G
        positions = [(n,n.attr['pos']) for n in G.nodes()]
        numPos = [(n,gPS2floatT(s)) for (n,s) in positions]
        dVecs = [(n,x-pos[0], y-pos[1]) for (n,(x,y)) in numPos]
        distances = [(n,x**2 + y**2) for (n,x,y) in dVecs]
        r = reduce(min2,distances)
        return r

        
def main():
    global G
    global window
    global app
    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(3,1)
    G.get_node(1).attr['color'] = 'red'
    G.get_node(2).attr['color'] = 'blue'
    G.get_node(3).attr['color'] = 'green'
    G.get_node(1).attr['hoverColor'] = 'darkRed'
    G.get_node(2).attr['hoverColor'] = 'darkBlue'
    G.get_node(3).attr['hoverColor'] = 'darkGreen'
    G.get_node(1).attr['selectedColor'] = 'lightGray'
    G.get_node(2).attr['selectedColor'] = 'lightGray'
    G.get_node(3).attr['selectedColor'] = 'lightGray'
    G.get_node(1).attr['heldColor'] = 'white'
    G.get_node(2).attr['heldColor'] = 'white'
    G.get_node(3).attr['heldColor'] = 'white'
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
