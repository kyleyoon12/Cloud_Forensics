from playwright.sync_api import Playwright, sync_playwright, expect
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from time import sleep
import requests
import json
import re
import urllib3
import os

def functions(headers, cookies): #Controller
    global folder
    folder = ['/']
    global file
    file = []

    print("[System] >>> Browsing Dropbox...")
    print("[System] >>> Folder Browsing Start!")
    recursive_search_folder("", headers, cookies)  # Root Directory부터 재귀적으로 모든 폴더 목록 획득
    print("[System] >>> Done")
    print("[System] >>> File Browsing Start!")
    for i in range(len(folder)):  # 획득한 폴더 각각을 input으로 해당 폴더에 존재하는 파일 목록 획득
        recursive_search_file(folder[i], headers, cookies)
    print("[System] >>> Done")

    while True:
        print("""

        <Select Mode>
        1.File Browser
        2.File Download
        3.Get Preview
        4.Get Revision
        5.Terminate

        """)

        try:
            mode = int(input("[Type Number] >>> "))
            if mode == 1:
                print("\nㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡList of Filesㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n")

                for i in range(len(file)):
                    print("[%d]" % (i+1), file[i][1]) #List of All Files

            if mode == 2:
                try:
                    while True:
                        sec_mode = input("\n[System] >>> Wish to download files? (y/n)\n") #파일 다운로드 - 로컬에서 저장경로 설정 필

                        if sec_mode == "y":
                            file_download(cookies) #파일 다운로드 - 로컬에서 저장경로 설정 필

                        elif sec_mode == "n":
                            break

                        else:
                            print("[System] >>> Invalid input. Please try again")

                except Exception as e:
                    print("[System] >>> Invalid input or error occurred. Please try again")
                    #print(e)

            if mode == 3:
                get_thumbnails(headers, cookies)

            if mode == 4:
                file_revision(headers, cookies)

            if mode == 5:
                print("[System] >>> Terminated")
                break

        except Exception as e:

            print("[System] >>> Error occurred or Invalid input. Please try again?")
            print("[System] >>> Error:", e)

def file_revision(headers, cookies):
    revisionable_file = []

    for i in range(len(file)):
        if file[i][2] > 0: #크기가 "-1"이면 삭제된 파일
            revisionable_file.append(file[i])

    param = {
        '_subject_uid': headers['X-Dropbox-Uid'],
        'undelete': '1',
    }

    for i in range(len(revisionable_file)):
        print("[System] >>> Checking Revisions of [%s] ..." % revisionable_file[i][1])
        url = "https://www.dropbox.com/history" + revisionable_file[i][1]
        response = requests.get(url, params=param, cookies=cookies, headers=headers, verify=False)
        revision_content = str(response.content)
        rev_filter = re.compile('("revisions": )(.*?)(, "cursor")')
        rev_filtered = rev_filter.findall(revision_content)
        make_json = '{"revisions": ' + rev_filtered[0][1] + "}"
        encoder = make_json.replace("\\\\", "\\")
        revision = json.loads(encoder)
        #print(revision)

        if len(revision["revisions"]) != 1:
            print("[System] >>> Downloading Revisions of [%s] ..." % revision["revisions"][0]["filename"])
            os.mkdir("Revision/%s" % revision["revisions"][0]["filename"])
            for x in range(len(revision["revisions"])):
                downloadable_url = "https:" + revision["revisions"][x]["preview_info"]["href"]
                s_filter = re.compile('(subject_uid=)(.*?)(&r)')
                subject_uid = s_filter.findall(downloadable_url)
                r_filter = re.compile('(revision_id=)(.*?)(&s)')
                revision_id = r_filter.findall(downloadable_url)
                w_filter = re.compile('(w=)(.*?)($)')
                w = w_filter.findall(downloadable_url)

                params = {
                    '_notify_domain': 'www.dropbox.com',
                    '_subject_uid': subject_uid[0][1],
                    "revision_id": revision_id[0][1],
                    "source": "_private_jsinfo_helper",
                    'w': w[0][1],
                }

                url = "https://www.dropbox.com/pri/get" + revisionable_file[i][1] + "?"
                response = requests.get(url, params=params, cookies=cookies, verify=False)

                with open("Revision/%s/[Ver.%d]%s" % (revision["revisions"][0]["filename"], (x+1), revision["revisions"][0]["filename"]), "wb") as f:
                    f.write(response.content)
        print("[System] >>> Done")

def revision_download(downloadable_url):

    #//www.dropbox.com/pri/get/revision_test.pptx?_subject_uid=1215469809\u0026revision_id=B0Ot9upTGMz-PAYOoF11qX6YjA2wkQTXJr6VKVpqOvn8eCdVeAi_s6b0b9pTpFgatorPJzAfv_sMGKdwmT-INnyLRU_BMLR6_Qb1-UpLYgVMaFXjII-5Y93rE6cQBcT-kP7prr4_WRRdna6r4YE_n8vk\u0026source=_private_jsinfo_helper\u0026w=AACyyUaUosgvF2tULwZxUc3K8_J3OVsBgxEVgfpEbVWV1A

    downloadable_url.replace("\u0026", "&")
    downloadable_url = "https:" + downloadable_url

    #https://www.dropbox.com/pri/get/revision_test.pptx?_subject_uid=1215469809&revision_id=B0Ot9upTGMz-PAYOoF11qX6YjA2wkQTXJr6VKVpqOvn8eCdVeAi_s6b0b9pTpFgatorPJzAfv_sMGKdwmT-INnyLRU_BMLR6_Qb1-UpLYgVMaFXjII-5Y93rE6cQBcT-kP7prr4_WRRdna6r4YE_n8vk&source=_private_jsinfo_helper&w=AACyyUaUosgvF2tULwZxUc3K8_J3OVsBgxEVgfpEbVWV1A

    s_filter = re.compile('(subject_uid=)(.*?)(&r)')
    subject_uid = s_filter.findall(downloadable_url)
    r_filter = re.compile('(revision_id=)(.*?)(&s)')
    revision_id = r_filter.findall(downloadable_url)
    w_filter = re.compile('(w=)(.*?)($)')
    w = w_filter.findall(downloadable_url)

    params = {
        '_notify_domain': 'www.dropbox.com',
        '_subject_uid': subject_uid[0][1],
        "revision_id": revision_id[0][1],
        "source": "_private_jsinfo_helper",
        'w': w[0][1],
    }

    url = "https://www.dropbox.com/pri/get/" # + file name with path + ?
    response = requests.get(url, params=params, cookies=cookies, verify=False)

    with open("Revision/filename", "wb") as f:
        f.write(response.content)


def get_thumbnails(headers, cookies):
    print("[System] >>> Getting thumbnail data...")

    global file
    previewable_file = [] #삭제된 파일(메타데이터상 파일 크기가 "-1") 제외한 다운로드 가능한 파일 리스트, 파일별 메타데이터 정보 포함

    for i in range(len(file)):
        if file[i][2] > 0: #크기가 "-1"이면 삭제된 파일
            previewable_file.append(file[i])

    preview_list = []
    preview_video = []
    preview_ssr_doc = []
    preview_image = []
    count = 0
    repeat = int(len(previewable_file)/30) #file이 전체 2000개라면, 30번씩 처리하기위한 반복횟수. 즉, 66번(66*30 = 1980)

    #만약 2000개라면, 30번씩 66번하면 1980개이고, 나머지 20개가 남기에 이를 위한 코드
    for i in range(repeat*30): #1980개 0부터 1979까지
        count += 1 #1,2,3,...30
        if count % 30 != 0: #i가 29일때(30번째일때) count는 30임 고로 여기로 안옴
            form = {"ns_id": previewable_file[i][5], "sj_id": previewable_file[i][6]}
            preview_list.append(form)

        if count % 30 == 0: #preview_list에 form이 30개 쌓였다면
            form = {"ns_id": previewable_file[i][5], "sj_id": previewable_file[i][6]}
            preview_list.append(form)
            data = {"files": preview_list}
            response = requests.post('https://www.dropbox.com/2/previews/get_preview_data_batch', cookies=cookies,
                                     headers=headers, data=json.dumps(data), verify=False)
            preview_list = []  # 초기화
            result = json.loads(response.content)

            for x in range(len(result["results"])):
                if "preview" in result["results"][x]:
                    if result["results"][x]["preview"]["content"][".tag"] == "video":
                        preview_video.append([result["results"][x]["file"]["sj_id"], result["results"][x]["preview"]["content"]["poster_url_tmpl"]])
                    if result["results"][x]["preview"]["content"][".tag"] == "ssr_doc":
                        preview_ssr_doc.append([result["results"][x]["file"]["sj_id"], result["results"][x]["preview"]["content"]["image_url_tmpl"]])
                    if result["results"][x]["preview"]["content"][".tag"] == "image":
                        preview_image.append([result["results"][x]["file"]["sj_id"], result["results"][x]["preview"]["content"]["default_src"]])

    for y in range(repeat*30, len(previewable_file)):
        form = {"ns_id": previewable_file[y][5], "sj_id": previewable_file[y][6]}
        preview_list.append(form)
        data = {"files": preview_list}
        response = requests.post('https://www.dropbox.com/2/previews/get_preview_data_batch', cookies=cookies,
                                 headers=headers, data=json.dumps(data), verify=False)
        result = json.loads(response.content)

        for z in range(len(result["results"])):
            if "preview" in result["results"][z]:
                if result["results"][z]["preview"]["content"][".tag"] == "video":
                    preview_video.append([result["results"][z]["file"]["sj_id"], result["results"][z]["preview"]["content"]["poster_url_tmpl"]])
                if result["results"][z]["preview"]["content"][".tag"] == "ssr_doc":
                    preview_ssr_doc.append([result["results"][z]["file"]["sj_id"], result["results"][z]["preview"]["content"]["image_url_tmpl"]])
                if result["results"][z]["preview"]["content"][".tag"] == "image":
                    preview_image.append([result["results"][z]["file"]["sj_id"], result["results"][z]["preview"]["content"]["default_src"]])


    print("[System] >>> Collecting the thumbnail of video files...")
    for ii in range(len(preview_video)):
        t_response = requests.get(preview_video[ii][1], cookies=cookies, headers=headers, verify=False)
        for xx in range(len(file)):
            if preview_video[ii][0] == file[xx][6]: #sj_id == sj_id
                t_video_filename = file[xx][1] #fq_path
                if t_response.status_code == 200:
                    t_video_finalname = t_video_filename.replace("/", "_")
                    with open('Thumbnail/%s' % t_video_finalname + ".jpg", 'wb') as f:
                        f.write(t_response.content)
                else:
                    print("Check:", t_video_filename, preview_video[ii])
    print("[System] >>> Video Files - Done")

    print("[System] >>> Collecting the thumbnail of document files...")
    for yy in range(len(preview_ssr_doc)):
        t_response = requests.get(preview_ssr_doc[yy][1], cookies=cookies, headers=headers, verify=False)
        for zz in range(len(file)):
            if preview_ssr_doc[yy][0] == file[zz][6]: #sj_id == sj_id
                t_doc_filename = file[zz][1] #fq_path
                if t_response.status_code == 200:
                    t_doc_finalname = t_doc_filename.replace("/", "_")
                    with open('Thumbnail/%s' % t_doc_finalname + ".jpg", 'wb') as f:
                        f.write(t_response.content)
                else:
                    print("Check:", t_doc_filename, preview_ssr_doc[yy])
    print("[System] >>> Document Files - Done")

    print("[System] >>> Collecting the thumbnail of image files...")
    for aa in range(len(preview_image)):
        t_response = requests.get(preview_image[aa][1], cookies=cookies, headers=headers, verify=False)
        for bb in range(len(file)):
            if preview_image[aa][0] == file[bb][6]: #sj_id == sj_id
                t_image_filename = file[bb][1] #fq_path
                if t_response.status_code == 200:
                    t_image_finalname = t_image_filename.replace("/", "_")
                    with open('Thumbnail/%s' % t_image_finalname + ".jpg", 'wb') as f:
                        f.write(t_response.content)
                else:
                    print("Check:", t_image_filename, preview_image[aa])

    print("[System] >>> Image Files - Done")

def file_download(cookies):
    global file #삭제된 파일을 포함한 전체 파일 리스트, 파일별 메타데이터 정보 포함
    downloadble_file = [] #삭제된 파일(메타데이터상 파일 크기가 "-1") 제외한 다운로드 가능한 파일 리스트, 파일별 메타데이터 정보 포함

    for i in range(len(file)):
        if file[i][2] > 0: #크기가 "-1"이면 삭제된 파일
            downloadble_file.append(file[i])

    for i in range(len(downloadble_file)):
        print("[%d]" % (i + 1), downloadble_file[i][1])

    to_download = int(input("\n[System] >>> Type the number of file you wish to download: "))
    print("[System] >>> File: [%s] selected. Please wait" % downloadble_file[(to_download-1)][1])
    print("[System] >>> Downloading...")

    get_param = downloadble_file[(to_download-1)][3] #파일별 메타데이터 중 다운로드에 필요한 Param값인 "subject_uid" 및 "w" 획득

    s_filter = re.compile('(=)(.*?)(&w)')
    subject_uid = s_filter.findall(get_param)
    w_filter = re.compile('(w=)(.*?)($)')
    w = w_filter.findall(get_param)

    params = {
        '_notify_domain': 'www.dropbox.com',
        '_subject_uid': subject_uid[0][1],
        'w': w[0][1],
    }

    url = "https://www.dropbox.com/pri/get"+downloadble_file[(to_download-1)][1]+"?"
    response = requests.get(url, params=params, cookies=cookies, verify=False)

    filename = downloadble_file[(to_download-1)][1]
    finalname = filename.replace("/", "_")

    with open('Download/%s' % finalname, 'wb') as f:
        f.write(response.content)

    print("[System] >>> Download Completed")

def recursive_search_folder(fq_path, headers, cookies):
    global folder

    data = {"path": fq_path, "max_height": 1, "limit_sub_folder_count": 150}
    response = requests.post('https://www.dropbox.com/2/files/list_subfolders', headers=headers, cookies=cookies,
                             data=json.dumps(data), verify=False)

    result = json.loads(response.content)

    if len(result['subfolder_entries']) != 0:
        for i in range(len(result['subfolder_entries'])):
            folder.append(result['subfolder_entries'][i]['folder_metadata']['path_display'])
            recursive_search_folder(result['subfolder_entries'][i]['folder_metadata']['path_display'], headers, cookies)
            #해당 폴더에 하위 폴더가 존재하는 경우 재귀적으로 조회

    else:
        flag = 0

def recursive_search_file_continue(headers, cookies, cursor):
    file_folder_continue = []

    response_continue = requests.post('https://www.dropbox.com/2/files/browse_continue', headers=headers,
                                      cookies=cookies, data=json.dumps(cursor), verify=False)

    result_continue = response_continue.content
    result_continue_json = json.loads(result_continue)

    for i in range(len(result_continue_json['paginated_file_info'])):
        file_folder_continue.append([result_continue_json['paginated_file_info'][i]['file_info']['type'][".tag"],
                            result_continue_json['paginated_file_info'][i]['file_info']['fq_path'],
                            result_continue_json['paginated_file_info'][i]['file_info']['size_bytes'],
                            result_continue_json['paginated_file_info'][i]['file_info']['direct_blockserver_link'],
                            result_continue_json['paginated_file_info'][i]['file_info']['file_id'],
                            result_continue_json['paginated_file_info'][i]['file_info']['ns_id'],
                            result_continue_json['paginated_file_info'][i]['file_info']['sjid']])
                            #필요한 메타 정보만 가공한 최종 형태: [type][fq_path][size][link][file_id][ns_id][sjid] - 보완 예정

    for x in range(len(file_folder_continue)): #Type이 폴더는 제외한 파일만 가공하는 과정
        if file_folder_continue[x][0] == "file":
            global file
            file.append(file_folder_continue[x])

    if result_continue_json["has_more"] == True: #여전히 불러올 파일 목록이 있는 경우
        cursor_continue = {}
        cursor_continue["cursor"] = result_continue_json["next_request_voucher"]
        recursive_search_file_continue(headers, cookies, cursor_continue) #cursor값과 함께 재귀적으로 처리

def recursive_search_file(fq_path, headers, cookies):
    path = {"fq_path": fq_path, "include_deleted": True, "sort_type": {".tag": "files_by_name"},
            "sort_is_ascending": True}
    response = requests.post('https://www.dropbox.com/2/files/browse', headers=headers, cookies=cookies,
                             data=json.dumps(path), verify=False)
    result = json.loads(response.content)
    file_folder = [] #input으로 주어진 경로(fq_path/folder)에 존재하는 모든 파일/폴더가 담기는 리스트

    for i in range(len(result['paginated_file_info'])):
        file_folder.append([result['paginated_file_info'][i]['file_info']['type'][".tag"],
                        result['paginated_file_info'][i]['file_info']['fq_path'],
                        result['paginated_file_info'][i]['file_info']['size_bytes'],
                        result['paginated_file_info'][i]['file_info']['direct_blockserver_link'],
                        result['paginated_file_info'][i]['file_info']['file_id'],
                        result['paginated_file_info'][i]['file_info']['ns_id'],
                        result['paginated_file_info'][i]['file_info']['sjid']])
                        #필요한 메타 정보만 가공한 최종 형태: [type][fq_path][size][link][file_id][ns_id][sjid] - 필요에 따라 보완 예정

    for x in range(len(file_folder)): #Type이 폴더는 제외한 파일만 가공하는 과정
        if file_folder[x][0] == "file":
            global file
            file.append(file_folder[x])

    if result['has_more'] == True: #해당 경로에 파일이 30개 이상인경우 별도 처리
        cursor = {}
        path_continue = result['next_request_voucher']
        cursor["cursor"] = path_continue
        recursive_search_file_continue(headers, cookies, cursor) #커서값과 함께 담당 재귀함수로 전달

def google_login():
    id = input("[System] >>> Input ID: ")
    pw = input("[System] >>> Input Password: ")

    driver = uc.Chrome(suppress_welcome = False)
    driver.get('https://www.dropbox.com/login')

    sleep(3)
    driver.find_element(By.CLASS_NAME, "auth-google.button-primary").click()
    sleep(3)
    driver.switch_to.window(driver.window_handles[1])
    sleep(3)
    driver.find_element(By.CLASS_NAME, "whsOnd.zHQkBf").send_keys(id)
    driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.qfvgSe.qIypjc.TrZEUc.lw1w4b").click()
    sleep(3)
    driver.find_element(By.CLASS_NAME, "whsOnd.zHQkBf").send_keys(pw)
    sleep(1)
    driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.qfvgSe.qIypjc.TrZEUc.lw1w4b").click()

    #print("[System] >>> Click OK button on the device")

    confirm = input("[System] >>> Click OK button on the device (Y/N)")

    print("[System] >>> Login succeeded!")
    print("[System] >>> Acquring authentication information. Please wait...")

    sleep(15)
    driver.switch_to.window(driver.window_handles[0])
    uid_html = driver.find_elements(By.CSS_SELECTOR, "body > script")

    for i in range(len(uid_html)):
        if "constants/auth" and "user_id" in uid_html[i].get_attribute("innerText"):
            inner_text = """%s""" % uid_html[i].get_attribute("innerText")
            uid_filter = re.compile('(: )(.*?)(})')
            uid_result = uid_filter.findall(inner_text)
            uid = uid_result[0][1]

    dropbox_cookies = driver.get_cookies()
    cookie_listing = []

    for i in range(len(dropbox_cookies)):
        cookie_listing.append((dropbox_cookies[i]["name"], dropbox_cookies[i]["value"]))

    cookies = {}  # 필수쿠키
    essential_cookies = ["t", "jar", "lid", "bjar", "blid"]  # 필수쿠키 선별

    for i in range(len(cookie_listing)):
        if cookie_listing[i][0] in essential_cookies:
            cookies[cookie_listing[i][0]] = cookie_listing[i][1]

    token = cookies["t"]  # 획득한 쿠키 중 사용자 인증 담당하는 필수 헤더값에 필요한 값 별도 추출 후 아래에서 대입
    headers = {'X-CSRF-Token': '', 'X-Dropbox-Uid': '', 'Content-Type': 'application/json'}  # 필수 헤더
    headers['X-CSRF-Token'] = token
    headers['X-Dropbox-Uid'] = uid

    driver.close()

    functions(headers, cookies)  # controller

def apple_login(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.dropbox.com/login")
    with page.expect_popup() as popup_info:
        page.locator("button:has-text(\"Apple로 로그인\")").click()
    page1 = popup_info.value
    page1.locator("input[type=\"text\"]").fill("ymaul2@korea.ac.kr")
    page1.locator("[aria-label=\"계속\"]").click()
    page1.locator("input[type=\"password\"]").fill("Alswldbsgh220@")
    page1.locator("[aria-label=\"로그인\"]").click()
    page1.locator("text=신뢰함").click()

    with page1.expect_navigation(): #2차인증 확인 후 브라우저에 직접 입력
        page1.locator("button:has-text(\"계속\")").click()
    page1.close()

    print("[System] >>> Login succeeded!")
    print("[System] >>> Acquring authentication information. Please wait...")

    page.goto("https://www.dropbox.com/")
    page.goto("https://www.dropbox.com/home")

    page.wait_for_timeout(10000) #HTML 로딩 기다리기 위함
    uid_html = page.query_selector_all("body > script") # 로그인 후 "/home" 에서 "X-Dropbox-Uid" 값 관련 태그에서 얻기 위함

    for i in range(len(uid_html)):
        if "constants/auth" and "user_id" in uid_html[i].inner_text():
            inner_text = """%s""" % uid_html[i].inner_text()
            uid_filter = re.compile('(: )(.*?)(})')
            uid_result = uid_filter.findall(inner_text)
            uid = uid_result[0][1]

    dropbox_cookies = page.context.cookies() #cookies 획득
    cookie_listing = []

    for i in range(len(dropbox_cookies)):
        cookie_listing.append((dropbox_cookies[i]['name'], dropbox_cookies[i]['value']))

    cookies = {} #필수쿠키
    essential_cookies = ["t", "jar", "lid", "bjar", "blid"] #필수쿠키 선별

    for i in range(len(cookie_listing)):
        if cookie_listing[i][0] in essential_cookies:
            cookies[cookie_listing[i][0]] = cookie_listing[i][1]

    token = cookies["t"] #획득한 쿠키 중 사용자 인증 담당하는 필수 헤더값에 필요한 값 별도 추출 후 아래에서 대입
    headers = {'X-CSRF-Token': '', 'X-Dropbox-Uid': '', 'Content-Type': 'application/json'} #필수 헤더
    headers['X-CSRF-Token'] = token
    headers['X-Dropbox-Uid'] = uid

    functions(headers, cookies) #controller

    # ---------------------
    context.close()
    browser.close()

def main():
    global folder
    folder = ['/']
    global file
    file = []

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while True:
        print("""

        <Select Login Mode>
        1.Google Login
        2.Apple Login
        3.Terminate

        """)

        try:
            login_mode = int(input("[Type Number] >>> "))
            if login_mode == 1:
                google_login()

            if login_mode == 2:
                with sync_playwright() as playwright:
                    apple_login(playwright)

            if login_mode == 3:
                print("[System] >>> Terminated")
                break

        except Exception as e:
            print("[System] >>> Error occurred or Invalid input. Please try again?")
            print(e)

if __name__ == '__main__':
    main()

