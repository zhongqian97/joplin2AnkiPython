import json
import urllib.request
import yaml
import requests
from pprint import pprint
from typing import Set, Dict, Any, TextIO
import json
from copy import deepcopy
import os
from multiprocessing import Pool
from html.parser import HTMLParser

# 配置部分, 读取yaml文件即可
# config.yaml 只需要路径path、 基础端口port、 身份验证token 以及 笔记标签 tags 即可！
#
#

def _load_config(fp: TextIO) -> Dict[str, Any]:
    """
    Load the yaml config from the file-like object.
    """
    try:
        return yaml.safe_load(fp)
    except yaml.parser.ParserError as e:
        raise Exception(
            "Error parsing yaml file. Please check for formatting errors. "
            "A tool such as http://www.yamllint.com/ can be helpful with this."
        ) from e

def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path) as data_file:
            args = _load_config(data_file)
            return args
    except OSError:
        abs_path = os.path.abspath(config_path)
        raise Exception(f"Config file could not be found at {abs_path}.")
    except UnicodeDecodeError:
        raise Exception(
            f"There was an error decoding Config file from {config_path}. "
            f"Make sure your file is save using UTF-8"
        )

args = load_config('./config.yaml')
print("My config file: " + str(args))

# 可调函数部分
def getJson(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.json())
    return r.json()

def getPicture(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.content)
    return r.content

def getText(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.text)
    return r.text

def HasAnkiPing():
    global args
    url = 'http://localhost:'+ str(args['anki_port']) + '/'
    payload = {}
    try:
        if getText(url, payload) == 'AnkiConnect v.6':
            return True
        else:
            return False
    except:
        return False
    return False

def HasJoplinPing():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/ping'
    payload = {}
    try:
        if getText(url, payload) == 'JoplinClipperServer':
            return True
        else:
            return False
    except:
        return False
    return False

def HasTokenIsWorked():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/auth/check/'
    payload = deepcopy(args)
    try:
        if getJson(url, payload)["valid"] == True:
            return True
        else:
            return False
    except:
        return False
    return False

def getAllTags():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/tags'
    payload = deepcopy(args)
    i = 1
    all_jsons = {}
    while True:
        try:
            payload['page'] = i
            temp_json = getJson(url, payload)
            if len(all_jsons) == 0:
                all_jsons = temp_json
            else:
                all_jsons["items"].extend(temp_json["items"])
            
            i += 1
            if temp_json["has_more"] == False:
                break
        except:
            return []
    return all_jsons["items"]

def getAllFolders():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/folders'
    payload = deepcopy(args)
    i = 1
    all_jsons = {}
    while True:
        try:
            payload['page'] = i
            temp_json = getJson(url, payload)
            if len(all_jsons) == 0:
                all_jsons = temp_json
            else:
                all_jsons["items"].extend(temp_json["items"])
            
            i += 1
            if temp_json["has_more"] == False:
                break
        except:
            return []
    return all_jsons["items"]

def _tagsList2Dict(tags_list):
    d = {}
    for tag in tags_list:
        d[tag['title']] = tag['id']
    return d

def getNoteListByTags(tags_list):
    global args
    all_jsons = {}
    payload = deepcopy(args)
    tags = args['tags']
    tags_dict = _tagsList2Dict(tags_list)
    for tag_title in tags:
        if tag_title not in tags_dict:
            continue
        tag = tags_dict[tag_title]
        url = 'http://localhost:'+ str(args['port']) + '/tags/' + tag + "/notes"
        i = 1
        while True:
            try:
                payload['page'] = i
                temp_json = getJson(url, payload)
                if len(all_jsons) == 0:
                    all_jsons = temp_json
                else:
                    all_jsons["items"].extend(temp_json["items"])
                
                i += 1
                if temp_json["has_more"] == False:
                    break
            except:
                return []
    return all_jsons["items"]

def getNoteBodyByNoteId(note_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/notes/' + note_id + '/'
    payload = deepcopy(args)
    payload['fields'] = 'body'
    try:
        body = getJson(url, payload)
        return body['body']
    except:
        return ""
    return ""

def getNoteParentByNoteId(note_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/notes/' + note_id + '/'
    payload = deepcopy(args)
    payload['fields'] = 'parent_id'
    try:
        body = getJson(url, payload)
        return body['parent_id']
    except:
        return ""
    return ""

def getNoteAllResourceIdByNoteId(note_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/notes/' + note_id + '/resources'
    payload = deepcopy(args)
    i = 1
    all_jsons = {}
    while True:
        try:
            payload['page'] = i
            temp_json = getJson(url, payload)
            if len(all_jsons) == 0:
                all_jsons = temp_json
            else:
                all_jsons["items"].extend(temp_json["items"])
            
            i += 1
            if temp_json["has_more"] == False:
                break
        except:
            return []
    return all_jsons["items"]


def getNoteResourceFileByResourceId(resource_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/resources/' + resource_id + '/file'
    payload = deepcopy(args)
    try:
        img = getPicture(url, payload)
        return img
    except:
        return None
    return None

def getJoplinFolderName(folder_list, id):
    flag = True
    dir_name = '' # 使用：：作为分隔符
    parent_id = getNoteParentByNoteId(id)
    while flag:
        flag = False
        for folder in folder_list:
            if parent_id == folder['id']:
                dir_name = "::" + folder['title'] + dir_name
                parent_id = folder['parent_id']
                flag = True
                break
            pass
        pass
    return dir_name


# def saveNoteMarkdownFile(name, text):
#     global args
#     with open(args["path"] + name + '.md', "w", encoding='utf-8') as f:
#         f.write(getNoteBodyByNoteId(text))
#     pass

# def saveResourceFile(title, name, img):
#     global args
#     path = args["path"] + title + '/'
#     if os.path.exists(path) == False:
#         os.makedirs(path)
#     with open(path + name, "wb") as f:
#         f.write(getNoteResourceFileByResourceId(img))
#     pass

# Joplin单元测试
# assert HasPing() == True
# assert HasTokenIsWorked() == True
# tags_list = getAllTags()
# print(len(tags_list))
# note_list = getNoteListByTags(tags_list)
# print(len(note_list))
# print(getNoteBodyByNoteId(note_list[0]['id']))
# for note in note_list:
#     print(getNoteAllResourceIdByNoteId(note['id']))
# resource = getNoteAllResourceIdByNoteId(note['id'])
# getNoteResourceFileByResourceId(resource[0]['id'])

# Joplin主流程部分
# if __name__ == '__main__':
#     assert HasPing() == True
#     assert HasTokenIsWorked() == True
#     tags_list = getAllTags()
#     note_list = getNoteListByTags(tags_list)
#     # 串行代码
#     # for note in note_list:
#     #     saveNoteMarkdownFile(note['title'], getNoteBodyByNoteId(note['id']))
#     #     resource = getNoteAllResourceIdByNoteId(note['id'])
#     #     for r in resource:
#     #         saveResourceFile(note['title'], r['title'], getNoteResourceFileByResourceId(r['id']))
#     #     pass

#     # 并行代码
#     p = Pool(12)
#     for note in note_list:
#         p.apply_async(saveNoteMarkdownFile, args=(note['title'], note['id']))
#         resource = getNoteAllResourceIdByNoteId(note['id'])
#         for r in resource:
#             p.apply_async(saveResourceFile, args=(note['title'], r['title'], r['id']))

#     print('Waiting for all subprocesses done...')
#     p.close()
#     p.join()
#     print("zhongqian: done!!!!")

# 一个类绑定这两个内容
class anki:
    # Anki API 
    def request(action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def invoke(action, **params):
        requestJson = json.dumps(anki.request(action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            # raise Exception(response['error'])
            print(response['error'])
        return response['result']

    # 1、逐一检查是否已经添加到Anki中，如果不是，重新添加；（这里有一个BUG，即如果是图片，怎么处理？Base64检查，多进程运行吧？）
    def check_note_in_anki(self, note_list):
        for note in note_list:
            pass
        pass

    # 2、Anki重新添加 / 修改，没目录记得创建一下目录
    def add_note_in_anki(self, note_dir, note_front, note_back):
        pass

# html解析器
class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.joplin2anki_list = []
        pass

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", attrs)
        self.tag_stack.append(attrs[0][1]) # 使用模板直接硬解码出来的内容
        pass

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        flag = self.tag_stack.pop()
        if flag == 'question':
            self.question = self.data
        elif flag == 'answer':
            self.answer = self.data
            self.handle_joplin2anki()
        pass

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        self.data = data

    def set_dir(self, dir):
        self.dir = dir

    def handle_joplin2anki(self):
        card = dict({
                "deckName": "Default",
                "modelName": "Basic",
                "fields": {
                    "Front": "前面卡片",
                    "Back": "背面卡片"
                },
            }
        )
        card['deckName'] = self.dir
        card['fields']['Front'] = self.question.replace('\n', '<br />')
        card['fields']['Back'] = self.answer.replace('\n', '<br />')
        self.card = card
        self.joplin2anki_list.append(card)
        pass

# 单元测试
# invoke('createDeck', deck='test1123::123') # 创建目录 :: 这个符号可以创建子文件目录
# result = invoke('deckNames') // 获取名称
# print('got list of decks: {}'.format(result))
# 添加笔记
# note = dict({
#         "deckName": "Default",
#         "modelName": "Basic",
#         "fields": {
#             "Front": "前面卡片",
#             "Back": "背面卡片"
#         },
#     }
# )   
# result = anki.invoke('addNote', note=note)
# parser = MyHTMLParser()
# anki.invoke('createDeck', deck='zhongqian_test_deck')
# parser.set_dir('zhongqian_test_deck')
# strs = '''
# <span class="jta" data-id="2022-10-05T16-28-35-481">**Question:**<span class="question">

# ipairs和pairs的区别？

# </span><details class="answer">

# 1.ipairs遇到nil会停止，pairs会输出nil值然后继续下去。

# 2.ipairs并不会输出table中存储的键值对,会跳过键值对，然后顺序输出table中的值。而pairs会输出table的键值对，先顺序输出值，再乱序(键的哈希值)输出键值对。

# </details></span>
# '''
# parser.feed(strs)
# result = anki.invoke('addNote', note=parser.card)

# 主流程
if __name__ == '__main__':
    assert HasAnkiPing() == True and HasJoplinPing() == True
    assert HasTokenIsWorked() == True
    tags_list = getAllTags()
    dirs_list = getAllFolders()
    note_list = getNoteListByTags(tags_list)

    # 获取Joplin内所有的Anki卡片
    card_list = []
    # p = Pool(12)
    for note in note_list:
        all_joplin_md_content = getNoteBodyByNoteId(note['id'])
        parser = MyHTMLParser()
        dir_name = getJoplinFolderName(dirs_list, note['id'])[2:] # TODO zhongqian: 这个名字注意分割使用：：符号
        anki.invoke('createDeck', deck=dir_name)
        parser.set_dir(dir_name)
        parser.feed(all_joplin_md_content)
        card_list.extend(parser.joplin2anki_list)
        # p.apply_async(saveNoteMarkdownFile, args=(note['title'], note['id']))
        # resource = getNoteAllResourceIdByNoteId(note['id'])
        # for r in resource:
        #     p.apply_async(saveResourceFile, args=(note['title'], r['title'], r['id']))
        pass
    
    # 对比所有card是否有更换了新的内容，如果更换了及时更新一下
    for card in card_list:
        anki.invoke('addNote', note=card)
        pass

    # print('Waiting for all subprocesses done...')
    # p.close()
    # p.join()
    print("zhongqian: done!!!!")