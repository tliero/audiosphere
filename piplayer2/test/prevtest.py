import subprocess

out, err = subprocess.Popen(['mocp','--info'], stdout=subprocess.PIPE).communicate()
out = out.splitlines()

#ls = subprocess.Popen(['mocp','--info'], stdout=subprocess.PIPE)
#out = ls.stdout.readlines()

for s in out:
    s = s.decode("utf-8")
    if s.startswith('CurrentSec'):
        print(s)
        print(s.rfind(' '))
        print(s[s.rfind(' ')+1:])
        sec = s[s.rfind(' ')+1:]
        print(int(sec) > 10)
