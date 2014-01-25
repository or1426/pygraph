#! /usr/bin/env python2

import os
import sys #for sys.maxint
import pprint
import random
import wx
import pickle
import Graph
from ArrowPlot import arrowplot

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

class GraphPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        self.colours = {'selected':'red',
                        'unselected':'cyan',}
        self.graph = Graph.Graph()
        self.initUI()
    def initUI(self):
        """ Creates the main panel with all the controls on it:
             * mpl canvas 
             * mpl navigation toolbar
             * Control panel for interaction
        """
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self, -1, self.fig)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event',self.on_click)

        self.canvas.mpl_connect('key_press_event',self.on_key)
        # Create the navigation toolbar, tied to the canvas
        #
        self.toolbar = NavigationToolbar(self.canvas)
        
        #
        # Layout with box sizers
        #
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        
        self.selectStuffRadBut=wx.RadioButton(self,
                                             label="select stuff mode",
                                             style=wx.RB_GROUP)
        
        self.createEdgeRadBut=wx.RadioButton(self,
                                             label="create edge mode")
        self.Bind(wx.EVT_RADIOBUTTON, self.clear_all_selections, self.createEdgeRadBut)
        self.createNodeRadBut=wx.RadioButton(self,
                                             label="create node mode")
        self.changeEdgeWeightRadBut=wx.RadioButton(self,
                                                   label="change edge weight mode")
        
        self.radBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.radBoxSizer.Add(self.selectStuffRadBut)
        self.radBoxSizer.Add(self.createEdgeRadBut)
        self.radBoxSizer.Add(self.createNodeRadBut)
        self.radBoxSizer.Add(self.changeEdgeWeightRadBut)
        
        flags = wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL
                
        self.vbox.Add(self.radBoxSizer, 0, flag = wx.ALIGN_LEFT | wx.TOP)        
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.draw_figure()

    def clear_all_selections(self, event=None):
        for node in self.graph.node_list:
            node.state = 'unselected'
            for edge in node.edge_list:
                edge.state = 'unselected'
        self.draw_figure()
    def draw_figure(self):
        """ Redraws the figure
        """
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(True)
        
        for node in self.graph.node_list:
            node.draw(self.axes)
    
        xMin, xMax, yMin, yMax = self.axes.axis()
        if xMax - xMin < 2:
            xMin, xMax = -1, 1
        else:
            xMin, xMax = xMin + 0.2*(xMin-xMax)/2, xMax + 0.2*(xMax-xMin)/2

        if yMax - yMin < 2:
            yMin, yMax = -1, 1
        else:
            yMin, yMax = yMin + 0.2*(yMin-yMax)/2, yMax + 0.2*(yMax-yMin)/2
        
        self.axes.axis((xMin,xMax,yMin,yMax))
        
        self.canvas.draw()

    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
       
        #print self.graph.node_list
        clicked_node, = None,
        for node in self.graph.node_list:
            if node.artist == event.artist:
                clicked_node = node
        if self.selectStuffRadBut.GetValue():
            if event.mouseevent.button == 1:
                if clicked_node != None:
                    clicked_node.state = 'selected'
                    return self.draw_figure()
                else:
                    clicked_edge = None
                    for node in self.graph.node_list:
                        for edge in node.edge_list:
                            if edge.artist == event.artist:
                                if edge.state == 'selected':
                                    edge.state = 'unselected'
                                else:
                                    edge.state = 'selected'
        elif self.changeEdgeWeightRadBut.GetValue():
            clicked_edge = None
            for node in self.graph.node_list:
                for edge in node.edge_list:
                    if edge.artist == event.artist:
                        wx.CallAfter(self.change_edge_length,edge)
        elif self.createEdgeRadBut.GetValue():
            if any([node.state == 'selected' for node in self.graph.node_list]):
                for node in self.graph.node_list:
                    if node.state == 'selected':
                        new_edge = node.add_edge_to(clicked_node, 5)
                        node.state = 'unselected'
            else:
                clicked_node.state = 'selected'

    def on_click(self, event):
        if event.button == 3:
            self.clear_all_selections()
        if event.button == 1 and self.createNodeRadBut.GetValue():
            self.graph.add_node(Graph.Node(str(len(self.graph.node_list)), 
                                           event.xdata,event.ydata ))
        self.draw_figure()

    def change_edge_length(self,edge):
        new_length = wx.GetNumberFromUser(message="Enter a new weight for the edge",prompt = "weight:",min=0,max=1000000,parent=self,caption="get new weight box",value=0)
        if 0 <= new_length < 1000000: 
            edge.length = new_length
            self.draw_figure()
    def on_key(self, event):
        #print('you pressed', event.key, event.xdata, event.ydata)
        if event.key == 'delete':
            selected_nodes = [node for node in self.graph.node_list if node.state == 'selected']
            for selected_node in selected_nodes:
                self.graph.node_list.remove(selected_node)
                for node in self.graph.node_list:
                    for edge in node.edge_list[:]:
                        if edge.dest_node == selected_node:
                            node.edge_list.remove(edge)

            for node in self.graph.node_list:
                for edge in node.edge_list:
                    if edge.state == 'selected':
                        node.edge_list.remove(edge)
                        
            self.draw_figure()

class BarsFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Demo: wxPython with matplotlib'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.create_menu()
        self.create_status_bar()

        self.sizer = wx.BoxSizer()
        self.panel = wx.Panel(self)
        self.notebook = wx.Notebook(self.panel,style=wx.NB_TOP)

        self.graph_panels = []

        self.graph_panels.append(GraphPanel(self.notebook)) 

        for i, graph_panel in enumerate(self.graph_panels):
            self.notebook.AddPage(graph_panel,str(i))

        self.sizer.Add(self.notebook, 1, wx.EXPAND)

        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        m_load = menu_file.Append(-1, "&Load plot\tCtrl-L", "Load plot from file")
        m_close_page = menu_file.Append(-1, "&Close page\tCtrl-K", "Close currrent page")
        self.Bind(wx.EVT_MENU, self.on_close_page, m_close_page)
        menu_ops = wx.Menu()

        menu_ops_in_graph = wx.Menu()
        m_del_edges = menu_ops_in_graph.Append(-1, "Delete all edges", "Why would you want to do this?")

        self.Bind(wx.EVT_MENU, self.on_delete_edges, m_del_edges)
        menu_ops_new_graph = wx.Menu()

        menu_ops.AppendMenu(-1,"Within one graph",menu_ops_in_graph)
        menu_ops.AppendMenu(-1,"Outputting new graph",menu_ops_new_graph)

        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        self.Bind(wx.EVT_MENU, self.on_load_plot, m_load)

        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        
        menu_help = wx.Menu()
        m_about = menu_help.Append(-1, "&About\tF1", "About the demo")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_ops, "&Ops")
        self.menubar.Append(menu_help, "&Help")
        self.SetMenuBar(self.menubar)

    def on_close_page(self, event):
        graphToClose = self.notebook.GetCurrentPage().graph
        iGraphToClose = self.notebook.GetSelection()
        self.notebook.DeletePage(iGraphToClose)

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    
    def on_save_plot(self, event):
        file_choices = "GRAPH (*.graph)|*.graph"
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="graph.graph",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            filename = dlg.GetFilename()
            graphToSave = self.notebook.GetCurrentPage().graph
            index = self.notebook.GetSelection()
            self.notebook.SetPageText(index, filename)
            pickle.dump(graphToSave, open(path,"wb"))
            self.flash_status_message("Saved to %s" % path)


    def on_delete_edges(self, event):
        current_graph_page = self.notebook.GetCurrentPage()
        for node in current_graph_page.graph.node_list:
            node.edge_list = []
        current_graph_page.draw_figure()
                

    def on_load_plot(self, event):
        file_choices = "GRAPH (*.graph)|*.graph"
        dlg = wx.FileDialog(
            self, 
            message="Load a graph...",
            defaultDir=os.getcwd(),
            defaultFile="graph.graph",
            wildcard=file_choices,
            style=wx.OPEN)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            filename = dlg.GetFilename()
            with open(path, "rb") as f:
                new_graph_panel = GraphPanel(self.notebook)
                new_graph_panel.graph = pickle.load(f)
                self.notebook.AddPage(new_graph_panel,filename)
                self.graph_panels.append(new_graph_panel)
                new_graph_panel.draw_figure()
    
    def on_exit(self, event):
        self.Destroy()
        
    def on_about(self, event):
        msg = """ A demo using wxPython with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw!")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        dlg = wx.MessageDialog(self, msg, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = BarsFrame()
    app.frame.Show()
    app.MainLoop()

