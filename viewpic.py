import os, sys
import pygame
import threading
import traceback
import datetime, time
import getopt

def init():
    pygame.init()
    size = width, height = 1920, 1080

    #screen = pygame.display.set_mode(size)
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN|pygame.HWSURFACE)
    #screen = pygame.display.set_mode(size, pygame.HWSURFACE)



def scale(img1, width, height):
    rect  = img1.get_rect()
    #print('img1:', rect)
    img1h = rect.height
    img1w = rect.width

    img2h = height

    rate = float(height) / img1h
    img2w = int(rect.width * rate)
    
    if img2w > width:
        img2w = width
        
        rate  = float(width) / img1w
        img2h = int(rect.height * rate) 


    img2 = pygame.transform.smoothscale(img1, (img2w, img2h))
    #print('img2:',  img2.get_rect())
    print ("from: %d/%d to: %d/%d" % (img1w, img1h, img2w, img2h))

    return img2

class Text:
    def __init__(self, fontsize=24):
        self.fontsize = fontsize
        self.font = pygame.font.Font(None, self.fontsize)

        self.color = pygame.Color(255,255,255)
        self.bgcolor = pygame.Color(0,0,0)

    def draw(self, text, suf, pos=None, colorkey=True):
        t = self.font.render(text, False, self.color, self.bgcolor)
        if colorkey:
            t.set_colorkey(self.bgcolor)

        if not pos:
            suf.blit(t, t.get_rect())
        else:
            suf.blit(t, pygame.Rect(pos[0], pos[1], t.get_width(), t.get_height()))



class ImageList:
    def __init__(self, image_dir, pos):
        global screen

        self.screen_width  = screen.get_width()
        self.screen_height = screen.get_height()

        self.image_dir = image_dir

        self.loadn  = 0
        self.cachen = 100 + pos

        self.files  = self.load_files()
        self.images = [] # (filename, surface)
        for fn in self.files[:self.cachen]:
            self.images.append([fn, None])


    def load_files(self):
        retfiles = []
        for root,dirs,files in os.walk(self.image_dir):
            for fn in files:
                if not fn.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    continue
                fpath = os.path.join(root, fn)
                retfiles.append(fpath)
        print("files:", len(retfiles))
        return retfiles

    def load_image(self, pos):
        start = time.time()
        try:
            idxs = []
            if type(pos) == int:
                idxs.append(pos)
            else:
                idxs = pos

            for i in idxs:
                if i >= len(self.images):
                    return
                one = self.images[i]
                if not one[1]:
                    print("load:", one[0])
                    suf = pygame.image.load(one[0])
                    if suf.get_height() == 1080 or suf.get_width() == 1920: 
                        one[1] = suf
                    else:
                        one[1] = scale(suf, self.screen_width, self.screen_height)
                    self.loadn += 1
        except Exception as e:
            traceback.print_exc()
        finally:
            print('load time:', time.time()-start)


    def get(self, pos):
        if pos >= len(self.files) or pos < 0:
            print("get pos:%d out of range, %d" % (pos, len(self.files)))
            return None
        
        if pos >= len(self.images):
            for i in range(len(self.images), len(self.images)+10):
                self.images.append([self.files[i], None])

        one = self.images[pos]
        if not one[1]:
            self.load_image(pos)

        return one


class ImageWindow:
    def __init__(self, image_dir, pos):
        global screen

        self.screen_width  = screen.get_width()
        self.screen_height = screen.get_height()

        self.imagelist = ImageList(image_dir, pos)

        self.pos = pos

    def get(self, idx):
        width = self.screen_width
        ret = []

        while True:
            suf = self.imagelist.get(idx)
            w = suf[1].get_width()

            if width >= w:
                ret.append([suf, pygame.Rect(0, 0, w, self.screen_height)])
            else:
                ret.append([suf, pygame.Rect(0, 0, width, self.screen_height)])
                return ret

            idx += 1
            width -= w

        return ret


    def get_idx(self, idx):
        width = self.screen_width
        ret = []

        while True:
            suf = self.imagelist.get(idx)
            if not suf:
                break
            w = suf[1].get_width()

            ret.append(idx)

            if width < w:
                return ret

            idx += 1
            width -= w

        return ret


    def get_surface(self, idx):
        global text
        imgs = self.get(idx)

        suf = pygame.Surface((self.screen_width, self.screen_height))
        x = 0
        for img in imgs:
            suf.blit(img[0][1], pygame.Rect(x, 0, img[1].width, img[1].height), img[1])

            title = os.sep.join(img[0][0].split(os.sep)[-2:])
            text.draw(title, suf, (x, self.screen_height-50))

            x += img[1].width

        return suf


    
    def get_surface_wall(self, idx):
        global text

        suf = pygame.Surface((self.screen_width, self.screen_height))


        i = idx

        x = 0
        row = 0

        rect = pygame.Rect(0, 0, 0, 0)
        while True:
            img = self.imagelist.get(i)
            if not img:
                break
            imgsuf = img[1]

            imgsuf_small = scale(imgsuf, 960, 540)
           
            rect.left = x
            rect.top  = row * 540
            suf.blit(imgsuf_small, rect)

            x += imgsuf_small.get_width()
            i += 1

            if x >= self.screen_width:
                if row == 0:
                    row = 1
                    i -= 1
                    x = 0
                else:
                    i -= 1
                    break


        return suf, i





    def get_surface_more(self, idx):
        idxes = self.get_idx(idx)

        for i in range(0, 2):
            if (idxes[0] > 0):
                idxes.insert(0, idxes[0]-1)

        for i in range(0, 2):        
            if idxes[-1] < len(self.imagelist.files)-1:
                idxes.append(idxes[-1]+1)

        cur = idxes.index(idx)

        imgs = [ self.imagelist.get(i) for i in idxes ]

        #print("idx:", ",".join([ str(x) for x in idxes ]))
        #print("idx:", ",".join([ x[0][-40:] for x in imgs ]))

        widths = [ x[1].get_width() for x in imgs ]
        allwidth = sum(widths)

        suf = pygame.Surface((allwidth, self.screen_height))

        x = 0
        for img in imgs:
            suf.blit(img[1], pygame.Rect(x, 0, 0, 0))

            x += img[1].get_width()

        return suf, widths, cur


    def preload(self, toidx):
        if self.pos >= len(self.imagelist.images):
            return False

        self.imagelist.load_image(self.pos)
        self.pos += 1

        return True




class Anim2:
    def __init__(self, suf, widths, cur, step=1, direction='r'):

        self.suf = suf
        self.widths = widths
        
        #self.speed = speed
        self.direction = direction
        self.cur = cur
        self.step = 1

        pw = sum(widths[:cur])
        if self.direction == 'r':
            #self.x = [widths[0], widths[0]+widths[1]]
            self.x = [pw, pw+widths[cur]]
        else:
            if cur > 0:
                self.x = [pw, pw-widths[cur-1]]
            else:
                self.x = [pw, 0]

        self.end = False

        self.start_time = time.time()
        self.last_time = self.start_time

        self.all_time = 1 

        self.cur_x = self.x[0]

    def display(self):
        global screen

        delta = time.time() - self.last_time
        distance = (delta/self.all_time) * self.suf.get_width()

        self.last_time = time.time()

        area = pygame.Rect(self.cur_x, 0, screen.get_width(), screen.get_height())
        if self.x[0] < self.x[1]:   # r
            self.cur_x += distance
            if self.cur_x >= self.x[1]:
                self.cur_x = self.x[1]
        else:
            self.cur_x -= distance
            if self.cur_x <= self.x[1]:
                self.cur_x = self.x[1]

        screen.fill((0,0,0))
        screen.blit(self.suf, screen.get_rect(), area)

        



class Viewer:
    def __init__(self, image_dir, pos=0):
        global screen

        pygame.init()
        size = width, height = 1920, 1080

        #screen = pygame.display.set_mode(size)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN|pygame.HWSURFACE)
        #screen = pygame.display.set_mode(size, pygame.HWSURFACE)
      
        self.screen = screen
        self.anim = None
        self.win = ImageWindow(image_dir, pos)
        self.idx = pos
        self.wall_idx = 0

    def display(self, direction='r'):
        if self.idx == 0 and direction == 'l':
            return

        if self.idx >= len(self.win.imagelist.files)-1 and direction == 'r':
            return
        
        if direction == 'r':
            idx2 = self.idx + 1
        else:
            idx2 = self.idx - 1

        #screen.blit(tosuf, screen.get_rect())
        
        #fromsuf = win.get_surface(idx)
        #tosuf = win.get_surface(idx2)
        #anim = Anim(fromsuf, tosuf, 10, direction)

        suf, widths, cur = self.win.get_surface_more(self.idx)
        self.anim = Anim2(suf, widths, cur, 10, direction)

        self.idx = idx2


    def display_wall(self, direction='r'):
        if self.idx == 0 and direction == 'l':
            return

        if self.idx >= len(self.win.imagelist.files)-1 and direction == 'r':
            return
        

        suf, idx2 = self.win.get_surface_wall(self.idx)
        screen.blit(suf, screen.get_rect())

        self.idx = idx2

        self.anim = None


    def run(self):
        global text

        text = Text()

        self.screen.blit(self.win.get_surface(self.idx), self.screen.get_rect())
        
        while True:
            self.win.preload(self.idx+20)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print('space')
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.key == pygame.K_LEFT:
                        self.display('l') 
                    elif event.key == pygame.K_RIGHT:
                        self.display('r') 
                    elif event.key == pygame.K_UP:
                        self.idx -= 6
                        if self.idx < 0: self.idx = 0
                        self.display_wall()
                    elif event.key == pygame.K_DOWN:
                        self.display_wall()

            if self.anim:
                self.anim.display()

            text.draw("%d/%d %d" % (self.win.pos, len(self.win.imagelist.files), self.idx), self.screen, colorkey=False)

            pygame.display.flip()


def main():
    image_dir = 'C:\\Users\\zhaow\\Pictures\\youyou_cache'
    pos = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hd:p:",["dir=","pos="])
    except getopt.GetoptError:
        print ('viewer.py -d <image directory> -p <start position>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('viewer.py -d <image directory> -p <start position>')
            sys.exit()
        elif opt in ("-d", "--dir"):
            image_dir = arg
        elif opt in ("-p", "--pos"):
            pos = int(arg)

    print("dir:", image_dir, 'pos:', pos)

    view = Viewer(image_dir, pos)
    view.run()


if __name__ == '__main__':
    main()

