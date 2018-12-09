'''
This module will allow you to downlaod all pictures from VSCO account
'''

import requests
import time
import random


class vscoDownloader(object):
    def __init__(self, top_level_url):
        self.top_level_url = top_level_url
        self.image_urls = []
        self.cur_sesh = None
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
        self.timeout = 20

    def run(self, max_page, start_count_at):
        count = start_count_at

        self.image_urls = []
        self.cur_sesh = None

        # Get images on page
        print('Getting page {}'.format(i))

        self.cur_sesh = requests.Session()

        cur_url = self.top_level_url.format(i)

        
        all_indexes, collection_text = self.create_image_indexes(cur_url)

        self.image_urls += self.create_image_urls(all_indexes, collection_text)
        time.sleep(random.random() * 5)
        #Finish getting images on page

        print('Deduplicating Images...')
        self.image_urls = set(self.image_urls)
        print(self.image_urls)
        print('Total of {} images'.format(len(self.image_urls)))
        time.sleep(1)
        print('Beginning Download...')
        
        for img_page_url in self.image_urls:
            
            time.sleep(random.random() * 2)
            final_url = self.get_final_img_url(img_page_url)
            converted = self.convert_final_image_url(final_url)

            print(final_url, 'final')
            print(converted, 'converted')

            filename = 'mandyAdenan{}'.format(count)
            filename = filename + '.jpg'
            self.download_final_img(converted, filename)

            count += 1
            
            time.sleep(random.random() * 1)
    
        print('Complete')
        
    def create_image_indexes(self, collection_url):
        '''Recieves the home page with all small images hosted and returns a list of indexes at which
        the image page urls begin
         '''
        all_images_start_index = set()
        resp = self.cur_sesh.get(collection_url, headers=self.headers, timeout=self.timeout)

        collection_text = resp.text
        keyword = 'permalink":"'

        for i in range(len(collection_text)):
            if collection_text[i] == 'p':
                if collection_text[i : i + len(keyword)] == keyword:
                    all_images_start_index.add(i + 12)

        return all_images_start_index, collection_text

    def create_image_urls(self, image_indexes, resp_text):
        '''Iterates through the HTTP text response and collects the real image URL
        to store in a list
        '''
        
        #the image url has a hash of fixed length at the end, which is why 57 is hardcoded
        image_urls = []
        for elm in image_indexes:
            image_urls.append(resp_text[elm: elm + 55]) #CHANGE THIS this end portion needs to be CUSTOMIZED
        return image_urls
        #57 for georgia, 55 for ayemandy



    def get_final_img_url(self, single_image_page_url):
        error_count = 0
        while error_count < 5:
            try:
                resp = self.cur_sesh.get(single_image_page_url, headers = self.headers, timeout=self.timeout)
                if resp.status_code == 200:
                    break
                else:
                    error_count += 1

            except Exception as e:
                print(e)
                print(single_image_page_url)
                error_count += 1


        http_text = resp.text
        keyword = '"responsiveUrl":"'
        final_image_url_start = resp.text.find(keyword) + len(keyword)
        final_image_url_end = 0

        for i in range(final_image_url_start, final_image_url_start + 500):
            if http_text[i: i + 4] == '.jpg':
                final_image_url_end = i 
        final_image_url = http_text[final_image_url_start : final_image_url_end + 4]

        return final_image_url

    def convert_final_image_url(self, url):
        if url.find('vsco_') == -1:
            first = False 
            final_index = 0
            print(url)
            for i in range(len(url)):
                if url[i] == '/' and first:
                    final_index = i
                    break
                elif url[i] == '/':
                    first = True

                    #if it has vsco_ --> #https://image.vsco.co/1/54dff5b132d922277393/5980edb047eb6a1f368225da/vsco_080117.jpg
                    #if it has other or "vsco" -->

                    #standard -->vsco
                    #im.vsco.co/aws-us-west-2/4d4920/2277393/5b612c83537bb14847e89c61/vsco5b612c85a875c.jpg
                    #https://image-aws-us-west-2.vsco.co/4d4920/2277393/5b612c83537bb14847e89c61/vsco5b612c85a875c.jpg

                    ##first exception to rule --> vsco_
                    #im.vsco.co/1/54dff5b132d922277393/5980edb047eb6a1f368225da/vsco_080117.jpg
                    #https://image.vsco.co/1/54dff5b132d922277393/5980edb047eb6a1f368225da/vsco_080117.jpg

                    #im.vsco.co/aws-us-west-2/4d4920/2277393/59de7644abbf221c66f93d10/vsco59de7647c6aa6.jpg
                    #https://image-aws-us-west-2.vsco.co/4d4920/2277393/59de7644abbf221c66f93d10/vsco59de7647c6aa6.jpg
            prefix = 'https://image-aws-us-west-2.vsco.co'
            url = prefix + url[final_index:]

        elif url.find('vsco_') != -1:
            url = 'https://image.vsco.co' + url[10:]

        else:
            print(url, "what is happening")
            #im.vsco.co/aws-us-west-2/4d4920/2277393/59de763dabbf221c66f93d0f/vsco59de76404d41e.jpg
            #https://image-aws-us-west-2.vsco.co/4d4920/2277393/59de763dabbf221c66f93d0f/vsco59de76404d41e.jpg

            #59d139ff6ac236375d372d7b/59d139ff6ac236375d372d7b couldn't download because it's a gif video thing
        
        return url

    def download_final_img(self, url, filename):
        resp = requests.get(url, headers = self.headers, timeout=self.timeout)
        error_count = 0

        while error_count < 5:
            try:
                if resp.status_code == 200:
                    with open("C:/Users/Nick/Desktop/vsco/" + filename, 'wb') as f:
                        f.write(resp.content)
                    break
                else:
                    print(resp.status_code)
                    error_count += 1
                    time.sleep(1)
                    print(url, 'Couldnt download')
            except Exception as e:
                print(e)
                error_count += 1
                time.sleep(1)



top_level = 'https://vsco.co/ayeemandy/images/{}'

if __name__ == '__main__':
    dwnld = vscoDownloader(top_level)
    page = 1
    #16
    for i in range(1, 17):
        dwnld.run(i, page * 1000)
        page += 1
        time.sleep(4)
