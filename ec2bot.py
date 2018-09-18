from __future__ import print_function, unicode_literals
import random
import logging
import os
import pandas as pd

os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

from textblob import TextBlob
from config import FILTER_WORDS

import nltk

import re
import sys

#nltk.download('punkt')

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

LOCATION_KEY = ["us east", "eu west"]
KEY_WORDS = ["price", "ghz", "memory", "gib", "network"]

def get_best_lines(sentence):
    """
    Takes a list of words and searches a csv file for lines that are similar
    Returns the line/s from csv that have most words in common
    Also returns the number of words in common found
    """
    
    bestlines = []
    blcount = 0
    
    parsed = TextBlob(sentence)
    userinput = parsed.split(" ")
    userinput = list(set(userinput))#remove dupe words
    filelines = []
    
    try:
        fp = open('newtrim.csv', 'r')
        line = fp.readline()
        while line:
            filelines.append(line)
    finally:
        fp.close()
    
    filelines,userinput = filter_on_category("price",sentence, userinput, filelines)
    filelines,userinput = filter_on_category("cpu",sentence, userinput, filelines)
        
    for line in filelines:
            filteredline = " ".join(list(set(line.split(",")))) #remove dupe words in line
            for word in userinput:
                if(re.search(word.lower(), filteredline.lower())):
                    count += 1
            if(count > blcount):
                blcount = count
                bestlines = [line]
            elif(count == blcount):
                bestlines.append(line)
            line = fp.readline()
            count = 0
  
    
    """
    bestlines = []
    blcount = 0
    
    parsed = TextBlob(sentence)
    words = parsed.split(" ")
    words = list(set(words))#remove dupe words
    
    priceflag, relationalop,price,words = set_flag("price",sentence, words)
    cpuflag, cpuop ,numcpu,words = set_flag("cpu",sentence, words)
    
    try:
        fp = open('newtrim.csv', 'r')
        line = fp.readline()
        count = 0
        while line:
            split = " ".join(list(set(line.split(","))))
            for word in words:
                if(re.search(word.lower(), split.lower())):
                    count += 1
            if(count > blcount):
                blcount = count
                bestlines = [line]
            elif(count == blcount):
                bestlines.append(line)
            line = fp.readline()
            count = 0
    finally:
        fp.close()
  
    flagflag = False  
    bl2 = []
    if(priceflag):
        for line in bestlines:
            if (compare_string_op(float(get_price_from_sentence(line)),float(price),relationalop)):
                bl2.append(line)
        return bl2,blcount
    if(cpuflag):
        for line in bestlines:
            if (compare_string_op(float(get_cpu_from_sentence(line)),float(numcpu, cpuop))):
                bl2.append(line)
        return bl2,blcount
    return bestlines,blcount
        """
#def price():
    
def filter_lines(flag,op, num, lines):
    if(priceflag):
            for line in lines:
                if (not compare_string_op(float(get_price_from_sentence(line)),float(price),relationalop)):
                    lines.remove(line)
    return lines
                    
def filter_on_category(category, sentence, words,lines):
    question = has_asked_for_subject(category,sentence)
    if question is not None:
        relop = get_relationalop_in_question(question)
        num = get_number_in_question(question)
        flag = True
        try:
            words.remove(relop)
            words.remove(num)
            words.remove(category)
        except:
            print("probably tried to delete val from words twice")
        for line in lines:
                if (not compare_string_op(float(get_price_from_sentence(line)),float(num),relop)):
                    lines.remove(line)
    return lines, words
    
def is_number(s):
    """
    is the string value a digit
    """
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def has_asked_for_subject(subject, sentence):
    """
    Takes user input as param 
    Check whether user asked for price in input string, 
    if so return price compare part of string and string without price compare
    """
    pattern = subject + "(\s)*([><=]|=[><=]|greater(\s)*(than)?|less(\s)*(than)?)(\s)*\$?(\d)+(\.(\d)+)?"
    match = re.search(pattern,sentence)
    if match is not None:
        return match.group(0)
    return (match)

def get_number_in_question(question):
    """
    Reads question and returns the mentioned price
    """
    number = []
    for i in range(len(question)-1,0,-1):
        if(is_number(question[i]) or question[i] == "."):
            number.insert(0,question[i])
        else:
            break
    return "".join(number)

def get_relationalop_in_question(question):
    """
    Reads question and returns relational operator as string
    """
    operator = ""
    pattern = "(greater(\s)*(than)?)|(less(\s)*(than)?)"
    match = re.search(pattern, question.lower())
    if match is not None:
        return match.group(0)
    for i in range(0,len(question)):
        if(question[i] == "<" or question[i] == ">" or question[i] == "="):
            operator += question[i]
        
    return operator

def get_price_from_sentence(sentence):
    s = sentence.split(",")
    return s[6]
    
def get_cpu_from_sentence(sentence):
    s = sentence.split(",")
    return s[18]

def compare_string_op(price1,price2,operator):
    operator = operator.strip()
    if(price1 is not None and price2 is not None):
        if (operator == "<" or operator == "less" or operator == "less than"):
            return price1 < price2 
        if (operator == ">" or operator == "greater" or operator == "greater than"):
            #print("this should print")
            return price1 > price2 
        if (operator == ">="):
            return price1 >= price2 
        if (operator == "<="):
            return price1 <= price2 
        if (operator == "="):
            return price1 == price2 
    return False  

def respond(sentence):
    bestlines,blcount = get_best_lines(sentence)
    i = 0
    for line in bestlines:
        print(line + "Number of keywords in common " + str(blcount) + "\n")
        i += 1
        if i > 3:
            print("Only showing top 4 results.")
            break

def search_csv(file,word):
    file = open(file, "r")
    lines = []
    for line in file:
        if(re.search(word.lower(), line.lower())):
            lines.append(line.lower())
            #print(line,)
    return lines
    
def search_list(thelist, word):
    lines = []
    for line in thelist:
        if(re.search(word.lower(), line.lower())):
            lines.append(line.lower())
    return lines
    
if __name__ == '__main__':
    import sys
    # Usage:
    # python broize.py "I am an engineer"
    if (len(sys.argv) > 0):
        saying = sys.argv[1]
    else:
        saying = "How are you, brobot?"
    respond(saying)
     