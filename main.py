import pyMeow as pm
import math

proc = pm.open_process("hl.exe")

class Colors:
    cyan = pm.get_color("cyan")
    red = pm.get_color("red")
    green = pm.get_color("lime")


class Modules:
    base = pm.get_module(proc,"hl.exe")["base"]
    hw = pm.get_module(proc,"hw.dll")["base"]
    client = pm.get_module(proc,"client.dll")["base"]

class Addresses:
    entity_list = Modules.hw+0x100CC60
    player_count = Modules.hw+0x13FCC44
    camera_direction = Modules.client + 0x1207C0
    fov = Modules.client+0x10A4B4

class Pointers:
    ent_list = [0x3A4]

class Offsets:
    ent_size = 0x324
    health = 0x160
    pos = 0x8

class Entity:
    def __init__(self,base):
        self.base = base
        self.h = self.base+Offsets.health
        self.pos = self.base+Offsets.pos
    def health(self):
        return pm.r_float(proc,self.h)
    def position(self):
        return pm.r_floats(proc,self.pos,3)
    
def direction():
    return pm.r_floats(proc,Addresses.camera_direction,3)
    
def wts(ply,worldpos,width,height):
    x_fov = math.radians(pm.r_float(proc,Addresses.fov))
    y_fov = x_fov/width * height
    cam_pos = ply.position()
    cam_look = direction()
    camToObj = [worldpos[i]-cam_pos[i] for i in range(3)]
    distToObj = math.sqrt(sum([camToObj[i]**2 for i in range(3)]))
    if distToObj == 0:
        distToObj = 0.0001
    camToObj = [i/distToObj for i in camToObj]
    camYaw = math.atan2(cam_look[1],cam_look[0])
    objYaw = math.atan2(camToObj[1],camToObj[0])
    relYaw = camYaw-objYaw
    if (relYaw > math.pi):
        relYaw -= 2*math.pi
    if (relYaw<-math.pi):
        relYaw += 2*math.pi
    objPitch = math.asin(camToObj[2])
    camPitch = math.asin(cam_look[2])
    relPitch = camPitch-objPitch
    if x_fov == 0:
        x_fov =0.001
    if y_fov == 0:
        y_fov = 0.001
    x = relYaw/(0.5*x_fov)
    y = relPitch/(0.5*y_fov)
    x = (x+1)/2
    y = (y+1)/2
    return x*width,y*height,distToObj
    

def entities():
    ntofind = pm.r_int(proc,Addresses.player_count)
    ply = pm.pointer_chain_32(proc,Addresses.entity_list,Pointers.ent_list)
    return Entity(ply),[Entity(ply+Offsets.ent_size*i) for i in range(1,ntofind)]

pm.overlay_init(target="Condition Zero", fps=144, trackTarget=True)
while pm.overlay_loop():
    swidth,sheight = pm.get_screen_width(),pm.get_screen_height()
    ply,ents = entities()
    alive_enemies = [i for i in ents if i.health()>1]       
    pm.begin_drawing()
    for i in alive_enemies:
        pos = i.position()
        x,y,dist = wts(ply,pos,swidth,sheight)
        width = 15000/dist
        height = 35000/dist
        x-=width/2
        
        pm.draw_text("health: "+str(i.health()),x,y,20/dist,Colors.cyan)
        pm.draw_line(x,y,x+width,y,Colors.red)
        pm.draw_line(x,y,x,y+height,Colors.red)
        pm.draw_line(x+width,y,x+width,y+height,Colors.red)
        pm.draw_line(x,y+height,x+width,y+height,Colors.red)
        pm.draw_line(swidth/2,sheight,x,y,Colors.green)

    pm.end_drawing()



