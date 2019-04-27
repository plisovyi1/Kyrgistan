def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def laws_referencing(data):
    index = data.find("в редакции")
    
    #check whether we are in version area
    if(data[index:index + 300].find("href") == -1):
        return ""
    if (index != -1):
        print(data[index:index + 200])
    data = data[index:len(data)]

    #whatever is closer
    data = data[0:min(data.find("\n\n"), (10000000 if (data.find("</i></p>") == -1) else data.find("</i></p>")))]

    #now we have the links
    #we need to extract references to the laws
    data = data.split("href")
    to_return = ""
    for index, link in enumerate(data):
        link = link[link.find("ru-ru")+6:len(link)]
        link = link[0:link.find("?")]
        if (len(link) > 0 and hasNumbers(link)):
            link = link + "_10.txt, "
            to_return += link
    return to_return





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

