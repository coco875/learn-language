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

edit = False
# ------ Make the Table Data ------
# sg.Print('Creating table...')
data = category[0]["list_word"]
# headings = [str(data[0][x])+'     ..' for x in range(len(data[0]))]
headings = category[0]["language"]
# sg.Print('Done creating table.  Creating GUI...')

category_name : list = []

convert_title_category:dict = {}

for i in category:
    if equivalence_lang[config["lang"]] in i["language"]:
        convert_title_category[i["title"][config["lang"]]] = category.index(i)
        category_name.append(i["title"][config["lang"]])
print(category_name)

layout_category: list = [
    [sg.Listbox(category_name, key="cat", select_mode="LISTBOX_SELECT_MODE_SINGLE")],
    [sg.Button(lang["menu"]["continue"]), sg.Button(lang["menu"]["back"]), sg.Button(lang["menu"]["new_list"])]
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

sg.set_options(dpi_awareness=True)

SelectLang = lambda lkey: sg.Input(do_not_clear=True, size=(22,1), key=lkey, pad=(0,2))

layout_make_list = [
    [sg.Text(lang["menu"]["name_file"]), sg.Input(key="name_file")],
    [
        sg.Text(lang["menu"]["lang"]+" :"),
        SelectLang("lang1"),
        sg.Text(" "),
        SelectLang("lang2")],
    [sg.Table(values=data, headings=headings, max_col_width=25,
                        auto_size_columns=True,
                        # display_row_numbers=True,
                        justification='right',
                        num_rows=20,
                        alternating_row_color=sg.theme_button_color()[1],
                        key='-TABLE-',
                        # selected_row_colors='red on yellow',
                        # enable_events=True,
                        # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,  # Comment out to not enable header and other clicks
                        )]
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
        sg.Column(layout_total, key='total', visible=False),
        sg.Column(layout_make_list, key='make_list', visible=False)
    ]
]

# Create the window
window:sg.Window = sg.Window(lang["menu"]["name"], layout, finalize=True, size=(600,300), grab_anywhere=True, element_justification='c', font=('Courier', 12))
window.bind("<Return>", "+Enter+")
window.bind("<Escape>", "-Escape-")


def edit_cell(window, key, row, col, justify='right'):

    global textvariable, edit

    def callback(event, row, col, text, key):
        global edit
        widget = event.widget
        if key == 'Return':
            text = widget.get()
            print(text)
        widget.destroy()
        widget.master.destroy()
        values = list(table.item(row, 'values'))
        values[col] = text
        table.item(row, values=values)
        edit = False

    if edit or row <= 0:
        return

    edit = True
    root = window.TKroot
    table = window[key].Widget

    text = table.item(row, "values")[col]
    x, y, width, height = table.bbox(row, col)

    frame = sg.tk.Frame(root)
    add_y=0
    for i in layout_make_list:
        y_tmp= 0
        for j in i:
            if j == window[key]:
                break
            y_temp = j.get_size()[1]
            y_tmp = max(y_tmp, y_temp)
        add_y += y_tmp

    add_y += 17
    frame.place(x=x, y=y+add_y, anchor="nw", width=width, height=height)
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify,font=('Courier', 12))
    entry.pack()
    entry.select_range(0, sg.tk.END)
    entry.icursor(sg.tk.END)
    entry.focus_force()
    entry.bind("<Return>", lambda e, r=row, c=col, t=text, k='Return':callback(e, r, c, t, k))
    entry.bind("<Escape>", lambda e, r=row, c=col, t=text, k='Escape':callback(e, r, c, t, k))

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

    elif isinstance(event, tuple):
        row, col = event[2]
        edit_cell(window, '-TABLE-', row+1, col, justify='right')

    elif event in all_lang:
        config["lang"] = event[:2]
        with open("config.json","w") as file:
            json.dump(config,file)
        restart_program()
    
    elif event == lang["menu"]["new_list"]:
        window["category"].update(visible=False)
        window["make_list"].update(visible=True)

    elif event == lang["menu"]["vocabulary"]:
        window["menu"].update(visible=False)
        window["category"].update(visible=True)
    
    elif (event == "+Enter+" or event.startswith(lang["menu"]["continue"])) and window["category"].visible and values["cat"] != []:
        selected_categorie= category[convert_title_category[values["cat"][0]]]
        window["category"].update(visible=False)
        window["mode"].update(visible = True)
        option_mode=[]
        for i in getCombinations(selected_categorie["language"]):
            option_mode.append(i[0]+f" {lang['menu']['to']} "+i[1])
        option_mode.append(lang["menu"]["random"])
        window["option_mode"].update(values=option_mode)
    
    elif (event.startswith(lang["menu"]["continue"]) or event == "+Enter+") and values["option_mode"] != "":
        selected_mode = [f for f in values["option_mode"].split(" "+lang['menu']['to']+" ")]
        option_mode = []
        for i in getCombinations(selected_categorie["language"]):
            option_mode.append(i[0]+f" {lang['menu']['to']} "+i[1])
        option_mode.append(lang["menu"]["random"])
        window["option_mode"].update(values=option_mode)
        window["mode"].update(visible=False)
        window["quest"].update(visible=True)
        list_word = selected_categorie["list_word"]
        random.shuffle(list_word)
        if selected_mode == [lang["menu"]["random"]]:
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
