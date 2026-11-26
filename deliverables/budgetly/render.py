from pathlib import Path
import math,json,subprocess,wave,re
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg
R=Path(__file__).resolve().parent
T=R.parent.parent/'.cache'/'budgetly-render';T.mkdir(parents=True,exist_ok=True)
F=imageio_ffmpeg.get_ffmpeg_exe()
WHITE='#f1f7f5';GREEN='#38edb1';MUTED='#a8c4bb'
DATA=[('01-personal',['فين مشاو','فلوسي؟'],[
('كتسالي الشهر وكتقول، فين مشاو فلوسي؟','dashboard','فلوسك، بوضوح'),
('وقف التخمين! بادجيتلي كيعاونك تشوف شحال دخل، شحال خرج، وشحال بقى.','monthcards','دخل • خرج • بقى'),
('الفكرة بسيطة بزاف!','cashflow','الصورة واضحة'),
('كتدخل للحساب، وكتضغط على نيو ترانزاكشن.','new','١. زيد عملية'),
('كتسجّل المدخول ولا المصروف، وكتختار الفئة والحساب.','monthly','٢. سجّل وصنّف'),
('مثلاً، دخلتي ألف وصرفتي ثلاثمية؟ بقاو سبعمية.','example','٣. شوف شحال بقى'),
('غير مثال باش تفهم!','example','مثال توضيحي'),
('من بعد، كتشوف الأرقام والرسوم قدّامك.','cashflow','تابع الأرقام'),
('حتى مصروفك الشخصي تقدر تنظمو بهاد الطريقة.','monthly','حتى فالميزانية الشخصية'),
('نتا كتسجّل العمليات، ما كاينش ربط بالبنك.','accounts','تسجيل يدوي'),
('دخل لبادجيتلي دوت أونلاين، وجرّب الديمو بلا حساب!','dashboard','جرّب الديمو بلا حساب')]),
('02-business',['كتبيع…','شحال كيبقى؟'],[
('كتبيع مزيان، ولكن شحال كيبقى ليك من بعد المصاريف؟','monthcards','شحال كيبقى؟'),
('المبيعات بوحدها ما كافياش!','income','ما تنساش المصاريف'),
('فبادجيتلي، سجّل المداخيل، والإشهار، والسلعة، والتوصيل.','monthbreakdown','سجّل كل تكلفة'),
('ما تنساش حتى المصاريف الصغيرة!','breakdown','الصغير حتى هو كيتجمع'),
('فميزانية الشهر، كتشوف شحال دخل وشحال خرج، وفين تصرفات الفلوس.','monthly','ميزانية الشهر'),
('حدّد شحال ناوي تصرف فكل فئة، وقارن الخطة مع المصروف الحقيقي.','plan','خطّط وقارن'),
('باش تعرف فين خاصك تراجع!','planactual','راجع المصاريف'),
('وفحسابات الأداء، كتتبع الفلوس اللي سجّلتي فوايز، بايبال، ولا البنك.','accounts','حسابات الأداء'),
('هادي تقديرات، ماشي ربط مباشر.','wise','تقديرات حسب تسجيلاتك'),
('وبحسب الباقة، كتخرج التقارير للمحاسب.','reports','تقارير حسب الباقة'),
('بغيتي تشوف كيفاش؟ جرّب ديمو بادجيتلي، والرابط فالبايو!','reports','جرّب الديمو')]),
('03-multi-business',['مشاريع بزاف،','صورة وحدة.'],[
('عندك متجر، وكالة، ولا قهوة؟','businesses','كل مشروع بوحدو'),
('وكتخلّط فلوسهم كاملين؟ هنا كيبدا الصداع!','all','حبس الخلط'),
('فبادجيتلي، كل مشروع عندو بلاصتو، بمداخيلو ومصاريفو بوحدهم.','businesscard','حسابات مفروقة'),
('ما تبقاش تجمع كلشي فحساب واحد!','businesses','تنظيم، ماشي تخمين'),
('كتفتح بيزنسز، كتزيد المشروع، وكتسجّل العمليات ديالو.','businesses','١. زيد المشروع'),
('كتبدّل بين المشاريع باش تشوف كل واحد بوحدو.','businesscard','٢. شوف كل مشروع'),
('وبغيتي الصورة كاملة؟','all','بغيتي المجموع؟'),
('صفحة أول بيزنسز كتجمع ليك الأرقام فبلاصة وحدة!','table','٣. شوف الصورة كاملة'),
('كل مشروع واضح، والمجموع واضح.','table','كلشي واضح'),
('وحتى التقارير كتختار فيها مشروع واحد ولا الجميع، حسب الباقة.','reports','تقارير حسب الباقة'),
('عدد المشاريع حتى هو حسب الباقة.','businesses','اختار الباقة المناسبة'),
('دخل لبادجيتلي دوت أونلاين، وجرّب الديمو بلا حساب.','all','جرّب الديمو بلا حساب'),
('نظّم فلوسك، وقرّر على بيّنة!','dashboard','قرّر على بيّنة')])]
SHOTS={'dashboard':(1,(305,70,1480,735)),'income':(1,(605,160,1185,320)),'cashflow':(1,(310,330,1085,730)),'breakdown':(1,(1090,330,1475,730)),'new':(1,(0,50,217,180)),'monthly':(4,(310,50,1480,695)),'monthcards':(4,(310,160,1090,300)),'monthbreakdown':(4,(310,310,695,690)),'plan':(5,(310,50,700,552)),'planactual':(4,(700,310,1088,690)),'accounts':(6,(310,50,1475,690)),'wise':(6,(313,145,1474,320)),'reports':(7,(310,55,1480,520)),'businesses':(3,(310,80,1470,665)),'businesscard':(3,(310,230,700,660)),'all':(2,(310,78,1480,735)),'table':(2,(310,375,1478,733))}
S={}
for i in range(1,9):
 im=Image.open(R/'sources'/f'image-{i}.png').convert('RGB');S[i]=im.resize((1568,round(im.height*1568/im.width)),Image.Resampling.LANCZOS)
def font(size,ar=False):
 f=ImageFont.truetype(str(R/'fonts'/('Arabic.ttf' if ar else 'Latin.ttf')),size)
 f.set_variation_by_axes([700,100] if ar else [700]);return f
def shape(t):return get_display(arabic_reshaper.reshape(t))
def text(d,t,y,size=49,color=WHITE,ar=True,x=540):
 t=shape(t) if ar else t;f=font(size,ar);b=d.textbbox((0,0),t,font=f)
 d.text((x-(b[2]-b[0])/2,y-b[1]),t,font=f,fill=color)
def wrap(t):
 f=font(49,True);lines=[];line=''
 for w in t.split():
  v=(line+' '+w).strip()
  if f.getlength(shape(v))>890 and line:lines.append(line);line=w
  else:line=v
 if line:lines.append(line)
 return lines
def background():
 im=Image.new('RGB',(1080,1920),'#0b2025');d=ImageDraw.Draw(im)
 for x in range(0,1080,90):d.line((x,0,x,1920),fill='#18363a')
 for y in range(0,1920,90):d.line((0,y,1080,y),fill='#18363a')
 return im

def crop_shot(im,shot,top,height):
 n,b=SHOTS[shot];c=S[n].crop(b);scale=min(912/c.width,height/c.height)
 c=c.resize((round(c.width*scale),round(c.height*scale)),Image.Resampling.LANCZOS)
 im.paste(c,((1080-c.width)//2,top+(height-c.height)//2))

def frame(titles,caption,shot,step,progress):
 im=background();d=ImageDraw.Draw(im)
 d.rounded_rectangle((66,76,126,136),radius=17,fill=GREEN)
 d.rounded_rectangle((82,94,112,118),radius=4,outline='#0b2025',width=3)
 d.text((145,82),'Budgetly',font=font(43),fill=WHITE)
 d.rounded_rectangle((748,86,1008,132),radius=23,fill='#193d3b');text(d,'DARIJA / DEMO',98,21,GREEN,False,878)
 text(d,titles[0],205,91);text(d,titles[1],340,100,GREEN)
 d.rounded_rectangle((64,480,1016,1140),radius=35,fill='#dbeae5')
 d.rounded_rectangle((65,481,1015,548),radius=30,fill='#23473f');text(d,step,497,27)
 if shot=='example':
  d.rounded_rectangle((84,560,996,1118),radius=22,fill='#102b2b')
  for y,num,label,col in [(590,'1,000','دخل',GREEN),(750,'− 300','خرج','#ff839c'),(910,'= 700','بقى',WHITE)]:
   text(d,num,y,106,col,False,485);text(d,label,y+24,40,col,True,862)
  text(d,'مثال توضيحي، ماشي نتيجة مضمونة',1070,28,MUTED)
 else:crop_shot(im,shot,560,550)
 d=ImageDraw.Draw(im);text(d,'صور من الحساب التجريبي • الأرقام للتوضيح',1175,26,MUTED)
 lines=wrap(caption);y=1260+(3-len(lines))*22
 for line in lines:text(d,line,y);y+=84
 d.rounded_rectangle((65,1513,1015,1598),radius=24,fill=GREEN)
 text(d,'budgetly.online/demo',1533,40,'#0b2025',False);text(d,'جرّب الديمو بلا حساب',1630,31)
 d.rounded_rectangle((70,1710,1010,1716),radius=3,fill='#2c4848')
 d.rounded_rectangle((70,1710,70+int(940*progress),1716),radius=3,fill=GREEN)
 return im

def cover(slug,titles,shot):
 im=background();d=ImageDraw.Draw(im)
 d.rounded_rectangle((380,270,700,345),radius=26,fill=GREEN);text(d,'Budgetly',284,43,'#0b2025',False)
 text(d,titles[0],420,96);text(d,titles[1],560,100,GREEN)
 d.rounded_rectangle((62,740,1018,1320),radius=34,fill='#e8f3ee');crop_shot(im,shot,765,530)
 d=ImageDraw.Draw(im);text(d,'صور من الحساب التجريبي',1355,29,MUTED)
 text(d,'جرّب الديمو بلا حساب',1430,48);text(d,'budgetly.online',1570,38,GREEN,False)
 im.save(R/'covers'/f'{slug}.jpg',quality=95)
def run(a):
 p=subprocess.run([F,'-hide_banner','-loglevel','error','-y']+list(map(str,a)),capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode()[-4000:])
def stamp(t):
 m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'

def render(idx):
 slug,title,phrases=DATA[idx];work=T/slug;work.mkdir(exist_ok=True)
 p=subprocess.run([F,'-v','error','-i',str(R/'audio'/f'{slug}.mp3'),'-f','f32le','-ac','1','-ar','48000','-'],capture_output=True,check=True)
 pcm=np.frombuffer(p.stdout,dtype=np.float32).copy();nf=math.ceil(len(pcm)/1600)
 pcm=np.pad(pcm,(0,nf*1600-len(pcm)+96000))
 weights=[len(re.sub(r'\s','',x[0])) for x in phrases]
 bounds=[round(nf*sum(weights[:k])/sum(weights)) for k in range(len(weights)+1)]
 scenes=[(*p,bounds[i+1]-bounds[i],bounds[i]/30) for i,p in enumerate(phrases)]
 scenes.append(('شوف كيفاش خدام، بلا حساب.','dashboard','جرّب الديمو دابا',60,nf/30))
 rng=np.random.default_rng(idx+2026);sfx=np.zeros(len(pcm),dtype=np.float32);subs=[]
 for i,(cap,shot,step,frames,start) in enumerate(scenes):
  frame(title,cap,shot,step,(i+1)/len(scenes)).save(work/f'{i}.png')
  vf=f"zoompan=z='1+0.025*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1080x1920:fps=30,format=yuv420p"
  run(['-i',work/f'{i}.png','-vf',vf,'-frames:v',frames,'-an','-c:v','libx264','-preset','ultrafast','-crf','23','-threads','2',work/f'{i}.mp4'])
  pos=round(start*48000);n=min(12000,len(pcm)-pos);t=np.arange(n)/48000
  sfx[pos:pos+n]+=(.035*rng.normal(size=n)*np.exp(-t*25)+.045*np.sin(2*np.pi*(650*t+900*t*t))*np.exp(-t*32)).astype(np.float32)
  subs.append(f'{i+1}\n{stamp(start)} --> {stamp(start+frames/30)}\n{cap}\n')
  print(slug,i+1,'/',len(scenes),flush=True)
 pos=nf*1600;n=min(36000,len(pcm)-pos);t=np.arange(n)/48000
 sfx[pos:pos+n]+=(.055*(np.sin(2*np.pi*880*t)+.5*np.sin(2*np.pi*1320*t))*np.exp(-t*6)).astype(np.float32)
 with wave.open(str(work/'mix.wav'),'wb') as out:
  out.setnchannels(1);out.setsampwidth(2);out.setframerate(48000);out.writeframes((np.clip(pcm*.88+sfx,-.98,.98)*32767).astype('<i2').tobytes())
 (work/'concat.txt').write_text('\n'.join(f"file '{work/f'{i}.mp4'}'" for i in range(len(scenes))))
 run(['-f','concat','-safe','0','-i',work/'concat.txt','-i',work/'mix.wav','-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','21','-threads','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',R/'reels'/f'{slug}.mp4'])
 run(['-i',R/'reels'/f'{slug}.mp4','-f','null','-'])
 (R/'reels'/f'{slug}.srt').write_text('\n'.join(subs))
 cover(slug,title,['dashboard','monthly','businesses'][idx])
 return {'file':slug+'.mp4','seconds':len(pcm)/48000,'decode_ok':True,'width':1080,'height':1920,'fps':30}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(render,range(3)))
 (R/'render-manifest.json').write_text(json.dumps(results,indent=2))
 (R/'NARRATION.md').write_text('# Approved Darija scripts\n\n'+'\n\n'.join('## '+s+'\n\n'+' '.join(x[0] for x in p) for s,t,p in DATA))
 print(json.dumps(results),flush=True)
