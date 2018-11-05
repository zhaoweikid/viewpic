import os, sys
import pygame
import threading
import traceback
import datetime, time


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

class ImageTrans:
    def __init__(self, image_dir, trans_dir, width=0, height=0):

        self.screen_width = width
        self.screen_height = height

        self.image_dir = image_dir
        self.trans_dir = trans_dir

        self.files  = self.load_files()


    def length(self):
        return len(self.images)

    def load_files(self):
        retfiles = []
        for root,dirs,files in os.walk(self.image_dir):
            for fn in files:
                if fn.startswith('zw_'):
                    continue
                if not fn.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    continue
                fpath = os.path.join(root, fn)
                retfiles.append(fpath)
        print("files:", len(retfiles))
        return retfiles

    def make(self):
        start = time.time()
        n = 0
        try:
            for fn in self.files:
                cachepath = self.trans_dir + fn[len(self.image_dir):]
                cdirname  = os.path.dirname(cachepath)
                filename = os.path.basename(cachepath)
                cachefile = 'zw_%04d_%s' % (self.screen_width, filename)

                cachepath = os.path.join(cdirname, cachefile)
                if os.path.isfile(cachepath):
                    print("found cache:", cachepath)
                else:
                    print("img:", fn)
                    try:
                        suf = scale(pygame.image.load(fn), self.screen_width, self.screen_height)
                        if not os.path.isdir(cdirname):
                            os.makedirs(cdirname)
                        print("save:", cachepath)
                        pygame.image.save(suf, cachepath)
                    except:
                        traceback.print_exc()

                n += 1

                print("%d/%d %f" % (n, len(self.files), round(float(n)/len(self.files), 4)))
        except Exception as e:
            traceback.print_exc()
        finally:
            print('load time:', time.time()-start)



def make_cache():
    pygame.init()


    image_dir = 'C:\\Users\\zhaow\\Pictures\\youyou'
    trans_dir = "C:\\Users\\zhaow\\Pictures\\youyou_cache"

    im = ImageTrans(image_dir, trans_dir, 1920, 1080)
    im.make()


if __name__ == '__main__':
    make_cache()

