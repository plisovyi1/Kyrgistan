
import glob
import csv
import numpy as np
import pandas as pd
import re
from langdetect import detect
import datetime
#import send_email
import openpyxl
import multiprocessing
from multiprocessing.pool import ThreadPool
import threading
from concurrent.futures import ThreadPoolExecutor




def scroop_doc(data, key_terms, excpetion_terms):

    dict_return = []
    dict_return = dict(dict_return)
    for word in data.split():
        if any (x in word for x in key_terms):
            word = word.replace(',', '')
            if any (x in word for x in excpetion_terms):
                continue
            else:
                if word in dict_return:
                    dict_return[word] += 1
                else:
                    dict_return[word] = 1
    return str(dict_return)

def occurances(data, key_terms, excpetion_terms):
    word_found = "---"
    already_found = []

    number_of_occurances = 0
    number_non_unique_occurances = 0
    for word in data.split():
        if any (x in word for x in key_terms):
            word = word.replace(',', '')
            if any (x in word for x in excpetion_terms):
                continue
            else:
                number_non_unique_occurances = number_non_unique_occurances + 1
                if any (x in word for x in already_found):
                    continue
                else:
                    number_of_occurances = number_of_occurances + 1
                    already_found.append(word)
    return number_of_occurances, number_non_unique_occurances

def occurances_ration(data, key_terms, excpetion_terms):
    word_found = "---"

    #begin_title = data.find("<title>")
    #end_title = data.find("</title>")
    #begin_body = data.find("<pre>")
    #end_body = data.find("</pre>")
    #data = data[begin_title:end_title] + " " + data[begin_body:end_body]
    number_of_occurances = 0
    for word in data.split():
        if any (x in word for x in key_terms):
            word = word.replace(',', '')
            if any (x in word for x in excpetion_terms):
                continue
            else:
                number_of_occurances = number_of_occurances + 1
    return ((1000.0 * number_of_occurances)/(int(len(data.split())+1)))


def selector(name, key_terms, excpetion_terms):
    word_found = "---"
    counter = []
    for i in range(0, len(key_terms)):
        counter.append(0)

    with open (name, "r") as myfile:
        data=myfile.read()
        for word in data.split():
            if any (x in word for x in key_terms):
                for i in key_terms:
                    if (i == word):
                        counter[key_terms.index(i)] +=1
    return(key_terms[counter.index(max(counter))] + str(counter.index(max(counter)) - counter.index(min(counter))))

def which_year(title):
    try:
        data = title
        start_index = data.find("от") + 3
        p = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
        end_index = data.find(p[0]) + 4
        if (start_index != -1 and len(data) > 1):
            if (start_index < end_index):
                data = data[start_index:end_index]
            else:
                number_index = data.find("№")
                if (start_index < number_index):
                    data = data[start_index:number_index]
        if (len(data) > 30):
            p = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
            end_index = data.find(p[0]) + 4
            start_index = end_index - 30
            data = data[start_index:end_index]
            m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)
            if(len(m) < 1):
                m = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
            start_index_month = data.find(m[0])
            end_index = len(data)
            data = data[start_index_month:end_index]
        m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)
        if(len(data) == 4):
            numero_index = title.find(" от ")
            data = title[numero_index:len(title)]
            numero_index = data.find("№")
            data = data[0:numero_index]
            m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)
            start_index_month = data.find(m[0])
            data = data[start_index_month:len(data)]
        if (data[(len(data) - 3)].isdigit()):
            year = data[len(data) - 4: len(data)]
        else:
            year = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)[0]
        return year
    except:
        return ("N/A")
def which_title(data):
    try:
        data = re.sub("[&][a-zA-Z]+", "", data)
        full_descrition_index = data.find(";О")
        #filter out semicolon if it appears as first character
        if (full_descrition_index != -1):
            data = data[full_descrition_index + 1:len(data)]
        if (data[0] == ';'):
            data = data[1:len(data)]
        return data
    except:
        print("Unable title")
        return "Unable"

def which_month(data):
    month = " "
    if (data.find("янва") != -1):
        month = "01"
    elif (data.find("февр") != -1):
        month = "02"
    elif (data.find("март") != -1):
        month = "03"
    elif (data.find("апрел") != -1):
        month = "04"
    elif (data.find("ай") != -1 or data.find("ая") != -1):
        month = "05"
    elif (data.find("июн") != -1):
        month = "06"
    elif (data.find("июл") != -1):
        month = "07"
    elif (data.find("август") != -1):
        month = "08"
    elif (data.find("сентябр") != -1):
        month = "09"
    elif (data.find("октябр") != -1):
        month = "10"
    elif (data.find("ноябр") != -1):
        month = "11"
    elif (data.find("декабр") != -1):
        month = "12"
    else:
        month = "NA"
    return month

def which_date(title, all_data):
    if ("в редакции законов" in all_data or "в редакции закона" in all_data):
        try:
            cyrilic_data = re.sub('[A-z]', '', all_data)
            left = cyrilic_data.find("в редакции законов")
            if (left == -1):
                left = cyrilic_data.find("в редакции закона")
            cyrilic_data = cyrilic_data[left:]
            right = cyrilic_data.find(')')
            cyrilic_data = cyrilic_data[:right]
            left = cyrilic_data.rfind(',')
            if (left != -1):
                cyrilic_data = cyrilic_data[left:]
            number_index = cyrilic_data.find('года')
            cyrilic_data = cyrilic_data[:number_index]
            cyrilic_data = re.sub('[</>]', '', cyrilic_data)
            number_index = cyrilic_data.rfind("\"")
            cyrilic_data = cyrilic_data[number_index + 1:]
            p = re.findall(r"(?<!\d)\d{4,4}(?!\d)", cyrilic_data)
            year = p[0]
            month = which_month(cyrilic_data)
            p = re.findall(r"(?<!\d)\d{2,2}(?!\d)", cyrilic_data)
            day = p[0]
            to_return = str(year) + str('/') + month + str('/') + str(day)
            print(to_return)
            return to_return
        except:
            pass
    else:
        try:
            data = title
            start_index = data.find("от") + 3
            p = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
            end_index = data.find(p[0]) + 4
            if (start_index != -1 and len(data) > 1):
                if (start_index < end_index):
                    data = data[start_index:end_index]
                else:
                   number_index = data.find("№")
                   if (start_index < number_index):
                       data = data[start_index:number_index]

            if (len(data) > 30):
                p = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
                end_index = data.find(p[0]) + 4
                start_index = end_index - 30
                data = data[start_index:end_index]
                m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)
                if(len(m) < 1):
                    m = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)
                start_index_month = data.find(m[0])
                end_index = len(data)
                data = data[start_index_month:end_index]


            m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)

            if(len(data) == 4):
                numero_index = title.find(" от ")
                data = title[numero_index:len(title)]
                numero_index = data.find("№")
                data = data[0:numero_index]
                m = re.findall(r"(?<!\d)\d{1,2}(?!\d)", data)
                start_index_month = data.find(m[0])
                data = data[start_index_month:len(data)]
            start_index_month = data.find(m[0])
            date = 100
            #date is 2 characters long
            if (data[1].isdigit() == True):
                date = data[0:2]
            else:
                date = data[0]
            if (data[(len(data) - 3)].isdigit()):
                year = data[len(data) - 4: len(data)]
            else:
                year = re.findall(r"(?<!\d)\d{4,4}(?!\d)", data)[0]

            month = " "
            month = which_month(data)
            data = year + "/" + month + "/" + date
            return data
        except:
            try:
                index_begin = [i for i in range(len(all_data)) if all_data.startswith('от ', i)]
                index_end = [i for i in range(len(all_data)) if all_data.startswith(' года', i)]
                index_numer1 = [i for i in range(len(all_data)) if all_data.startswith('№', i)]
                index_numer2 = [i for i in range(len(all_data)) if all_data.startswith(' N ', i)]
                index_numer3 = [i for i in range(len(all_data)) if all_data.startswith(' n ', i)]
                potential_matches = []
                for begin_a in range (0, len(index_begin),1):
                    for end_a in range (0, len(index_end), 1):
                        if (abs(index_end[end_a] - index_begin[begin_a]) < 20):
                            potential_matches.append(index_begin[begin_a])


                minimum_distance = 10000
                best_match = 1000
                best_match_number = 100000
                if (len(index_numer1) > 0):
                    for potential_a in range (0, len(potential_matches), 1):
                        for numer1_a in range (0, len(index_numer1), 1):
                            if (abs(index_numer1[numer1_a] - potential_matches[potential_a]) < minimum_distance):
                                minimum_distance = abs(index_numer1[numer1_a] - potential_matches[potential_a])
                                best_match = potential_matches[potential_a]
                                best_match_number = index_numer1[numer1_a]
                elif (len(index_numer2) > 0):
                    for potential_a in range (0, len(potential_matches), 1):
                        for numer2_a in range (0, len(index_numer2), 1):
                            if (abs(index_numer2[numer2_a] - potential_matches[potential_a]) < minimum_distance):
                                minimum_distance = abs(index_numer2[numer2_a] - potential_matches[potential_a])
                                best_match = potential_matches[potential_a]
                                best_match_number = index_numer2[numer2_a]
                elif (len(index_numer3) > 0):
                    for potential_a in range (0, len(potential_matches), 1):
                        for numer3_a in range (0, len(index_numer3), 1):
                            if (abs(index_numer3[numer3_a] - potential_matches[potential_a]) < minimum_distance):
                                minimum_distance = abs(index_numer3[numer3_a] - potential_matches[potential_a])
                                best_match = potential_matches[potential_a]
                                best_match_number = index_numer3[numer3_a]
                else:
                    return "N/A"
                if(minimum_distance > 100):
                    all_data = all_data[best_match:best_match + 50]
                else:
                    all_data = all_data[best_match:best_match_number]
                month = which_month(all_data)
                date_occurance = re.findall(r"(?<!\d)\d{1,2}(?!\d)", all_data)
                date = date_occurance[0]
                year_occurance = re.findall(r"(?<!\d)\d{4,4}(?!\d)", all_data)
                year = year_occurance[0]
                data = str(year) + "/" + str(month) + "/" + str(date)
                return data
            except:
                return "N/A"

def which_language(title):
    try:
        lang = detect(title)
        return lang
    except:
        return "Unable"


def which_law_number(title, data):

    if ("в редакции законов" in data or "в редакции закона" in data):
        try:
            cyrilic_data = re.sub('[A-z]', '', data)
            left = cyrilic_data.find("в редакции законов")
            if (left == -1):
                left = cyrilic_data.find("в редакции закона")
            cyrilic_data = cyrilic_data[left:]
            right = cyrilic_data.find(')')
            cyrilic_data = cyrilic_data[:right]
            left = cyrilic_data.rfind(',')
            if (left != -1):
                cyrilic_data = cyrilic_data[left:]
            number_index = cyrilic_data.find('года')
            if (number_index != -1):
                number_index += 5
            if(number_index == -1):
                number_index = cyrilic_data.find('N')
            if(number_index == -1):
                number_index = cyrilic_data.find('n')
            cyrilic_data = cyrilic_data[number_index:]
            cyrilic_data = re.sub('[</>]', '', cyrilic_data)
            return cyrilic_data
        except:
            pass
    else:
        try:
            start_index_num = title.find("№")
            start_index_and = title.find("&")
            if ((start_index_and == -1 and start_index_and != 0) or start_index_num > start_index_and):
                start_index_and = len(title)
            if (start_index_num == -1):
                title = title[0:start_index_and]
                start_index_num = title.find("№")
                if (start_index_num == -1):
                    start_index_num = title.find("N")
                if (start_index_num == -1):
                    start_index_num = title.find("n")
                    if(start_index_num != -1):
                        title = title.replace('n', '№')
                if(start_index_num != -1):
                    data = title[start_index_num:len(data)]
                    start_index_and = data.find("</")
                    data = data[0:start_index_and]
                    data = re.sub('[&()]', '', data)
                    return data
                else:
                    start_index_num = data.find("№")
                if(start_index_num == -1):
                    start_index_num = data.find(" N ")
                if (start_index_num == -1):
                    start_index_num = data.find("n")
                    if(start_index_num != -1):
                        title = data.replace('n', '№')
                data = data[start_index_num:start_index_num + 20]
                start_index_and = data.find("</")
                data = data[0:start_index_and]
                data = re.sub('[&()]', '', data)
                return data
            title = title[start_index_num:start_index_and]
            title = re.sub('[&()]', '', title)
            return title
        except:
            return "N/A"



def which_type(title):
    type_dictionary = ["акт","государственный стандарт", "декларация", "декрет", "договор", "доклад", "доктрина", "заключение", "закон", "законопроект",
                       "заявление", "инструкция", "исследование", "классификатор", "классификация", "кодекс", "конвенция", "конституция", "концепция", "матрица", "меморандум",
                       "мероприятия", "методика", "методические указания", "механизм", "модель", "направления", "номенклатура", "нормативы", "основные принципы",
                       "перечень", "письмо", "план", "политика", "положение", "порядок", "постановление", "правила", "приказ", "программа", "проект", "проект",
                       "протокол", "распоряжение", "регламент", "регламент", "реестр", "рекомендация", "решение", "руководство", "руководящий документ", "свод",
                       "соглашение", "ставки", "стандарт", "стратегия", "требования", "указ", "указания", "устав"]

    type_needed = ["title"]
    internal_list = []
    actual_title = ""
    final = "aa"
    try:
        actual_title = title.lower()
        for x in type_dictionary:
            if (x in actual_title):
                final = x
    except:
        print("can't open " + filen)
        return "NotFound"
    if (final != "aa"):
        return final
    else:
        return "NotFound"

def state_of_law(data, name):
    underscore = name.rfind('_')
    forwardslash = name.rfind('/') + 1
    copy_name = name
    #name = name[forwardslash:underscore] + str('_')
    #tifCounter = len(glob.glob1("../files2/", name + "*"))

    #data = re.sub('[A-z&/<>;:=-?"\']', '', data)
    to_return = ""
    dot = copy_name.rfind('.')
    copy_name = copy_name[underscore+1:dot]
    if (len(data) > 3000):
        data = data[:3000]
    if (copy_name == "10"):
        #Questionable
        to_return = "оригинал"
    elif ("утратил силу" in data):
        to_return += "утратил силу"
    elif ("в редакции закона" in data or "в редакции законов"):
        to_return += " в редакции закона"



    return to_return




def check(name, index):
    global original_date
    global original_law
    excpetion_terms = ["ташкилотининг", "чекадилар", "ташкилотининг",
                       "маҳсулотини", "чекади", "хокимами",
                       "тўкадиган", "таъминотини", "хатибошиси",
                       "ҳисоботини", "хатиблари",
                       "эр-хотинлар", "ташкилотини", "эр-хотинлар", "ҳисоботини",
                       "тақдимотини", "тартиботининг", "ҳисоботини", "Нотукимамато",
                       "Абдикадирович", "Маматкадировича", "Аркади",
                       "Таджимамату",
                       "зажимами", "тартиботини", "Бурчмуллинского",
                       "Бурчмуллинского", "Бурчмулла", "антиникотинового",
                       "гильотинные", "зажимам", "зажимам",
                       "штангенциркулем", "долотининг", "пулемёт", "чўкадиган",
                       "гильотинного", "тафсилотини", "штангенциркулем", "цефалотин",
                       "матбуотини", "жумаба", "преподавател", "создав",
                       "курманб", "намазбек", "выдават", "давать", "имамал", "абдикадиров", "мамбетказ", "аев",
                       "джумалиевой", "нурказиевича", "абдыкадиров",
                       "сейитказиевну", "намазова", "абдукадиров", "курманалиевн", "джумакадыров", "кадиров",
                       "хожимаматович", "тожимаматовна", "курманалиевич", "ову", "имамалиеву", "ташкилотининг", "чекадилар",
                       "чекади", "хокимами",
                       "тўкадиган", "таъминотини", "хатибошиси", "хатиблари", "ахборотини",
                       "эр-хотинлар", "ташкилотини", "эр-хотинлар",
                       "мукофотини", "тартиботининг", "ҳисоботини", "Нотукимамато",
                       "Абдикадирович", "Маматкадировича",
                       "Таджимамату", "никотиновой",
                       "зажимами", "тартиботини", "Бурчмуллинского",
                       "Бурчмуллинского", "Бурчмулла", "антиникотинового",
                       "гильотинные", "зажимам", "зажимам",
                       "штангенциркулем", "пулемёт", "чўкадиган",
                       "гильотинного", "тафсилотини", "штангенциркулем", "тожимаматовна", "вна", "вая", "силикриотин", "нико", "пулеме",
                       "учет", "радиоактив", "нбек", "суфибека", "сказителей", "тажимамат", "вич", "казино", "рулем", "муллит", "джумановну", "намазалиеву", "казилу", "ханафитский", "намазкан",
                       "исламская республика пакистан", "исламская республика иран"]
    key_terms = ["религ", "мусульман", "ислам", "муфти", "улем", "имам", "мечет", "хиджаб", "фатва", "кади", "шейх", "мулл", " отин ", "гадалка", "фолбин", "проповедь", "хутба", "тарика", "суфи", "джамаат" "таблигa", "хизб ут-тахрир", "ахмади", "ханафи", "православ", "баптист", "свидетели иегов", "мазхаб", "махтаб", "медрес", "мадрас", "муфти", "головной платок", "рамадан", "орозо-айт", "курман", "байрам", "обрезание", "суннат", "паломничеств", "хадж", "хутбе", "хутба", "мазар", "намаз", "джума", "халяль", "зикр", "даават", "дават", "джихад", "шариа", "кази", "ханафи", "христианин",
        " думк ", "духовное управление мусульман", "государственная комиссия по делам религ"]


    data = " "
    with open (name, "r") as myfile:
        data=myfile.read()
    data = data.lower()
    cyrilic_data = re.sub('[A-z&#<>;/\="-:%]', '', data)

    matches, non_unique_occurances = occurances(cyrilic_data, key_terms, excpetion_terms)
    #if (matches == 0):
        #a[index + 1][2] = 0
        #return


    a[index + 1][1] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][2] = matches
    a[index + 1][3] = non_unique_occurances
    a[index + 1][4] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)


    key_terms = ["мусульманский совет", "комитет по делам религи", "комитет по религи",
                 "государственная религиоведческая экспертиза", "религиоведческая", "государственная комиссия по делам религ",
                 " думк ", "духовное управление мусульман"]
    a[index + 1][42] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][41], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][7] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)



    key_terms = ["улем", "имам", "хатиб", "муфтий", "фатва", "кади", "шейх", "мулл", "отин", "гадалка",
                  "фолбин", "проповед", "хутба"]

    a[index + 1][8] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][9], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][10] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["учет", "религиозные организации", "религиозная организация", "религиозные политические партии",
                  "религиозная политическая партия", "тарика", "суфи", "джамаат", "таблигa", "хизб ут-тахрир",
                  "тахрир", "исламское движение узбекистана", "исламского движения узбекистана", "ахмади",
                  "ханафи", "православ", "баптист", "свидетели иеговы"]
    a[index + 1][11] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][12], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][13] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["мазхаб", "махтаб", "мазхаб", "медрес",
                  "мадрас", "муфти", "мулл", "исламский университет", "религиозное образование"]
    a[index + 1][14] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][15], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][16] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["религиозного содержания", "религиозная литература", "религиозные публикации",
                  "религиозная публикация","сайты", "брошюр", "листовок", "радио",
                  "телев", "запис", "аудиокассет"]
    a[index + 1][17] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][18], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][19] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["религиозное убрание", "религиозная одежд", "хиджаб", "бород",
                  "головной платок", "чолпон", "рамадан", "орозо-айт",
                  "орозо", "курман", "байрам", "религиозные церемонии",
                  "религиозные праздники", "свадьб", "похорон", "обрезание",
                  "суннат"]
    a[index + 1][20] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][21], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][22] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["паломничеств", "хадж", "святын", "зийарат",
                  "зиярат", "посещение мечети", "мазар", "проповед",
                  "хутбе", "хутба", "джума́-нама́з", "джума",
                  "молитва", "пост", "халяль", "зикр",
                  "даават", "дават"]
    a[index + 1][23] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][24], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][25] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    key_terms = ["экстрем", "террор", "религиозное насилие", "религиозная ненависть",
                  "религиозное превосходство", "шариа", "джихад"]
    a[index + 1][26] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][27], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][28] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)


    key_terms = ["предупреждение", "штраф", "тюремный срок", "тюремного срока",
                  "запрет", "ликвидац", "задерж", "арест"]
    a[index + 1][29] = scroop_doc(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][30], dummy = occurances(cyrilic_data, key_terms, excpetion_terms)
    a[index + 1][31] = occurances_ration(cyrilic_data, key_terms, excpetion_terms)

    begin_title = data.find("<title>") + 7
    end_title = data.find("</title>")
    title = data[begin_title:end_title]
    a[index + 1][34] = which_type(title)
    a[index + 1][35] = which_title(title)
    a[index + 1][36] = which_date(title, data)
    try:
        a[index + 1][33] = a[index + 1][36][0:4]
    except:
        a[index + 1][33] = "N/A"

    a[index + 1][32] = which_language(title)
    a[index + 1][37] = which_law_number(title, data)
    a[index + 1][38] = scroop_doc(title, key_terms, excpetion_terms)
    a[index + 1][39], dummy = occurances(title, key_terms, excpetion_terms)
    a[index + 1][40] = state_of_law(data, name)
    if (a[index + 1][40] == "утратил силу" or a[index + 1][40] == "утратил силу в редакции закона"):
        a[index + 1][42] = "утратил силу"
        for prev_row in range (index + 2 - int(a[index + 1][41]), index + 1, 1):
            a[prev_row][42] = "утратит силу"
    if (a[index + 1][40] == "оригинал"):
        original_date = a[index + 1][36]
        original_law = a[index + 1][37]
    a[index + 1][1] = original_date
    a[index + 1][44] = original_law
current_law_name = ""
#globals
original_date = " "
original_law = " "
txtfiles = []
for file in glob.glob("../feb_20191/*.txt"):
    txtfiles.append(file)

txtfiles.sort()
txtfiles.sort(key=len, reverse=False) # sorts by descending length



categories = ["Files", "Religious or not", "Number of occurances", "Non Unique Occurances",
              "Ratio of occurances", "Religious Institutions (Gov’t)", "Number of occurances",
              "Ratio of occurances", "Religious Leaders & Clergy", "Number of occurances",
              "Ratio of occurances", "Religious Organizations (non-Gov’t)","Number of occurances",
              "Ratio of occurances",
              "Religious Education","Number of occurances",
              "Ratio of occurances", "Religious Publications & Media ","Number of occurances",
              "Ratio of occurances",
              "Religious Clothing, Holidays, and Rituals ","Number of occurances",
              "Ratio of occurances", "Religious Practice and Worship","Number of occurances",
              "Ratio of occurances", "Extremism/Terrorism","Number of occurances",
              "Ratio of occurances",
              "Penalties & Punishments","Number of occurances",
              "Ratio of occurances", "language(tentative)", "year", "type of law", "Title", "Date", "Law Number", "Key Terms in Title", "Occurances in Title", "Repealed/Replaced",
              "How Many Versions", "Would Lose Power", "original date", "original law number"]
try:
    a = np.genfromtxt('file_path.csv', delimiter=',')
    print("found in dir")
except:
    a = np.chararray(shape = (len(txtfiles) + 1, len(categories)), itemsize=1100, unicode = True)
    print("creating new array")

a[:] = " "
for i in range (0,len(categories)):
    a[0][i] = categories[i]
for i in range (0,len(txtfiles)):
    #document_number = re.findall(r"(?<!\d)\d{1,10}(?!\d)", txtfiles[i])
    right_slash = txtfiles[i].rfind('/')
    dot = txtfiles[i].rfind('.')
    document_number = txtfiles[i][right_slash:dot]
    document_number = document_number.replace('_', '/')
    document_link = "http://cbd.minjust.gov.kg/act/preview/ru-ru" + document_number
    print(document_link)

    print(document_link)
    a[i + 1][0] = document_link
    document_number = document_number.replace('/', '_',)
    document_number = document_number[1:len(document_number)]
    document_number = document_number + ".txt"
    a[i + 1][0] = document_number


unique_laws = []
previous = 10000000 #random number
version_numbers = 0

for iter, law_name in enumerate (txtfiles):
    print(law_name)
    slash = law_name.rfind('/')
    dot = law_name.rfind('.')
    law_name = law_name[slash + 1:dot]
    underscore = law_name.rfind('_')
    law_name = law_name[:underscore]
    print(law_name + " this is law name")
    law_name = int(law_name)
    if (previous != law_name):
        previous = law_name
        for index in range (iter - version_numbers, iter, 1):
            a[index + 1][6] = version_numbers
        version_numbers = 1
    else:
        version_numbers += 1

    print(law_name)
    print(iter)

threads = []
progress = 0
for i in (txtfiles):
    visual_progress = " "
    temp = 10 * progress/len(txtfiles)
    for j in range (0, int(temp)%10):
        visual_progress+="#"
    check(i, txtfiles.index(i))
    print(str(round(100 * progress/len(txtfiles), 4)) + " % ")
    print(i)




df = pd.DataFrame(a)
df.to_csv("Kyrgistan_all_data.csv")
writer = pd.ExcelWriter('kyrgiz_data.xlsx')
df.to_excel(writer)
writer.save()

for year_sort in range(1990, 2020, 1):
    row_incrementer = 0
    b = np.chararray(shape = (len(txtfiles) + 1, len(categories)), itemsize=1100, unicode = True)
    for row in range (1, len(txtfiles), 1):
        if (a[row][33] == str(year_sort)):
            b[row_incrementer] = a[row].copy()
            row_incrementer += 1
    df = pd.DataFrame(b)
    df.to_csv(str(year_sort) + ".csv")
    writer = pd.ExcelWriter(str(year_sort) + ".xlsx")
    df.to_excel(writer)
    writer.save()


#print(a.dtype)
#print(a)

#send_email.send("lisovyi.pavlo@gmail.com", religious_matches)
#send_email.send("gamza@umich.edu", religious_matches)
#send_email.send("pjluong@umich.edu", religious_matches)
