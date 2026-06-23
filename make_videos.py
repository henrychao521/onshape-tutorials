#!/usr/bin/env python3
# 建立每章教學影片：書中頁面截圖 + 文字說明字卡 + 美佳旁白 → MP4
import os, subprocess, json, textwrap
from PIL import Image, ImageDraw, ImageFont

A   = "/Volumes/128G/onshape-tutorials/assets"
OUT = "/Volumes/128G/onshape-tutorials"
W, H = 1280, 720
BG   = (11, 26, 43); GRID=(20,42,64); CYAN=(55,194,224); INK=(219,233,244); DIM=(127,166,196); AMBER=(245,185,72)
FH = "/System/Library/Fonts/STHeiti Medium.ttc"        # heading
FB = "/System/Library/Fonts/Hiragino Sans GB.ttc"      # body
def font(p,s): return ImageFont.truetype(p,s)

def base():
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    for x in range(0,W,42): d.line([(x,0),(x,H)],fill=GRID)
    for y in range(0,H,42): d.line([(0,y),(W,y)],fill=GRID)
    return img,d

def wrap_cjk(s,n):
    out=[]; line=""
    for ch in s:
        line+=ch
        if ch=="\n": out.append(line.rstrip("\n")); line=""
        elif len(line)>=n: out.append(line); line=""
    if line: out.append(line)
    return out

def title_card(ch, title, sub, path):
    img,d=base()
    d.line([(80,250),(140,250)],fill=CYAN,width=3)
    d.text((150,232),"ONSHAPE 教學重製 · 自動建模",font=font(FB,22),fill=CYAN)
    d.text((80,290),title,font=font(FH,72),fill=INK)
    d.text((80,400),sub,font=font(FH,38),fill=CYAN)
    d.text((80,560),"原書：趙珩宇《動手入門：3D 繪圖到機構製作》",font=font(FB,24),fill=DIM)
    d.text((80,600),"旁白：美佳 (zh-TW) · 字卡：Claude",font=font(FB,20),fill=DIM)
    d.rectangle([0,0,12,H],fill=CYAN)
    img.save(path)

def page_scene(label, page_img, head, body_lines, params, path):
    img,d=base()
    # left: book page
    pg=Image.open(page_img).convert("RGB")
    maxh=600; r=maxh/pg.height; pw=int(pg.width*r)
    pg=pg.resize((pw,maxh))
    px,py=70,60
    d.rectangle([px-3,py-3,px+pw+3,py+maxh+3],outline=CYAN,width=2)
    img.paste(pg,(px,py))
    d.text((px,py+maxh+12),"書中頁面截圖",font=font(FB,18),fill=DIM)
    # right column
    rx=px+pw+60
    d.text((rx,70),label,font=font(FB,24),fill=CYAN)
    d.line([(rx,108),(rx+70,108)],fill=AMBER,width=3)
    d.text((rx,128),head,font=font(FH,40),fill=INK)
    y=200
    for ln in body_lines:
        d.text((rx,y),ln,font=font(FB,27),fill=DIM); y+=42
    y+=14
    for p in params:
        d.ellipse([rx+1,y+13,rx+13,y+25],fill=CYAN)
        d.text((rx+26,y),p,font=font(FB,25),fill=CYAN); y+=40
    # bottom rec bar
    d.ellipse([rx,H-44,rx+14,H-30],fill=(255,107,107))
    d.text((rx+26,H-48),"旁白播放中",font=font(FB,20),fill=DIM)
    d.rectangle([0,0,12,H],fill=CYAN)
    img.save(path)

def dur(f):
    o=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",f])
    return float(json.loads(o)["format"]["duration"])

def say(text,path):
    subprocess.run(["say","-v","Meijia","-o",path,text],check=True)

def scene_clip(frame,audio,mp4,pad=0.6):
    d=dur(audio)+pad
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate","30","-i",frame,
        "-i",audio,"-c:v","libx264","-tune","stillimage","-pix_fmt","yuv420p","-r","30",
        "-t",f"{d:.2f}","-c:a","aac","-b:a","128k","-movflags","+faststart",mp4],check=True)

CHAPTERS=[
 dict(key="ch3", title="第 3 章 · 可愛小動物", sub="草圖 → 擠出 → 自由曲線",
   scenes=[
     dict(label="3-1 建立草圖", page=f"{A}/ch3a.png", head="開新草圖",
       body=["進入文件後，在「上視 (Top)」平面","上點選草圖，準備開始畫圖。"],
       params=["平面：Top","正視於：按 n 轉正"],
       narr="第三章，我們要做一隻可愛的小動物。第一步，在上視平面上開一個新草圖，準備畫圖。"),
     dict(label="3-2 擠出", page=f"{A}/ch3b.png", head="畫正方形再擠出",
       body=["用中心點矩形吸附到正中心，","鍵盤輸入邊長，再擠出成立方體。"],
       params=["矩形：50 × 50 mm","擠出深度：50 mm"],
       narr="用中心點矩形，吸附到正中心，鍵盤輸入邊長五十乘五十，再用擠出長出五十毫米，就得到立方體的身體。"),
     dict(label="3-3 草圖曲線", page=f"{A}/ch3c.png", head="自由曲線畫耳朵",
       body=["在頂面用不規則曲線，點出","封閉造型，擠出後就是耳朵。"],
       params=["工具：不規則曲線 (spline)","耳朵擠出：+20 mm"],
       narr="接著在頂面，用不規則曲線點出封閉的耳朵造型，擠出之後，可愛的小動物就完成了。"),
   ]),
 dict(key="ch4", title="第 4 章 · 馬克杯", sub="圓 → 擠出 → 薄殼挖空",
   scenes=[
     dict(label="4-1 平口馬克杯", page=f"{A}/ch4a.png", head="畫圓擠出成杯身",
       body=["在平面畫一個圓，擠出成","圓柱，作為杯子的本體。"],
       params=["圓：Ø70 mm","擠出：80 mm"],
       narr="第四章做馬克杯。先在平面上畫一個直徑七十毫米的圓，擠出八十毫米，變成圓柱杯身。"),
     dict(label="薄殼挖空", page=f"{A}/ch4b.png", head="薄殼變中空杯",
       body=["用薄殼移除頂面，留下杯壁，","杯子就被挖空了。"],
       params=["移除：頂面","杯壁厚：4 mm"],
       narr="再用薄殼，把頂面移除、留下四毫米的杯壁，杯子就被挖空，變成真正的馬克杯了。"),
   ]),
 dict(key="ch5", title="第 5 章 · 工程物件", sub="TT 馬達 · 依實際尺寸建模",
   scenes=[
     dict(label="5-2 TT 直流減速馬達", page=f"{A}/ch5a.png", head="上網查實際規格",
       body=["TT 馬達尺寸藏在圖片裡，","我上網查到了真實數據。"],
       params=["來源：Adafruit / Handson 資料表","軸徑：Ø5.3 mm"],
       narr="第五章是工程物件。書中馬達的精確尺寸藏在圖片裡，所以我上網查到了 TT 直流減速馬達的真實規格。"),
     dict(label="建立工程件", page=f"{A}/ch5b.png", head="齒輪箱＋馬達圓",
       body=["畫矩形擠出齒輪箱，再加上","馬達的圓，就是工程件雛形。"],
       params=["齒輪箱：70 × 22 × 19 mm","頂面馬達圓：Ø18 mm"],
       narr="齒輪箱本體是七十乘二十二乘十九毫米，畫矩形擠出，再在頂面加上馬達的圓，工程件的雛形就出來了。"),
   ]),
]

made=[]
for ch in CHAPTERS:
    clips=[]
    # title card
    tf=f"{A}/{ch['key']}_title.png"; title_card(ch['key'],ch['title'],ch['sub'],tf)
    ta=f"{A}/{ch['key']}_title.aiff"; say(ch['title'].replace('·','')+"。"+ch['sub'].replace('→','，'),ta)
    tc=f"{A}/{ch['key']}_s0.mp4"; scene_clip(tf,ta,tc,pad=0.4); clips.append(tc)
    # scenes
    for i,s in enumerate(ch['scenes'],1):
        fr=f"{A}/{ch['key']}_s{i}.png"
        page_scene(s['label'],s['page'],s['head'],s['body'],s['params'],fr)
        au=f"{A}/{ch['key']}_s{i}.aiff"; say(s['narr'],au)
        cl=f"{A}/{ch['key']}_s{i}.mp4"; scene_clip(fr,au,cl); clips.append(cl)
    # concat (re-encode for safe joins)
    lst=f"{A}/{ch['key']}_list.txt"
    open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
    final=f"{OUT}/{ch['key']}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","128k",
        "-movflags","+faststart",final],check=True)
    # poster = title card
    Image.open(tf).save(f"{OUT}/{ch['key']}_poster.jpg",quality=88)
    made.append((final,round(dur(final),1)))

for f,d in made: print(f"OK {f}  {d}s")
