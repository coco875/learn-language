import json
import PySimpleGUI as sg
from os import listdir
from os.path import isfile, join
import os
import sys
import random

vocabulary: list[str] = [f for f in listdir("vocabulary") if isfile(join("vocabulary", f))]

category: list[dict] = []

for i in vocabulary:
    with open(f"vocabulary/{i}") as file:
        category.append(json.load(file))

all_lang_file:list[str] = [f for f in listdir("language") if isfile(join("language", f))]

all_lang:list[str] = []
equivalence_lang: dict[str] ={}

for i in all_lang_file:
    with open("language/"+i) as file:
        name_lang:dict = json.load(file)["name"]
        equivalence_lang[i[:-5]] = name_lang
        all_lang.append(name_lang)

with open("config.json", "r") as file:
    config: dict = json.load(file)

with open(f"language/{config['lang']}.json") as file:
    lang: dict = json.load(file)

layout_menu:list = [
    [sg.Text(lang["menu"]["name"])],
    [sg.Button(lang["menu"]["vocabulary"])]
]

category_name : list = []

convert_title_category:dict = {}

for i in category:
    if config["lang"] in i["language"]:
        convert_title_category[i["title"][config["lang"]]] = category.index(i)
        category_name.append(i["title"][config["lang"]])

layout_category: list = [
    [sg.Listbox(category_name, key="cat", select_mode="LISTBOX_SELECT_MODE_SINGLE")],
    [sg.Button(lang["menu"]["continue"]), sg.Button(lang["menu"]["back"])]
]

layout_option_mode:list = [
    [sg.OptionMenu(["a"],key="option_mode")],
    [sg.Button(lang["menu"]["continue"]), sg.Button(lang["menu"]["back"])]
]

layout_quest:list = [
    [sg.Text("empty",key='question')],
    [sg.Input(key="answer")],
    [sg.Button(lang["menu"]["submit"])]
]

layout_responce = [
    [sg.Text("empty",key="resp")],
    [sg.Button(lang["menu"]["continue"])]
]

layout_total = [
    [sg.Text("ratio", key="ratio")],
    [sg.Button(lang["menu"]["continue"])]
]

menu_def:list = [
    [f'&{lang["menu"]["option"]}', [f'&{lang["menu"]["lang"]}', all_lang, '---', f'&{lang["menu"]["close"]}']]
]
#define layout
layout:list = [
    [sg.Menu(menu_def, background_color='lightsteelblue', text_color='navy', disabled_text_color='yellow', font='Verdana', pad=(10, 10))],
    [
        sg.Column(layout_menu, key='menu',visible=True), 
        sg.Column(layout_category, key='category',visible=False),
        sg.Column(layout_option_mode, key='mode',visible=False),
        sg.Column(layout_quest, key='quest',visible=False),
        sg.Column(layout_responce, key='responce', visible=False),
        sg.Column(layout_total, key='total', visible=False)
    ]
]

# Create the window
window:sg.Window = sg.Window(lang["menu"]["name"], layout, finalize=True, size=(600,300), grab_anywhere=True, element_justification='c')
window.bind("<Return>", "+Enter+")
window.bind("<Escape>", "-Escape-")


def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    python = sys.executable
    os.execl(python, python, *sys.argv)


def getCombinations(seq:list) -> list:
    combinations:list = []
    for i in range(0, len(seq)):
        for j in range(i+1, len(seq)):
            combinations.append([seq[i], seq[j]])
            combinations.append([seq[j], seq[i]])
    return combinations

selected_categorie: dict = {}
selected_mode:list[str] = []
list_word:list[list] = []
id_quest : int = 0
good_answer:int = 0
event: str
values: dict

# Create an event loop
while True:
    event, values = window.read()
    print(event,values)
    # End program if user closes window or
    # presses the OK button

    if event == lang["menu"]["close"] or event == sg.WIN_CLOSED:
        break

    elif event in all_lang:
        config["lang"] = event[:2]
        with open("config.json","w") as file:
            json.dump(config,file)
        restart_program()
    
    elif event == lang["menu"]["vocabulary"]:
        window["menu"].update(visible=False)
        window["category"].update(visible=True)
    
    elif (event == "+Enter+" or event.startswith(lang["menu"]["continue"])) and window["category"].visible and values["cat"] != []:
        selected_categorie= category[convert_title_category[values["cat"][0]]]
        window["category"].update(visible=False)
        window["mode"].update(visible = True)
        option_mode=[]
        for i in getCombinations(selected_categorie["language"]):
            option_mode.append(equivalence_lang[i[0]]+f" {lang['menu']['to']} "+equivalence_lang[i[1]])
        option_mode.append(lang["menu"]["random"])
        window["option_mode"].update(values=option_mode)
    
    elif (event.startswith(lang["menu"]["continue"]) or event == "+Enter+") and values["option_mode"] != "":
        selected_mode = [f[:2] for f in values["option_mode"].split(" "+lang['menu']['to']+" ")]
        option_mode = []
        for i in getCombinations(selected_categorie["language"]):
            option_mode.append(
                equivalence_lang[i[0]]+f" {lang['menu']['to']} "+equivalence_lang[i[1]])
        option_mode.append(lang["menu"]["random"])
        window["option_mode"].update(values=option_mode)
        window["mode"].update(visible=False)
        window["quest"].update(visible=True)
        list_word = selected_categorie["list_word"]
        random.shuffle(list_word)
        if selected_mode == [lang["menu"]["random"][:2]]:
            for i in list_word:
                random.shuffle(i)
        elif selected_mode != selected_categorie["language"]:
            for i in list_word:
                i.reverse()
        window["question"].update(value=list_word[id_quest][0])
    
    elif (event == "+Enter+" or event.startswith(lang["menu"]["submit"])) and values["answer"] != "" and not window["responce"].visible:
        window["quest"].update(visible=False)
        window["answer"].update(value="")
        window["responce"].update(visible=True)
        if values["answer"] == list_word[id_quest][1]:
            window["resp"].update(value=lang["menu"]["good_answer"])
            good_answer+=1
        else:
            window["resp"].update(value=lang["menu"]["bad_answer"]+list_word[id_quest][1])
    
    elif (event.startswith(lang["menu"]["continue"]) or event == "+Enter+") and window["responce"].visible:
        id_quest+=1
        if id_quest!=len(list_word):
            window["question"].update(value=list_word[id_quest][0])
            window["quest"].update(visible=True)
            window["responce"].update(visible=False)
        else:
            window["responce"].update(visible=False)
            window["total"].update(visible=True)
            window["ratio"].update(value=lang["menu"]["score"]+str(good_answer)+"/"+str(len(list_word)))
    
    elif (event.startswith(lang["menu"]["continue"]) or event == "+Enter+") and window["total"].visible == True:
        window["total"].update(visible=False)
        window["category"].update(visible=True)
        id_quest = 0
        good_answer = 0

    elif (event == lang["menu"]["back"] or event == "-Escape-") and window["category"].visible:
        window["category"].update(visible=False)
        window["menu"].update(visible=True)

    elif (event.startswith(lang["menu"]["back"]) or event == "-Escape-") and window["mode"].visible:
        window["mode"].update(visible=False)
        window["category"].update(visible=True)

window.close()
