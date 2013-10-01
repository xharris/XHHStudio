# WX Dialog
import wx

vals = None
txt = []
txt_title = ''

class wxSimpleInput(wx.Frame):
    def __init__(self,root):
        wx.Frame.__init__(self,None,title=txt_title,style=wx.CAPTION) # (self, None, wx.ID_ANY|wx.STAY_ON_TOP, title=txt_title)
        self.panel = wx.Panel(self) # (self, wx.ID_ANY)
        self.root = root

        self.elements = {}
        btns = {}

        btn = ['OK']#,'Cancel']

        topSizer = wx.BoxSizer(wx.VERTICAL)
        for index,i in enumerate(txt):
            t = []
            if i[0] == 'string': # label text, default value
                self.elements[index] = [wx.StaticText(self.panel, wx.ID_ANY, i[1]),
                               wx.TextCtrl(self.panel, wx.ID_ANY,str(i[2])),
                               wx.BoxSizer(wx.HORIZONTAL)
                               ]
                self.elements[index][1].SetValue(i[2])
            if i[0] == 'checkbox': # label text, default value
                self.elements[index] = [wx.StaticText(self.panel, wx.ID_ANY, i[1]),
                               wx.CheckBox(self.panel, -1,'', (10, 10)),
                               wx.BoxSizer(wx.HORIZONTAL)
                               ]
                self.elements[index][1].SetValue(bool(i[2]))
            if i[0] == 'int': # label text, default value, min, max
                self.elements[index] = [wx.StaticText(self.panel, wx.ID_ANY, i[1]),
                               wx.SpinCtrl(self.panel, -1, '',(150, 75), (60, -1)),
                               wx.BoxSizer(wx.HORIZONTAL)
                               ]
                if len(i)>3:
                    self.elements[index][1].SetRange(i[3],i[4])

                self.elements[index][1].SetValue(int(i[2]))

            if i[0] == 'file': # label text, default directory, wildcard
                self.elements[index] = [wx.StaticText(self.panel,wx.ID_ANY,i[1]),
                                #wx.Button
                                wx.BoxSizer(wx.HORIZONTAL)]

            if i[0] == 'image': # file, resize
                self.elements[index] = [None,
                                        wx.StaticBitmap(self.panel, wx.ID_ANY,wx.BitmapFromImage(wx.Image(i[1], wx.BITMAP_TYPE_ANY))),
                                        wx.BoxSizer(wx.HORIZONTAL)
                                        ]

            t = self.elements[index]
            if t[0] != None:
                self.elements[index][2].Add(t[0],0,wx.ALL,5)
            self.elements[index][2].Add(t[1],1,wx.ALL|wx.EXPAND,5)
            topSizer.Add(self.elements[index][2], 0, wx.ALL|wx.EXPAND, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(len(btn)):
            btns[i] = wx.Button(self.panel,wx.ID_ANY,btn[i])
            btnSizer.Add(btns[i],0,wx.ALL,5)
            eval('setattr(self,"self.on'+btn[i]+'",self.on'+btn[i]+')')
            eval('self.Bind(wx.EVT_BUTTON,self.on'+btn[i]+',btns[i])')

        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

    def onOK(self, event):

        values = []
        good = 0
        for index,i in enumerate(txt):
            if i[0] == 'string' or i[0] == 'checkbox' or i[0] == 'int':
                values.append(self.elements[index][1].GetValue())
        for v in values:
            if v == None:
                values = [0,0,0,0] # change to be more VARIABLE
            else:
                good += 1
        if good == len(values):
            global vals
            vals = values
            self.closeProgram()
        else:
            good = 0

    def closeProgram(self):
        #return vals
        self.Destroy()


def showDialog(title,texts):
    global txt,txt_title
    txt_title = title
    txt = texts
    app = wx.App()
    frame = wxSimpleInput(app).Show()
    app.MainLoop()
    app.ExitMainLoop()
    if not vals == None: return vals

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def resetRunOnce():
    loadFile.has_run = False

@run_once
def loadFile(DEFAULT_DIR=None,WILDCARD=''):
    global loading
    wc = str(WILDCARD)
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = None
    if DEFAULT_DIR != None: dialog = wx.FileDialog(None,'Open',defaultDir=DEFAULT_DIR, wildcard=wc, style=style)
    else: dialog = wx.FileDialog(None,'Open', wildcard=wc, style=style)
    app.MainLoop()
    app.ExitMainLoop()
    path = '-'
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = 'No'
    if len(path) > 2:
        f = path
        return str(f)
        dialog.Destroy()