import wx
from wx import stc
import keyword

    
done = False
text = ''
oldtext = ''
inited = False
first_text = ''

class PyDialog(wx.Frame):
    def onClose(self,evt):
        global text,done,oldtext
        if not oldtext == self.stc.GetText():
            box = wx.MessageDialog(None, 'Save before closing?','Are you sure?', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            result = box.ShowModal()
            if result == wx.ID_YES:
                text = self.stc.GetText()
                box.Destroy()
                done = True
                self.closeProgram()
            elif result == wx.ID_NO:
                box.Destroy()
                done = True
                self.closeProgram()
        else:
            done = True
            self.closeProgram()

    def closeProgram(self):
        self.Destroy()

    def __init__(self,txt='',title='Code',size=(700,300),pos=None):
        wx.Frame.__init__(self, None, wx.ID_ANY|wx.STAY_ON_TOP,title,size=size,pos=pos)


        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.text = txt

        self.stc = stc.StyledTextCtrl(self, -1)
        self.stc.ZoomIn()

        #self.sizer.Add(self.stc,0,wx.EXPAND)
        self.stc.SetSizeHints(400, 400)
        self.stc.SetLexer(stc.STC_LEX_LUA)
        self.stc.SetKeyWords(0, " ".join(keyword.kwlist))
        self.stc.SetMarginType(1, stc.STC_MARGIN_NUMBER)

        #self.SetSizer(self.sizer)
        

        self.Bind(wx.EVT_CLOSE, self.onClose)   #not working for some weird reason
		
		# missing 
		#LITERALSTRING
		#STRINGEOL

        highlights = [[wx.stc.STC_LUA_DEFAULT, 'fore:#000000'],
        			  [wx.stc.STC_LUA_PREPROCESSOR, 'fore:#008000,back:#F0FFF0'],
        			  [wx.stc.STC_LUA_STRING, 'fore:#800080'],						
        			  [wx.stc.STC_LUA_CHARACTER, 'fore:#800080'],					
        			  [wx.stc.STC_LUA_NUMBER, 'fore:#008080'],						
        			  [wx.stc.STC_LUA_OPERATOR, 'fore:#800000,bold'],				
        			  [wx.stc.STC_LUA_COMMENT,  'fore:#008000,back:#F0FFF0'],		
        			  [wx.stc.STC_LUA_COMMENTDOC, 'fore:#008000,back:#F0FFF0'],
					  [wx.stc.STC_LUA_COMMENTLINE, 'fore:#008000,back:#F0FFF0'],
					  [wx.stc.STC_LUA_IDENTIFIER, 'fore:#000000'],

					  [wx.stc.STC_LUA_WORD, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD2, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD3, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD4, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD5, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD6, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD7, 'fore:#000080,bold'],
					  [wx.stc.STC_LUA_WORD8, 'fore:#000080,bold']	
					  ]	

       	for i in range(len(highlights)):
       		self.stc.StyleSetSpec(highlights[i][0],highlights[i][1])

        # Caret color
        self.stc.SetCaretForeground("GREEN")
        # Selection background
        self.stc.SetSelBackground(1, '#66CCFF')

        '''
        sizer.Add(self.stc, 0, wx.EXPAND)

        button = wx.Button(self, -1, 'Save and Close')
        self.Bind(wx.EVT_BUTTON, self.SaveClose, button)
        sizer.Add(button)

        self.SetSizer(sizer)
        sizer.Fit(self)
        '''


def showTextEdit(txt='',title='',size=None,pos=None):
    global text,done,oldtext
    text = txt
    oldtext = txt
    app = wx.App()
    dlg = PyDialog(txt,title,size,pos)
    dlg.Show()
    dlg.stc.SetText(txt)
    app.MainLoop()
    app.ExitMainLoop()
    if done:
        return text
        done = False
