import json
from types import NoneType
import PySimpleGUI as sg
from os import listdir
from os.path import isfile, join
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

sg.set_options(dpi_awareness=True)

layout_menu:list = [
    [sg.Text(lang["menu"]["name"])],
    [sg.Button(lang["menu"]["vocabulary"])]
]

edit = False
# ------ Make the Table Data ------
# sg.Print('Creating table...')
data = [["",""]]
# headings = [str(data[0][x])+'     ..' for x in range(len(data[0]))]
headings = category[0]["category"]
# sg.Print('Done creating table.  Creating GUI...')

category_name : list = []

convert_title_category:dict = {}

for i in category:
    if lang["short_name"] in i["language"]:
        convert_title_category[i["title"][lang["short_name"]]] = category.index(i)
        category_name.append(i["title"][lang["short_name"]])

layout_category: list = [
    [sg.Listbox(category_name, key="-category-", select_mode="LISTBOX_SELECT_MODE_SINGLE")],
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

SelectLang = lambda lkey: sg.Input(do_not_clear=True, size=(22,1), key=lkey, pad=(0,2))

layout_make_list = [
    [sg.Text(lang["menu"]["name_file"]), sg.Input(key="name_file",size=(36,1)), sg.Text(".json"), sg.Button(lang["menu"]["open"])],
    [
        sg.Text(lang["menu"]["lang"]+" :"),
        SelectLang("lang1"),
        sg.Text(" "),
        SelectLang("lang2")],
    [
        sg.Text(lang["menu"]["category"]+" :"),
        SelectLang("cat1"),
        sg.Text(" "),
        SelectLang("cat2")],
    [sg.Table(values=data, headings=headings, max_col_width=25,
                        auto_size_columns=True,
                        # display_row_numbers=True,
                        justification='right',
                        alternating_row_color=sg.theme_button_color()[1],
                        key='-TABLE-',
                        # selected_row_colors='red on yellow',
                        # enable_events=True,
                        # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,  # Comment out to not enable header and other clicks
                        )],
    [sg.Button(lang["menu"]["save"]), sg.Button(lang["menu"]["add_line"]),sg.Button(lang["menu"]["exit"])]
]

#define layout
layout:list = [
    [sg.Menu(menu_def, background_color='lightsteelblue', text_color='navy', disabled_text_color='yellow', font='Verdana', pad=(10, 10))],
    [
        sg.Column(layout_menu, key='menu',visible=True, element_justification="center", vertical_alignment='center'), 
        sg.Column(layout_category, key='category',visible=False, element_justification="center", vertical_alignment='center'),
        sg.Column(layout_option_mode, key='mode',visible=False, element_justification="center", vertical_alignment='center'),
        sg.Column(layout_quest, key='quest',visible=False, element_justification="center", vertical_alignment='center'),
        sg.Column(layout_responce, key='responce', visible=False, element_justification="center", vertical_alignment='center'),
        sg.Column(layout_total, key='total', visible=False, element_justification="center", vertical_alignment='center'),
        sg.Column(layout_make_list, key='make_list', visible=False, element_justification="center", vertical_alignment='center')
    ]
]

# Create the window
window: sg.Window = sg.Window(lang["menu"]["name"], layout, finalize=True, element_justification="c", size=(900, 450), font=('Courier', 12))
window.bind("<Return>", "+Enter+")
window.bind("<Escape>", "-Escape-")
window["cat1"].bind("<KeyPress>","update_cat")
window["cat2"].bind("<KeyPress>", "update_cat")

def func():
    pass

def edit_cell(window, key, row, col, justify='right'):

    global textvariable, edit, func

    def callback(event, row, col, text, key, original_key):
        global edit
        if "widget" in event.__dict__:
            widget = event.widget
        else:
            widget = event

        if key == 'Return':
            text = widget.get()
        widget.destroy()
        widget.master.destroy()
        values = window[original_key].Get()
        values[row-1][col] = text
        window[original_key].update(values=values)
        edit = False

    if edit or row <= 0:
        return

    edit = True
    root = window.TKroot
    table = window[key].Widget
    text = window[key].Get()[row-1][col]
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

    add_y += 5
    frame.place(x=x+10, y=y+add_y, anchor="nw", width=width, height=height)
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    entry = sg.tk.Entry(frame, 
                        textvariable=textvariable, 
                        justify=justify, 
                        font=('Courier', 12), 
                        borderwidth=0,
                        highlightthickness=0)
    entry.pack()
    entry.select_range(0, sg.tk.END)
    entry.icursor(sg.tk.END)
    entry.focus_force()
    entry.bind("<Return>", lambda e, r=row, c=col, t=text, k='Return',o=key:callback(e, r, c, t, k, o))
    func = lambda e=entry, r=row, c=col, t=text, k='Return',o=key:callback(e, r, c, t, k, o)
    entry.bind("<Escape>", lambda e, r=row, c=col, t=text, k='Escape',o=key:callback(e, r, c, t, k, o))

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

    if edit and "+CICKED+" in event:
        func()

    if event == lang["menu"]["close"] or event == sg.WIN_CLOSED:
        break

    elif window["make_list"].visible:
        if event == lang["menu"]["add_line"]:
            window["-TABLE-"].update(values=window["-TABLE-"].Get()+[["", ""]])

        elif isinstance(event, tuple):
            row, col = event[2]
            if type(row) != NoneType:
                edit_cell(window, '-TABLE-', row+1, col, justify='right')
        
        elif event == "+Enter+" or event == "cat1update_cat" or event == "cat2update_cat":
            table = window['-TABLE-'].Widget
            headings = [values["cat1"], values["cat2"]]
            for cid, text in zip(window["-TABLE-"].ColumnHeadings, headings):
                table.heading(cid, text=text)

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
    
    elif (event == "+Enter+" or event.startswith(lang["menu"]["continue"])) and window["category"].visible and values["-category-"] != []:
        selected_categorie= category[convert_title_category[values["-category-"][0]]]
        window["category"].update(visible=False)
        window["mode"].update(visible = True)
        option_mode=[]
        for i in getCombinations(selected_categorie["category"]):
            option_mode.append(i[0]+f" {lang['menu']['to']} "+i[1])
        option_mode.append(lang["menu"]["random"])
        window["option_mode"].update(values=option_mode)
    
    elif (event.startswith(lang["menu"]["continue"]) or event == "+Enter+") and values["option_mode"] != "":
        selected_mode = [f for f in values["option_mode"].split(" "+lang['menu']['to']+" ")]
        option_mode = []
        for i in getCombinations(selected_categorie["category"]):
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
        elif selected_mode != selected_categorie["category"]:
            for i in list_word:
                i.reverse()
        window["question"].update(value=lang["menu"]["translate"]+list_word[id_quest][0])
    
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
            window["question"].update(value=lang["menu"]["translate"]+list_word[id_quest][0])
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
