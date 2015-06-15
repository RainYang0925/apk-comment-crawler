# -*- coding: utf-8 -*-

import sys
import urllib2
import urllib
import re
import traceback
import time


MAX_COUNT = 1000
HOST = "http://zhushou.360.cn"
PAGE_PATH = "/list/index/cid/1/order/download/?page="

class SpiderModel:

    def __init__(self):
        self.__page_index = 1
        self.__apk_count = 0
        self.__file_name = ""

    def _get_unicode_page(self, url):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url.encode('utf-8'), headers = headers)
        response = urllib2.urlopen(req)
        page = response.read()
        unicode_page = page.decode("utf-8", "ignore")
        return unicode_page

    # Get the list of the special apk link
    def _get_apk_links(self, index):
        apks_page = self._get_unicode_page(HOST + PAGE_PATH + index);
        items = re.findall('<h3><a sid="(.*?)" href="(.*?)">(.*?)</a></h3>', apks_page, re.S)
        apk_links = []
        for item in items:
            apk_links.append(item[1])
        return apk_links

    # Get the comments url by apk name in baike and comment type
    def _get_comments_url(self, name, type, start, count):
        current_time = long(time.time() * 1000)
        url = ("http://intf.baike.360.cn/index.php?"
                + "name=" + name + "&c=message&a=getmessage" + "&start=" + str(start)
                + "&count=" + str(count) + "&type=" + type + "&_=" + str(current_time))
        return url

    def _save_file(self, apk_name, comments):
        if (self.__apk_count % 100) == 0:
            self.__file_name = "apk_bad_comments" + str(self.__apk_count) + ".txt";

        f = open(self.__file_name, 'a+')
        for comment in comments:
            comment = comment.replace('\\n', '')
            f.write(apk_name + '\t' + comment.decode("unicode_escape", "ignore") + '\n')
        f.close()

    def _get_apk_comments(self, links):
        for link in links:
            apk_page = self._get_unicode_page(HOST + link);
            apk_name = re.findall('\'sname\': \'(.*?)\'', apk_page, re.S)
            jquery_name = re.findall('\'baike_name\': \'(.*?)\'', apk_page, re.S)
            comments_total_count = 0
            retry_time = 0
            while comments_total_count < 50:
                jquery_url = self._get_comments_url(jquery_name[0], "bad", comments_total_count, 10)
                comments_page = self._get_unicode_page(jquery_url)
                comments = re.findall('"content":"(.*?)"', comments_page, re.S)
                # There are comments and retry time lower than 10
                if len(comments) > 0:
                    self._save_file(apk_name[0], comments)
                    comments_total_count += 10
                elif len(comments) == 0:
                    retry_time += 1
                    if retry_time >= 10:
                        break
            self.__apk_count += 1
            if self.__apk_count >= MAX_COUNT:
                break

    def traverse_pages(self):
        while self.__apk_count < MAX_COUNT:
            try:
                links = self._get_apk_links(str(self.__page_index))
                self._get_apk_comments(links)
                self.__page_index += 1
            except Exception, e:
                traceback.print_exc()
                break

def main():
    print u"""
    ------------------------------------------------------
    Craw 50 bad comments for every APK from 360 zhushou
    ------------------------------------------------------
    """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    model = SpiderModel()
    model.traverse_pages()

if __name__ == '__main__':
    main()