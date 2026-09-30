import sys, subprocess
from pathlib import Path
sys.path.insert(0,'work/media')
import imageio_ffmpeg
from PIL import Image,ImageDraw
ff=imageio_ffmpeg.get_ffmpeg_exe()
p=Path('work/reference');p.mkdir(exist_ok=True)
r=subprocess.run([ff,'-i',r'C:\Users\leann\Downloads\Recording 2026-09-30 215046.mp4','-vf','fps=1/15,scale=640:-1','-frames:v','12',str(p/'frame%02d.jpg')],capture_output=True,text=True)
print(r.stderr[-2000:])
files=list(p.glob('frame*.jpg')); ims=[Image.open(x) for x in files]
out=Image.new('RGB',(1280,((len(ims)+1)//2)*380),'#222222')
for i,im in enumerate(ims):
 im.thumbnail((640,350));out.paste(im,((i%2)*640,(i//2)*380));ImageDraw.Draw(out).text(((i%2)*640+10,(i//2)*380+350),str(i*15)+' seconds',fill='white')
out.save(p/'contact.jpg')
