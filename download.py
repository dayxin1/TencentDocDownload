import requests
import re
from urllib.parse import urlparse
import json

def initial_fetch(url):
    init_url = url
    if (init_url.find('?') != -1):
        init_url = init_url[:init_url.find('?')]

    init_text = requests.get(init_url).text

    t = re.search(r"&t=(\d+)\"", init_text).group(1)
    id = re.search(r"/sheet/(.+)\??", init_url).group(1)

    opendoc_url = "https://docs.qq.com/dop-api/opendoc"
    opendoc_params={
        "id" : id,
        "normal" : "1",
        "outformat" : "1",
        "startrow" : "0",
        "endrow" : "60",
        "wb" : "1",
        "nowb" : "0",
        "callback" : "clientVarsCallback",
        "xsrf" : "",
        "t" : t
    }
    opendoc_text = requests.get(opendoc_url, params=opendoc_params).text
    opendoc_json = read_callback(opendoc_text)

    title = opendoc_json["clientVars"]["title"]
    tabs = opendoc_json["clientVars"]["collab_client_vars"]["header"][0]["d"]
    padId = opendoc_json["clientVars"]["collab_client_vars"]["globalPadId"]


    return title, tabs, opendoc_params

def read_sheet(sheet, opendoc_params):
    opendoc_url = "https://docs.qq.com/dop-api/opendoc"
    opendoc_params["tab"] = sheet
    opendoc_text = requests.get(opendoc_url, params=opendoc_params).text
    opendoc_json = read_callback(opendoc_text)
    max_row = opendoc_json["clientVars"]["collab_client_vars"]["maxRow"]
    max_col = opendoc_json["clientVars"]["collab_client_vars"]["maxCol"]
    padId = opendoc_json["clientVars"]["collab_client_vars"]["globalPadId"]
    rev = opendoc_json["clientVars"]["collab_client_vars"]["rev"]

    sheet_url = "https://docs.qq.com/dop-api/get/sheet"
    sheet_params={
        "tab" : sheet,
        "padId" : padId,
        "subId" : sheet,
        "outformat" : "1",
        "startrow" : "0",
        "endrow" : max_row,
        "normal" : "1",
        "preview_token" : "",
        "nowb" : "1",
        "rev" : rev
    }
    sheet_text = requests.get(sheet_url, params=sheet_params).text
    sheet_json = json.loads(sheet_text)
    # sheet_content = sheet_json["data"]["initialAttributedText"]["text"][0][-1][0]["c"][1]
    sheet_content = {}
    for temp_class in sheet_json["data"]["initialAttributedText"]["text"][0]:
        if type(temp_class[0]) == dict and "c" in temp_class[0].keys():
            if len(temp_class[0]["c"]) > 1 and type(temp_class[0]["c"][1]) == dict:
                temp = temp_class[0]["c"][1] # type: dict
                for k, v in temp.items():
                    if k.isdigit() and type(v) == dict:
                        sheet_content[k] = v
    return sheet_content, max_col

def read_callback(text):
    content = re.search(r"clientVarsCallback\(\"(.+)\"\)", text).group(1)
    content = content.replace("&#34;", "\"")
    content = content.replace(r'\\"', r"\\'")
    return json.loads(content)
