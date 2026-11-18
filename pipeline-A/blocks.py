# blocks.py -- show the good (G) and bad (.) blocks of 7x8 arrays.  usage: python3 blocks.py ARRAY ...
import sys
for s in sys.argv[1:]:
    g=[[int(c) for c in r] for r in s.split('/')]
    rows=[]
    ng=0
    for i in range(6):
        row=''
        for j in range(7):
            a,b,c,d=g[i][j],g[i][j+1],g[i+1][j],g[i+1][j+1]
            gd=(a==d) or (b==c)
            ng+=gd; row+='G' if gd else '.'
        rows.append(row)
    print(s,'good blocks',ng); print('\n'.join(rows))
