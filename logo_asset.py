import urllib.request,re
u='https://www.pokeos.com/tcg/eng/mega/580'
h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read().decode()
for m in re.finditer(r'.{0,200}(?:logo|Logo).{0,200}',h):
 t=m.group(0)
 if '<img' in t or 'src=' in t: print(t[:500])
