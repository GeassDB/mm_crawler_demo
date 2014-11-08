#!/usr/bin/env python
import os
import sys
import re
import urllib
import argparse
import threadpool
from collections import deque

base_url = 'http://www.22mm.cc'
sub_url = 'href=\"(/mm/.+?)\"'
pic_url = '0]=\"(http://.+?)\"'


class Crawler:
    def __init__(self, url, sub, pic, limit, threads, outdir):
        self.url = url
        self.re_sub = sub
        self.re_pic = pic
        self.limit = limit
        self.outdir = outdir
        self.threads = threads
        self.pool = threadpool.ThreadPool(self.threads)
        self.queue = deque()
        self.queue.append(url)
        self.visited = set()
        self.imgs = set()
        self.linkre = re.compile(self.re_sub)
        self.pattern = re.compile(self.re_pic)

    def start(self):
        # handle thread
        l = self.queue.popleft()
        self.visited |= {l}
        print "Get Page: "+l
        data = self.html_get(l)
        # get the whole
        for page in self.linkre.findall(data):
            page = base_url + page

            if page not in self.visited:
                self.visited |= {l}
                self.queue.append(page)
        # capture the img
        for pic in self.pattern.findall(data):
            pic = pic.replace('big', 'pic')
            self.imgs |= {pic}
            # reach the limit
            #if len(self.imgs) == self.limit and self.limit != 0:
                #self.down_img(self.imgs)
        requests = threadpool.makeRequests(self.real_iron, range(self.threads))
        [self.pool.putRequest(req) for req in requests]
        self.pool.wait()
        print self.imgs
        self.down_img(self.imgs)

    def html_get(self, url):
        # TODO: handle exception and retries
        fp = urllib.urlopen(url)
        return fp.read()

    def down_img(self, imgs):
        # download img
        cnt = 0
        for each in imgs:
            print 'Downloading image: '+each
            cnt += 1
            i = each.rfind('/')
            img_name = each[(i+1):]
            full_path = self.outdir+'/'+img_name
            print 'Saving to: ' + full_path
            urllib.urlretrieve(each, full_path)
            print "%d mm_pic downloaded." % cnt
        sys.exit()

    def real_iron(self, work_id):

        print("thread {} start".format(work_id))

        while self.queue:
            l = self.queue.popleft()
            self.visited |= {l}
            print "Get Page: "+l
            data = self.html_get(l)
            # get the whole
            for page in self.linkre.findall(data):
                page = base_url + page

                if page not in self.visited:
                    self.visited |= {l}
                    self.queue.append(page)
        # capture the img
            for pic in self.pattern.findall(data):
                pic = pic.replace('big', 'pic')
                self.imgs |= {pic}

        print("thread {} end".format(work_id))


def main():
    # handle arg
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--threads", type=int, default=10,
                        help="number of threads (default: 10)")
    parser.add_argument("-l", "--limit", type=int, default=0,
                        help="number of max images (default: 0 -> nolimit)")
    parser.add_argument("-o", "--outdir", default='./pics',
                        help="images output dir (default: ./pics)")

    args = parser.parse_args()
    args.threads = args.threads or 10
    args.limit = args.limit or 0
    args.outdir = args.outdir or './pics'

    if os.path.exists(args.outdir) is False:
        os.mkdir(args.outdir)

    crawler = Crawler(base_url, sub_url, pic_url,
                      args.limit, args.threads, args.outdir)
    crawler.start()

if __name__ == '__main__':
    main()
