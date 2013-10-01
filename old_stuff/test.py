import sys#,subprocess

tags = {'super': 'purple',
        'awesome': 'red',
        'color': 'blue',
        'text': 'orange',}

f = open ("Coder.py","r")
coder_code = f.read()
f.close()

code = 'asdf'
sys.argv = [code]
exec compile(coder_code,'"text"','exec')
print 'returned '+code
sys.argv = [code]
exec compile(coder_code,'"text"','exec')
print 'returned '+code