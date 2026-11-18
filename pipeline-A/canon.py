# canonical form of a 7x8 Dominosa array under the 4 rectangle symmetries and relabelling
# usage: python3 canon.py < lines whose last field is an array
import sys
def canon(s):
    g=[[int(ch) for ch in row] for row in s.strip().split('/')]
    best=None
    for fr in (False,True):
        for fc in (False,True):
            h=[row[::-1] if fc else row[:] for row in (g[::-1] if fr else g)]
            flat=[x for row in h for x in row]; m={}
            out=[]
            for x in flat:
                if x not in m: m[x]=len(m)
                out.append(m[x])
            t='/'.join(''.join(str(x) for x in out[r*8:r*8+8]) for r in range(7))
            if best is None or t<best: best=t
    return best
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split()
        if p: print(' '.join(p[:-1]),canon(p[-1]))
