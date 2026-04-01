import pygame
import sys
import os
import json
import math
import random
from datetime import datetime, timedelta
from tkinter import filedialog, Tk

pygame.init()

# شاشة
WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Diary Ultra 🎨")
clock = pygame.time.Clock()

# Grid
ROWS, COLS = 25, 25
PIXEL = 20
GRID_W = COLS * PIXEL
GRID_H = ROWS * PIXEL
offset_x = (WIDTH - GRID_W)//2 - 150
offset_y = (HEIGHT - GRID_H)//2

# التاريخ
current_date = datetime.now()
def file_name():
    return current_date.strftime("%Y-%m-%d") + ".json"

# Grid
def new_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]
grid = new_grid()

# 🎨 Palette
def palette_gen():
    base = random.randint(0,255)
    return [((base+i*40)%255,(base+i*80)%255,(base+i*120)%255) for i in range(6)]
palette = palette_gen()
current_color = palette[0]

# Brushes
brush_type = "square"

# 🧠 Ideas
ideas = ["Mood","Food","Dream","Nature","Memory","Abstract"]
def get_idea():
    return "Idea: " + ideas[datetime.now().day % len(ideas)]

# Load / Save
def load():
    global grid
    if os.path.exists(file_name()):
        with open(file_name(),"r") as f:
            grid = json.load(f)
    else:
        grid = new_grid()

def save():
    with open(file_name(),"w") as f:
        json.dump(grid,f)

# 🎨 Gradient
def gradient(r,c):
    radius = 3
    for i in range(-radius,radius+1):
        for j in range(-radius,radius+1):
            nr,nc = r+i,c+j
            if 0<=nr<ROWS and 0<=nc<COLS:
                dist = math.sqrt(i*i+j*j)
                if dist<=radius:
                    f = 1 - dist/radius
                    grid[nr][nc] = (
                        int(current_color[0]*f+30),
                        int(current_color[1]*f+30),
                        int(current_color[2]*f+30)
                    )

# Paint
def paint(r,c):
    if brush_type=="square":
        grid[r][c] = current_color
    elif brush_type=="circle":
        radius = 1
        for i in range(-radius,radius+1):
            for j in range(-radius,radius+1):
                if 0<=r+i<ROWS and 0<=c+j<COLS:
                    if i*i + j*j <= radius*radius:
                        grid[r+i][c+j] = current_color
    elif brush_type=="glow":
        for i in range(-2,3):
            for j in range(-2,3):
                if 0<=r+i<ROWS and 0<=c+j<COLS:
                    grid[r+i][c+j]=(
                        min(255,current_color[0]+40),
                        min(255,current_color[1]+40),
                        min(255,current_color[2]+40)
                    )
    elif brush_type=="gradient":
        gradient(r,c)

# 🖼️ Export PNG
def export_png(date_str, path=None):
    surf = pygame.Surface((GRID_W,GRID_H))
    file = date_str + ".json"
    if not os.path.exists(file):
        return
    with open(file,"r") as f:
        data = json.load(f)
    for r in range(ROWS):
        for c in range(COLS):
            col = data[r][c] if data[r][c] else (0,0,0)
            pygame.draw.rect(surf,col,(c*PIXEL,r*PIXEL,PIXEL,PIXEL))
    if path:
        pygame.image.save(surf, path)
    else:
        pygame.image.save(surf,date_str+".png")

# Draw palette
def draw_palette():
    for i,col in enumerate(palette):
        x = WIDTH - 120
        y = 250 + i*60
        rect = pygame.Rect(x,y,40,40)
        pygame.draw.rect(screen,col,rect,border_radius=8)
        if col == current_color:
            pygame.draw.rect(screen,(255,255,255),rect,3)

# Calendar
def calendar():
    global current_date
    run=True
    font=pygame.font.SysFont("arial",20)
    while run:
        screen.fill((18,20,25))
        for d in range(1,31):
            date_str = current_date.strftime("%Y-%m-") + str(d).zfill(2)
            has_data = os.path.exists(date_str + ".json")
            x=150+(d%7)*90
            y=120+(d//7)*70
            rect=pygame.Rect(x,y,60,40)
            color = (80,160,255) if has_data else (60,60,80)
            pygame.draw.rect(screen,color,rect,border_radius=8)
            txt=font.render(str(d),True,(255,255,255))
            screen.blit(txt,(x+20,y+10))
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                for d in range(1,31):
                    x=150+(d%7)*90
                    y=120+(d//7)*70
                    rect=pygame.Rect(x,y,60,40)
                    if rect.collidepoint(e.pos):
                        current_date=current_date.replace(day=d)
                        load()
                        return
        pygame.display.flip()

# Gallery
def gallery():
    run=True
    font=pygame.font.SysFont("arial",18)
    files = [f.replace(".json","") for f in os.listdir() if f.endswith(".json")]
    while run:
        screen.fill((20,22,28))
        for i, date_str in enumerate(files):
            x = 100 + (i%5)*180
            y = 100 + (i//5)*150
            export_png(date_str)
            img = pygame.image.load(date_str+".png")
            img = pygame.transform.scale(img,(120,120))
            screen.blit(img,(x,y))
            txt = font.render(date_str,True,(200,200,200))
            screen.blit(txt,(x,y+125))
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE:
                    return
        pygame.display.flip()

# AI draw suggestion
def ai_draw():
    # فقط يرسم ألوان عشوائية في الشبكة كنموذج
    for _ in range(30):
        r=random.randint(0,ROWS-1)
        c=random.randint(0,COLS-1)
        paint(r,c)

# Save dialog
def save_image_dialog():
    Tk().withdraw()
    path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")])
    if path:
        export_png(current_date.strftime("%Y-%m-%d"), path)

# Draw everything
def draw():
    screen.fill((20,22,28))
    for r in range(ROWS):
        for c in range(COLS):
            x=offset_x+c*PIXEL
            y=offset_y+r*PIXEL
            if grid[r][c]:
                pygame.draw.rect(screen,grid[r][c],(x,y,PIXEL,PIXEL))
            pygame.draw.rect(screen,(50,50,50),(x,y,PIXEL,PIXEL),1)
    draw_palette()
    font=pygame.font.SysFont("arial",18)
    screen.blit(font.render(current_date.strftime("%Y-%m-%d"),True,(200,200,200)),(WIDTH-250,30))
    screen.blit(font.render(get_idea(),True,(170,170,170)),(WIDTH-300,70))
    screen.blit(font.render("C Calendar",True,(200,200,200)),(WIDTH-250,120))
    screen.blit(font.render("G Gallery",True,(200,200,200)),(WIDTH-250,150))
    screen.blit(font.render("A AI Draw",True,(200,200,200)),(WIDTH-250,180))
    screen.blit(font.render("S Save PNG",True,(200,200,200)),(WIDTH-250,210))
    screen.blit(font.render(f"Brush: {brush_type}", True, (180,180,180)), (700,50))

# تشغيل
load()
running=True
while running:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            save()
            running=False

        if pygame.mouse.get_pressed()[0]:
            x,y=pygame.mouse.get_pos()
            if offset_x<=x<=offset_x+GRID_W and offset_y<=y<=offset_y+GRID_H:
                c=(x-offset_x)//PIXEL
                r=(y-offset_y)//PIXEL
                paint(r,c)

        if e.type==pygame.MOUSEBUTTONDOWN:
            x,y=e.pos
            for i,col in enumerate(palette):
                rect=pygame.Rect(WIDTH-120,250+i*60,40,40)
                if rect.collidepoint(x,y):
                    current_color=col

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_c: calendar()
            if e.key==pygame.K_g: gallery()
            if e.key==pygame.K_a: ai_draw()
            if e.key==pygame.K_s: save_image_dialog()
            if e.key==pygame.K_RIGHT:
                save(); current_date+=timedelta(days=1); load()
            if e.key==pygame.K_LEFT:
                save(); current_date-=timedelta(days=1); load()

            # ← Brush select
            if e.key == pygame.K_1:
                brush_type = "square"
            if e.key == pygame.K_2:
                brush_type = "circle"
            if e.key == pygame.K_3:
                brush_type = "glow"
            if e.key == pygame.K_4:
                brush_type = "gradient"

    draw()
    pygame.display.flip()

pygame.quit()
sys.exit()