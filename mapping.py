import stanza
import pandas as pd
import re

# stanza.download('id')
nlp = stanza.Pipeline('id')
templates = pd.read_csv('question-sparql-template.csv')
question_parse = pd.read_csv('question-parse-pattern.csv')

def set_query(query_index, **kwargs):
    query_template = templates[templates['query_index'] == query_index].reset_index(drop=True)['query_template'][0]
    for key, value in kwargs.items():
        query_template = re.sub(key, value.title() if key != "ayat_num" else value, query_template)
    if query_index == 13:
        ayat = kwargs.get('ayat_num')
        if not ayat:
            query_template = re.sub("ayat_num", "", query_template)
    return query_template

def get_legal_target(target_idx, head_values, word_head, text_pos, word_values):
    target = ""
    try:
        if word_head[target_idx] == head_values:
            target_stop = target_idx
            # get the first num
            try:
                first_num_index = text_pos.index("NUM", target_stop)
                target_stop = first_num_index - 1
            except:
                first_num_index = None
            # get second num
            try:
                second_num_index = text_pos.index("NUM", first_num_index + 1)
            except:
                second_num_index = None
            # legal title
            for j in range(len(word_values[target_idx:target_stop])):
                if word_values[target_idx+j][0] in ['/', ',']:
                    target += word_values[target_idx+j][0]
                    target += " " + word_values[target_idx+j][1:] if word_values[target_idx+j][1:] else ""
                else:
                    target += word_values[target_idx+j]
                if word_values[target_idx+j+1][0] not in ['/', ',']:
                    target += " "
            # legal number and year
            if first_num_index and second_num_index:
                if word_values[first_num_index-1] == "nomor" and word_values[second_num_index-1] == "tahun":
                    target += word_values[first_num_index-1] + " " + word_values[first_num_index] \
                            + " " + word_values[second_num_index-1] + " " + word_values[second_num_index]
                elif word_values[first_num_index-1] == "tahun" and word_values[second_num_index-1] == "nomor":
                    target += word_values[second_num_index-1] + " " + word_values[second_num_index] \
                            + " " + word_values[first_num_index-1] + " " + word_values[first_num_index]
            elif first_num_index:
                target += word_values[first_num_index-1] + " " + word_values[first_num_index]
    except:
        pass
    return target.title()

def get_question_type_and_legal_head(root, first, verb):
    target_row = question_parse[(question_parse['root']==root) & 
                                (question_parse['first']==first) & 
                                (question_parse['verb']==verb)].reset_index(drop=True)
    if len(target_row) == 0:
        return
    return {
        'q_type': target_row['q_type'][0],
        'legal_head': target_row['legal_head'][0],
        'legal_rel': target_row['legal_rel'][0]

    }

def mapping(text):
    doc = nlp(text)
    if len(doc.sentences) != 1:
        return ""

    ## POS tagging & dependency parsing result
    words = doc.sentences[0].words
    text_pos = [word.upos for word in words]
    word_values = [word.text.lower() for word in words]
    word_deprel = [word.deprel for word in words]
    word_head = [word_values[word.head - 1] if word.head > 0 else '' for word in words]
    
    # get verb, root, first word
    verb = word_values[text_pos.index("VERB")].lower() if "VERB" in text_pos else ""
    root = word_values[word_deprel.index('root')].lower()
    first = word_values[0].lower()

    question_type = 0
    legal_head = ""
    legal_index = 0
    target_pasal = ""
    target_ayat = ""
    question_info = get_question_type_and_legal_head(root, first, verb)
    if question_info:
        question_type = question_info['q_type']
        legal_head = question_info['legal_head']
        legal_index = word_deprel.index(question_info['legal_rel']) if question_info['legal_rel'] in word_deprel else 0
    else:
        if root == "apa" and first == "apa" and verb == "membuat":
            legal_head = verb
            legal_index = word_deprel.index('obj') if 'obj' in word_deprel else 0
            first_noun = word_values[text_pos.index("NOUN")] if 'NOUN' in  text_pos else ""
            if first_noun == "pertimbangan":
                question_type = 4
            elif first_noun == "hukum":
                question_type = 5
        elif root == "bunyi" and first == "bagaimana" and verb == "":
            if 'pasal' in word_values:
                index_pasal = word_values.index("pasal")
                if text_pos[index_pasal+1] == "NUM":
                    target_pasal += "pasal" + " " + word_values[index_pasal+1] 
            if target_pasal != "":
                if 'ayat' in word_values:
                    index_ayat = word_values.index("ayat") 
                    if text_pos[index_ayat+1] == "NUM":
                        target_ayat += "ayat" + " " + word_values[index_ayat+1] 
                legal_head = root
                legal_index = word_deprel.index('nmod') if 'nmod' in word_deprel else 0
                if target_ayat != "":
                    question_type = 12
                else:
                    question_type = 11
        elif root == "perubahan" and first == "bagaimana" and verb == "":
            if 'pasal' in word_values:
                index_pasal = word_values.index("pasal")
                if text_pos[index_pasal+1] == "NUM":
                    target_pasal += "pasal" + " " + word_values[index_pasal+1]
            if target_pasal != "":
                if 'ayat' in word_values:
                    index_ayat = word_values.index("ayat")
                    if text_pos[index_ayat+1] == "NUM":
                        target_ayat += "ayat" + " " + word_values[index_ayat+1]
                legal_head = root
                question_type = 13
                legal_index = word_deprel.index('nmod') if 'nmod' in word_deprel else 0
        else:
            return ''
        
    legal_target = get_legal_target(legal_index, legal_head, word_head, text_pos, word_values) if legal_index != 0 else ''
    if legal_target != '':
        if target_pasal != '' and target_ayat != '':
            return set_query(question_type, legal_title=legal_target, pasal_num=target_pasal, ayat_num=target_ayat)
        elif target_pasal != '':
            return set_query(question_type, legal_title=legal_target, pasal_num=target_pasal)
        return set_query(question_type, legal_title=legal_target)
    else:
        return ''

# df = pd.read_csv("sample-question.csv")
# for j in df['Q']:
#     print(mapping(j))
# get_result(mapping("Bagaimana perubahan bunyi Pasal 43 ayat 3 dalam Peraturan Komisi Pemberantasan Korupsi Republik Indonesia Tahun 2006 Nomor 06?"))
# print(mapping("Bagaimana perubahan bunyi Pasal 43 ayat 3 dalam Peraturan Komisi Pemberantasan Korupsi Republik Indonesia Tahun 2006 Nomor 06?"))
# print(mapping("Siapa yang menetapkan Peraturan Daerah Kabupaten Batang Nomor 7 Tahun 2010?"))
# print(mapping("Kapan Peraturan Menteri Kesehatan Republik Indonesia Nomor 49 Tahun 2019 ditetapkan?"))