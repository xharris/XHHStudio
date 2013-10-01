from Tkinter import *

#global root,coder,code

code = sys.argv[0]
root = Tk()
coder = Text(root)
coder.insert(END,code)

def config_tags():
    for tag, val in tags.items():
        coder.tag_config(tag, foreground=val)

def remove_tags(start, end):
    for tag in tags.keys():
        coder.tag_remove(tag, start, end)

def key_press(key):
    cline = coder.index(INSERT).split('.')[0]
    lastcol = 0
    char = coder.get('%s.%d'%(cline, lastcol))
    while char != '\n':
        lastcol += 1
        char = coder.get('%s.%d'%(cline, lastcol))

    buffer = coder.get('%s.%d'%(cline,0),'%s.%d'%(cline,lastcol))
    tokenized = buffer.split(' ')

    remove_tags('%s.%d'%(cline, 0), '%s.%d'%(cline, lastcol))

    start, end = 0, 0
    for token in tokenized:
        end = start + len(token)
        if token in tags:
            coder.tag_add(token, '%s.%d'%(cline, start), '%s.%d'%(cline, end))
        else:
            for index in range(len(token)):
                try:
                    int(token[index])
                except ValueError:
                    pass
                else:
                    coder.tag_add('int', '%s.%d'%(cline, start+index))

        start += len(token)+1

def onClose():
    global code
    code = coder.get('0.0',END)
    root.destroy()

config_tags()
coder.bind('<Key>', key_press)

root.iconbitmap("DATA\\icon.ico")
root.title("CODE :: object_test")
root.protocol('WM_DELETE_WINDOW', onClose)

coder.pack()
root.mainloop()