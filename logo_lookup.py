import urllib.request,json,re
for id in ['30th','30th-c']:
 d=json.load(urllib.request.urlopen('https://api.tcgdex.net/v2/en/sets/'+id));print(id,{k:v for k,v in d.items() if k!='cards'});print('sample',d['cards'][:3])
u='https://www.pokemon.com/us/news/the-pokemon-tcg-30th-celebration-expansion-is-available-now'
h=urllib.request.urlopen(u).read().decode();print('images',re.findall(r'(?:src|content)=[\"\x27]([^\"\x27]+(?:png|jpg|webp)[^\"\x27]*)',h)[:30])
