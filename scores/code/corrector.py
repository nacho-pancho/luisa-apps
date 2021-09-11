#-*- coding:utf-8 -*-
import sys

import dicsearch               # archivo local
import nltk
import ngram


#=============================================================================

WORD        = 0
WHITESPACE  = 1
PUNCTUATION = 2
NUMBER      = 3
SYMBOL      = 4
GARBAGE     = 5 #should not appear in normal text

# signal special cases during correction
#
CORRECTION_OK  =  0
TOO_FEW_WORDS  =  1
TOO_MANY_SHORT=  2 # often happens in garbage OCR

chartype = { ' ':WHITESPACE,
             '\t': WHITESPACE,
             '\n': WHITESPACE,
             '\r': WHITESPACE,
             ',' : PUNCTUATION,
             ';' : PUNCTUATION,
             ':' : PUNCTUATION,
             '.' : PUNCTUATION,
             'á' : WORD,
             'é' : WORD,
             'í' : WORD,
             'ó' : WORD,
             'ú' : WORD,
             'ü' : WORD,
             'Á' : WORD,
             'É' : WORD,
             'Í' : WORD,
             'Ó' : WORD,
             'Ú' : WORD,
             'Ü' : WORD,
             'ñ' : WORD,
             'Ñ' : WORD,
             '\'': PUNCTUATION,
             '"' : PUNCTUATION,
             '(' : PUNCTUATION,
             ')' : PUNCTUATION,
             '[' : PUNCTUATION,
             ']' : PUNCTUATION,
             '{' : PUNCTUATION,
             '}' : PUNCTUATION,
             '?' : PUNCTUATION,
             '¿' : PUNCTUATION,
             '!' : PUNCTUATION,
             '_' : PUNCTUATION,
             '“' : PUNCTUATION,
             '─' : PUNCTUATION,
             '—' : PUNCTUATION,
             '0' : NUMBER,
             '1' : NUMBER,
             '2' : NUMBER,
             '3' : NUMBER,
             '4' : NUMBER,
             '5' : NUMBER,
             '6' : NUMBER,
             '7' : NUMBER,
             '8' : NUMBER,
             '9' : NUMBER,
             '=' : SYMBOL,
             '+' : SYMBOL,
             '-' : SYMBOL,
             '*' : SYMBOL,
             '/' : SYMBOL,
             '<' : SYMBOL,
             '>' : SYMBOL,
             '%' : SYMBOL,
             '$' : SYMBOL,
             '°' : SYMBOL
             }

for c in range(ord('A'),ord('Z')+1):
    chartype[chr(c)] = WORD

for c in range(ord('a'),ord('z')+1):
    chartype[chr(c)] = WORD

#=============================================================================

def conservative_tokenizer(text_line):
    '''
    this is very slow, but doesn't matter compared to the cost
    of the rest (especially to the OCR)
    '''
    tokens = list()
    i = 0
    n = len(text_line)

    if n == 0:
        # nothing to do:
        return text_line

    # first character
    c = text_line[0]
    if c not in chartype:
        token_type = GARBAGE
    else:
        token_type = chartype[c]

    token_list = list()
    token = list()
    token.append(c)

    for c in text_line[1:]:
        if c not in chartype:
            new_token_type = GARBAGE
        else:
            new_token_type = chartype[c]
        if new_token_type != token_type:
            # new token
            token_list.append( (''.join(token), token_type) )
            # save previous token
            token_type = new_token_type
            token = list()
        token.append(c)

    # trailing token
    if len(token):
        token_list.append((''.join(token), token_type))

    return token_list


#=============================================================================

class Corrector:

    def __init__(self,dict_file):
        

        with open(dict_file, "r", encoding="utf-8") as word_file:
            self.list_of_words = sorted(set(word.strip().split(sep=' \n\t\r')[0].lower() for word in word_file))
            self.searcher = dicsearch.DicSearch(self.list_of_words)

    #--------------------------------------------------------------------------

    def __correct_word(self,word,max_dist,debug=False):
        if len(word) <= 1:
            return (word,0)
        lword = word.lower()
        lmap = [ i != j for i,j in zip(word,lword) ]
        matches = self.searcher.search(lword,max_dist)
        # sort matches by distance
        if len(matches):
            matches = sorted(matches, key=lambda x: x[1])
            if debug:
                print('matches:',matches)
            clword,dist = matches[0]
            #if dist > 0:
            #    min_dist_matches = [m for m in matches if m[1] == dist]
            #    if len(min_dist_matches) > 1:
            #        # more than 1 match with minimum distance
            #        # need to solve tie
            #        #scores 
                
            # undo case conversion
            cword = [ c.upper() if t else c for c,t in zip(clword,lmap)] 
            return (''.join(cword),dist)
        else:
            if debug:
                print('no match for',word)
            return (word,1000)

    #--------------------------------------------------------------------------
    

    def __isalpha(self,i):
        #i = ord(c)
        return ((i >= 'A') and (i <= 'Z')) or ((i >= 'a') and (i <= 'z')) or (i in self.letras_spa)

    #--------------------------------------------------------------------------


    #--------------------------------------------------------------------------

    def correct_line(self,text_line,ignore_tails=False,debug=False):
        input_token_list = conservative_tokenizer(text_line)
        if debug:
            print(input_token_list)

        ntokens = len(input_token_list)
        if ntokens == 0:
            return text_line,0,TOO_FEW_WORDS

        output  = list()
        total_error = 0
        error_code = CORRECTION_OK
        nwords = len([ w for w,k in input_token_list if k == WORD])
       
        if nwords == 0:
            return text_line,0,TOO_FEW_WORDS

        # too few words
        if ignore_tails and input_token_list[0][1] == WORD:
            nwords -= 1

        if ignore_tails and input_token_list[-1][1] == WORD:
            nwords -= 1

        if nwords < 1:
            return text_line,0,TOO_FEW_WORDS

        # enough words
        nshort = 0
        nsingle = 0
        for i,(tok,typ) in enumerate(input_token_list):

            if ignore_tails and typ != WHITESPACE and (i == 0 or i == ntokens - 1):
                output.append(tok)
                continue

            if typ == GARBAGE:
                total_error += len(tok)
                output.append(tok)

            elif typ == WORD:

                if len(tok) == 1:
                    nsingle += 1
                    output.append(tok)
                    continue

                if len(tok) < 3:
                    nshort += 1

                max_dist = len(tok)//4 # allow more corrections for larger words
                corrected_tok, tok_err = self.__correct_word(tok,max_dist,debug)

                if tok_err > max_dist:
                    total_error += len(tok)
                else:
                    total_error += tok_err
                output.append(corrected_tok)

            else:
                output.append(tok)

        #print(nwords,nshort,nsingle)
        # over 1/3 are single letter words
        if 3*nsingle > nwords:
            error_code = TOO_MANY_SHORT
        # over 2/3 are double letter words
        if 3*nshort > 2*nwords:
            error_code = TOO_MANY_SHORT

        return ''.join(output), total_error, error_code

#=============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        text = "con las luchas por la democracia en el Uruguay."
    else:
        text = sys.argv[1]
    print("original text:",text)
    print("length:",len(text))
    corr = Corrector('/luisa/diccionarios/todo.txt')
    ctext,err,code = corr.correct_line(text,ignore_tails=True,debug=True)
    print("corrected text:",ctext,"errors:",err,"code:",code)
