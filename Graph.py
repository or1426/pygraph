#edges are directed!!!!
from ArrowPlot import arrowplot
class Edge(object):
    def __init__(self, name=None,dest_node=None, length=0,
                 colours = {'selected':'red','unselected':'cyan'}):
        self.name = name
        self.dest_node = dest_node
        self.length = length
        self.colours = colours
        self.state = 'unselected'
    def __getstate__(self):
        return {"name":self.name,
                "dest_node":self.dest_node,
                "length":self.length,
                "colours":self.colours,
                "state":self.state}

    def __setstate(self, state):
        self.name = state["name"]
        self.dest_node = state["dest_node"]
        self.length = state["length"]
        self.colours = state["colours"] 
        self.state = state["state"]
class Node(object):
    def __init__(self, name=None, x=0,y=0,
                 colours = {'selected':'red','unselected':'blue',}):
        self.edge_list = []
        self.name = name
        self.x = x
        self.y = y
        self.colours = colours
        self.state = 'unselected'
    def add_edge(self, edge):
        self.edge_list.append(edge)
    def add_edge_to(self, dest_node=None, length=None, 
                    colours = {'selected':'red','unselected':'blue',}):
        s = "[" + self.name + "]"  + "--" + str(length) + "-->" + "["+ dest_node.name + "]"
        edge = Edge(name=s,dest_node=dest_node, length=length,colours=colours)
        self.edge_list.append(edge)
        return edge
        
    def __repr__(self):
        s = '[' + self.name + ':'
        for edge in self.edge_list:
            target, length = edge.dest_node, edge.length
            s += '--' + str(length) + '-->' + str(target.name) + '\n'
        s += ']\n'
        return s

    def draw(self, axes):
        colour=self.colours[self.state]
        self.artist, = axes.plot(self.x,self.y,'o',color=colour,picker=10,alpha=0.5)
        axes.text(x=self.x, y=self.y, s=self.name, color='black')
        for edge in self.edge_list:
            edge.artist, = arrowplot(axes,
                                     [self.x, edge.dest_node.x],
                                     [self.y, edge.dest_node.y],
                                     narrs=1,
                                     direc='pos', 
                                     hl = 0.1,
                                     hw=10,
                                     dspace=0.3,
                                     c=edge.colours[edge.state],
                                     picker=2, 
                                     s=str(edge.length))
    def __getstate__(self):
        return {"edge_list":self.edge_list,
                "name":self.name,
                "x":self.x,
                "y":self.y,
                "colours":self.colours,
                "state":self.state}
    def __setstate__(self, state):
        self.edge_list = state["edge_list"]
        self.name = state["name"]
        self.x = state["x"]
        self.y = state["y"]
        self.colours = state["colours"]
        self.state = state["state"]
class Graph(object):
    def __init__(self, name=None,filePath=None):
        self.name = name 
        if filePath == None:
            self.node_list = []

    def add_node(self, node):
        self.node_list.append(node)

    
