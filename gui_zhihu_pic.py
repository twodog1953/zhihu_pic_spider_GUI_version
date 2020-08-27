from tkinter import *
from urllib.request import urlopen as uReq
import urllib.request
import urllib.request as urr
from bs4 import BeautifulSoup as soup
from time import sleep
import json
import os
from random import randrange
from threading import Thread
from tkinter.messagebox import showinfo

root = Tk()
root.title('GUI Crawler for Zhihu pics')
root.geometry("380x450")

# initialize the program
q_num = ['344718540']
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/46.0.2490.76 Mobile Safari/537.36',
}

if_single = False


# define functions
def num_con():
    global q_label, q_num, if_single
    if if_single == True:
        q_label.config(text='Current Question: ' + e.get())
        q_num = [e.get()]
    else:
        if e.get() not in q_num:
            q_label.config(text='Question appended: ' + e.get())
            q_num.append(e.get())
        else:
            q_label.config(text='Repeated Question lol')

def My_url(num):
    my_url = 'https://www.zhihu.com/api/v4/questions/' + num + '/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default'
    return my_url


def Temp_url(num):
    temp_url = 'https://www.zhihu.com/question/' + num
    return temp_url


def ReadPage1(url):
    uClient = urr.Request(url, headers=headers)
    with uReq(uClient) as response:
        page_html = response.read()
    return page_html


def GetFolderName(url):
    uClient2 = uReq(url)
    temp_html = uClient2.read()
    uClient2.close()
    temp_soup = soup(temp_html, "html.parser")
    temp_header = temp_soup.h1
    folder_name = temp_header.get_text()
    if folder_name[-1] == '?':
        folder_name = folder_name[0:-1]
    return folder_name


# show the progress here
def exe_info(mes):
    exe_label.config(text=mes)


# save 2 dir, links need to be list; 2 inputs in tot
def save2dir(links):
    for jj in range(len(links)):
        local = str(links[jj][26:61]) + '.jpg'
        urllib.request.urlretrieve(links[jj], local)


def crawl():
    for i in q_num:
        exe_info('Start Crawling ...')
        my_url = My_url(i)
        temp_url = Temp_url(i)
        page_html = ReadPage1(my_url)
        folder_name = GetFolderName(temp_url)
        is_end = False
        img_links = []
        exe_info('Start capturing image links ...')
        while is_end == False:
            sleep(randrange(5, 20) / 10)
            # exe_info('Next page ...')
            aa = json.loads(page_html)
            # three big category: ad_info, data, paging
            paging = aa["paging"]
            data = aa['data']
            for i in data:
                # sleep(randrange(1,3))
                # find all img
                content = i['content']
                page_soup = soup(content, "html.parser")
                # j = json.loads(uClient.read())
                # print(page_soup.h1)
                containers = page_soup.findAll('img', {"class": "origin_image zh-lightbox-thumb"})
                # exe_info('Captured: ' + str(len(containers)))

                for j in containers:
                    img_links.append(j['src'])
                # exe_info("Total: " + str(len(img_links)))

            # check if everything is ended after the processing step
            is_end = paging['is_end']
            my_url = paging['next']

            # get the next url in queue
            uClient = uReq(my_url)
            page_html = uClient.read()
            uClient.close()

        exe_info('All links captured ...')

        # enter current dir and create a folder
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, folder_name)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        os.chdir(final_directory)

        # divide up the total targets into all cores in computer
        cpu_num = os.cpu_count()
        por_num = 1
        if len(img_links) < cpu_num:
            por_num = len(img_links)
            por_qua = 1
            remainder = 0
        else:
            por_num = cpu_num
            por_qua = len(img_links) // (cpu_num - 1)
            remainder = len(img_links) % (cpu_num - 1)

        # create multiple processes to get links faster
        threads = []
        for i in range(por_num):
            if remainder == 0:
                t = Thread(target=save2dir, args=(img_links[(i * por_qua):((i + 1) * por_qua)],))
            else:
                if i != por_num - 1:
                    t = Thread(target=save2dir, args=(img_links[(i * por_qua):((i + 1) * por_qua)],))
                else:
                    t = Thread(target=save2dir, args=(img_links[(i * por_qua):(i * por_qua) + remainder],))
            t.start()
            threads.append(t)
        for j in threads:
            j.join()

        os.chdir(current_directory)
        exe_info('Download finished lol')


def help_btn():
    showinfo(title='Help Content', message='Enter the number of the question in the box and click "# Enter" button, '
                                           'then click "start" button to start crawling. \n \n The program maybe not '
                                           'responding for a while during the running process, please do not close '
                                           'the program. The crawled pictures would be stored in the same directory as the main program. '
                                           '\n \n Example: when the address of the question page is '
                                           'https://www.zhihu.com/question/344718540, the question number would be '
                                           '344718540. '
                                           '\n \n The Queue button shows the current questions in queue. \n \n The '
                                           'clear button restore the queue to the default state. ')


def op():
    global if_single, q_num
    # if if_single == True:
    #     if_single = False
    #     exe_info('One Question at a time now')
    # else:
    #     if_single = True
    #     exe_info('Multiple Questions now')
    top = Toplevel()
    top.geometry("300x300")
    lll = Label(top, text='Current Question numbers in queue: ')
    lll.pack()
    for i in q_num:
        Label(top, text=i).pack()


def clean():
    global q_num
    q_num = ['344718540']
    exe_info('Queue restored to default')


# the entry box
q_label = Label(root, text='Question number', fg='blue', bg='white', font=("Courier", 10), pady=30)
q_label.grid(row=0, column=0, columnspan='2')
e = Entry(root, width=50, bg='white', borderwidth=3)
e.grid(row=1, column=0, columnspan='2')
e.insert(0, "344718540")
num_con_btn = Button(root, command=num_con, text='# Enter', padx=50, pady=15, font=("Courier", 10))
num_con_btn.grid(row=2, column=0, padx=10, pady=10)

# the crawl button
c_btn = Button(root, command=crawl, text='Start', padx=50, pady=15, font=("Courier", 10))
c_btn.grid(row=2, column=1, padx=10, pady=10)

# the help button
h_btn = Button(root, command=help_btn, text='help !', padx=50, pady=15, font=("Courier", 10), fg='red')
h_btn.grid(row=5, column=0, padx=10, pady=10)

# notification label
exe_label = Label(root, text='Notification would be shown here', bg='gray', pady=20)
exe_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# option button
op_btn = Button(root, text='Queue', command=op, padx=50, pady=15, font=("Courier", 10), fg='red')
op_btn.grid(row=5, column=1, padx=10, pady=10)

# clear button
clear_btn = Button(root, text='Clear', command=clean, padx=50, pady=15, font=("Courier", 10), fg='red')
clear_btn.grid(row=6, column=0, padx=10, pady=10)

root.mainloop()
