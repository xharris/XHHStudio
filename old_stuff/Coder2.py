from Tkinter import *
import sys

code = sys.argv[0]
root = None
coder = None

class Coder(Text):
    def __init__(self, root):
        Text.__init__(self, root)
        self.tags = tags
        self.config_tags()
        self.bind('<Key>', self.key_press)

        self.insert(INSERT, sys.argv[0])
        global code
        code = self.get('0.0',END)

    def config_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)

    def key_press(self, key):
        cline = self.index(INSERT).split('.')[0]
        lastcol = 0
        char = self.get('%s.%d'%(cline, lastcol))
        while char != '\n':
            lastcol += 1
            char = self.get('%s.%d'%(cline, lastcol))

        buffer = self.get('%s.%d'%(cline,0),'%s.%d'%(cline,lastcol))
        tokenized = buffer.split(' ')

        self.remove_tags('%s.%d'%(cline, 0), '%s.%d'%(cline, lastcol))

        start, end = 0, 0
        for token in tokenized:
            end = start + len(token)
            if token in tags:
                self.tag_add(token, '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            else:
                for index in range(len(token)):
                    try:
                        int(token[index])
                    except ValueError:
                        pass
                    else:
                        self.tag_add('int', '%s.%d'%(cline, start+index))

            start += len(token)+1


def onClose():
    global code
    code = coder.get('0.0',END)
    root.destroy()


if __name__ == '__main__':
    global coder,root
    root = Tk()
    coder = Coder(root)
    coder.pack(expand=1,fill='both')
    root.iconbitmap("DATA\\icon.ico")
    root.title("CODE :: object_test")
    root.protocol('WM_DELETE_WINDOW', onClose)
    root.mainloop()



