from OpenGL.GL import*
from OpenGL.GLU import*
from OpenGL.GLUT import*
import math
import random

width=800;height=500
GROUND=410          # chhader mejhe
POT=24              # tub er height

# ---------- animation state ----------
is_playing=True
speed=1.0
girl_x=40;girl_dir=1;girl_walk=0
mode='walk'         # 'walk' -> 'water' -> 'done'
target=0
timer=0
drops=[]
plants=[[x,0.3] for x in (200,330,460,590,720)]   # [x, growth]
clouds=[(120,60),(480,90),(640,45)]


# ---------- drawing helpers ----------
def color(h):
    h=h.lstrip('#')
    glColor3f(int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255)

def lighten(h,a):
    h=h.lstrip('#')
    v=[int(int(h[i:i+2],16)+(255-int(h[i:i+2],16))*a) for i in (0,2,4)]
    return '#%02x%02x%02x'%tuple(v)

def circle(cx,cy,r,c):
    color(c)
    r=max(r,0.5)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx,cy)
    for i in range(41):
        angle=2*math.pi*i/40
        glVertex2f(r*math.cos(angle)+cx,r*math.sin(angle)+cy)
    glEnd()

def rect(x,y,w,h,c):
    color(c)
    glBegin(GL_QUADS)
    glVertex2f(x,y);glVertex2f(x+w,y);glVertex2f(x+w,y+h);glVertex2f(x,y+h)
    glEnd()

def poly(points,c):
    color(c)
    glBegin(GL_POLYGON)
    for p in points:
        glVertex2f(p[0],p[1])
    glEnd()

def line(x1,y1,x2,y2,c,w=1):
    color(c)
    glLineWidth(w)
    glBegin(GL_LINES)
    glVertex2f(x1,y1);glVertex2f(x2,y2)
    glEnd()

def polyline(points,c,w=1):
    color(c)
    glLineWidth(w)
    glBegin(GL_LINE_STRIP)
    for p in points:
        glVertex2f(p[0],p[1])
    glEnd()

def bezier(p0,p1,p2,c,w=1):
    pts=[]
    for i in range(13):
        t=i/12
        x=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0]
        y=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]
        pts.append((x,y))
    polyline(pts,c,w)


# ---------- 5 rokom rooftop gach (g = 0.3 theke 1) ----------
def rose(x,y,g):
    for c in [(-12,-10,9),(12,-10,9),(0,-22,11),(0,-8,10)]:
        circle(x+c[0]*g,y+c[1]*g,c[2]*g+2,'#2f9e57')
    circle(x-3*g,y-26*g,6*g,'#48b96d')
    if g>0.9:
        for f in [(-10,-20),(8,-28),(14,-12),(-2,-32)]:
            circle(x+f[0],y+f[1],4,'#ff5d8f')

def palm(x,y,g):
    L=10+22*g
    top=(x+4,y-(10+45*g))
    bezier((x,y),(x+6,y-20*g),top,'#8a6a43',4)
    for a in [-2.9,-2.3,-1.57,-0.84,-0.25]:
        ctrl=(top[0]+math.cos(a)*L*0.6,top[1]+math.sin(a)*L*0.6-8)
        end=(top[0]+math.cos(a)*L,top[1]+math.sin(a)*L+6)
        bezier(top,ctrl,end,'#2f9e57',3)

def marigold(x,y,g):
    for c in [(-10,-6),(10,-6),(0,-10)]:
        circle(x+c[0]*g,y+c[1]*g,6*g+3,'#3aa860')
    fl=[(-12,-18),(0,-24),(12,-18),(-6,-12),(7,-13)]
    n=0 if g<0.5 else math.ceil((g-0.4)*8)
    for f in fl[:n]:
        circle(x+f[0]*g,y+f[1]*g,5*g+1,'#ffb300')
        circle(x+f[0]*g,y+f[1]*g,2,'#e65100')

def tomato(x,y,g):
    line(x,y,x,y-(12+42*g),'#3b8f4f',3)
    for j in range(4):
        yy=y-(8+11*j)*g
        circle(x-8*g,yy,5+3*g,'#2f9e57')
        circle(x+8*g,yy-4*g,5+3*g,'#48b96d')
    if g>0.95:
        for f in [(-9,-26),(9,-38),(-7,-44)]:
            circle(x+f[0],y+f[1],4.5,'#e8392f')

def tulsi(x,y,g):
    for c in [(-8,-8,8),(8,-8,8),(0,-16,10),(-4,-24,7),(5,-24,7)]:
        circle(x+c[0]*g,y+c[1]*g,c[2]*g+1.5,'#1f7a45')
    if g>0.9:
        for f in [(-4,-30),(5,-29),(0,-22)]:
            circle(x+f[0],y+f[1],2.5,'#9b6bd6')

kinds=[rose,palm,marigold,tomato,tulsi]

def draw_plant(i):
    x,g=plants[i]
    py=GROUND-POT
    kinds[i%len(kinds)](x,py,g)
    poly([(x-18,py),(x+18,py),(x+13,GROUND),(x-13,GROUND)],'#c4623a')   # tub
    rect(x-21,py-4,42,7,'#a84e2c')
    rect(x-17,py-5,34,3,'#4b3321')                                     # mati


# ---------- meye ----------
def draw_girl():
    watering=(mode=='water')
    sw=math.sin(girl_walk)*12 if mode=='walk' else 0
    glPushMatrix()
    glTranslatef(girl_x,GROUND,0)
    glScalef(girl_dir,1,1)
    line(-4,-40,-4+sw,-2,'#f1c7a0',5)                       # pa
    line(4,-40,4-sw,-2,'#f1c7a0',5)
    poly([(-8,-85),(8,-85),(18,-40),(-18,-40)],'#e8639a')   # dress
    circle(-2,-102,14,'#3a2416')                            # chul
    circle(2,-100,12,'#f1c7a0')                             # mukh
    circle(7,-102,1.8,'#222222')                            # chokh
    line(2,-80,24,-68,'#f1c7a0',5)                          # hat
    glPushMatrix()                                          # jhajhri (watering can)
    glTranslatef(26,-68,0)
    if watering:
        glRotatef(20,0,0,1)
    rect(-10,-9,22,18,'#4a90d9')
    line(12,2,28,-8,'#4a90d9',4)
    handle=[(-10+7*math.cos(a),-1+7*math.sin(a)) for a in [math.pi/2+i*math.pi/12 for i in range(13)]]
    polyline(handle,'#4a90d9',4)
    glPopMatrix()
    glPopMatrix()


# ---------- background ----------
def draw_background():
    # akash (gradient)
    glBegin(GL_QUADS)
    color('#8fd0ff');glVertex2f(0,0);glVertex2f(width,0)
    color('#e3f4ff');glVertex2f(width,350);glVertex2f(0,350)
    glEnd()
    circle(700,70,32,'#ffd84d')                             # surjo
    for c in clouds:                                        # megh (sthir)
        for a in [(0,0,22),(24,-8,26),(50,0,20)]:
            circle(c[0]+a[0],c[1]+a[1],a[2],'#ffffff')
    # dure barir silhouette
    for b in [(20,70,150,'#9fb4c8'),(100,90,110,'#b3c3d3'),(210,60,170,'#8fa6bb'),(290,80,120,'#a9bccd'),
              (400,100,100,'#9fb4c8'),(500,75,160,'#b3c3d3'),(590,95,130,'#8fa6bb'),(690,70,150,'#a9bccd')]:
        rect(b[0],350-b[2],b[1],b[2],b[3])
        wc=lighten(b[3],0.35)
        wy=350-b[2]+12
        while wy<335:
            wx=b[0]+10
            while wx<b[0]+b[1]-10:
                rect(wx,wy,8,11,wc)
                wx+=20
            wy+=24
    # chhader parapet deoal
    rect(0,350,width,60,'#c8694a')
    for y in range(360,410,12):
        rect(0,y,width,1,'#b05c41')
    rect(0,344,width,8,'#e3d6c3')
    # chhader mejhe
    rect(0,GROUND,width,90,'#b9a58a')


def main():
    draw_background()
    for i in range(len(plants)):
        draw_plant(i)
    draw_girl()
    for d in drops:
        circle(d[0],d[1],2.2,'#3aa0ff')


# ---------- controls ----------
def toggle():
    global is_playing
    is_playing=not is_playing
    glutSetWindowTitle(b"Girl watering rooftop garden - Playing" if is_playing else b"Girl watering rooftop garden - Paused")

def reset_all():
    global girl_x,girl_dir,girl_walk,mode,target,timer,drops
    for p in plants:
        p[1]=0.3
    girl_x=40;girl_dir=1;girl_walk=0
    mode='walk';target=0;timer=0;drops=[]

def mouse(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        toggle()

def keyboard(key, x, y):
    global speed
    if key==b' ':
        toggle()
    elif key in (b'r',b'R'):
        reset_all()
    elif key in (b'+',b'='):
        speed=min(3.0,speed+0.2)
    elif key==b'-':
        speed=max(0.4,speed-0.2)


# ---------- update ----------
def update(v):
    global girl_x,girl_dir,girl_walk,mode,target,timer,drops

    if is_playing:
        dt=0.015*speed
        for d in drops:
            d[3]+=420*dt
            d[0]+=d[2]*dt
            d[1]+=d[3]*dt
        drops=[d for d in drops if d[1]<GROUND-POT-4]

        if mode=='walk':
            stand=plants[target][0]-75
            diff=stand-girl_x
            if abs(diff)<3:
                girl_x=stand;girl_dir=1
                mode='water';timer=2.2
            else:
                girl_dir=1 if diff>0 else -1
                girl_x+=girl_dir*65*dt
                girl_walk+=dt*7
        elif mode=='water':
            timer-=dt
            if random.random()<dt*45:
                drops.append([girl_x+54,GROUND-72,25+random.random()*25,-10+random.random()*20])
            plants[target][1]=min(1,plants[target][1]+dt*(0.7/2.2))
            if timer<=0:
                plants[target][1]=1
                if target<len(plants)-1:
                    target+=1;mode='walk'
                else:
                    mode='done'

    glutPostRedisplay()
    glutTimerFunc(15,update,0)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)      # y niche-mukhi, jate picture ager moto thake
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    main()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA |GLUT_DOUBLE)
glutInitWindowSize(width,height)
glutInitWindowPosition(0,0)
glutCreateWindow(b"Girl watering rooftop garden - Playing")
glutDisplayFunc(showScreen)
glutMouseFunc(mouse)
glutKeyboardFunc(keyboard)
glutTimerFunc(0,update,0)
glutMainLoop()
