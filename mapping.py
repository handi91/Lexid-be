import stanza
import pandas as pd
import re
import string

def generate_mapping():
    stanza.download('id')
    nlp = stanza.Pipeline('id')
    templates = pd.read_csv('question-sparql-template.csv')
    semantic_templates = pd.read_csv('question-sparql-template-semantic.csv')
    question_parse = pd.read_csv('question-parse-pattern.csv')
    # semantic_questions = pd.read_csv('semantic-question-collection.csv').set_index('Question').fillna('')

    def set_query(query_index, is_semantic=False, **kwargs):
        if not is_semantic:
            query_template = templates[templates['query_index'] == query_index]\
                                      .reset_index(drop=True)['query_template'][0]
            for key, value in kwargs.items():
                query_template = re.sub(key, value.title() if key != "ayat_num" else value,
                                        query_template)
            if query_index == 13:
                ayat = kwargs.get('ayat_num')
                if not ayat:
                    query_template = re.sub("ayat_num", "", query_template)
        else:
            query_template = semantic_templates[semantic_templates['query_index'] == query_index]\
                                                .reset_index(drop=True)['query_template'][0]
            for key, value in kwargs.items():
                query_template = re.sub(key, value.title(), query_template)
        return query_template

    def get_legal_target(target_idx, head_values, word_head, text_pos, word_values):
        target = ""
        try:
            if word_head[target_idx] == head_values:
                target_stop = target_idx
                # get the first number
                try:
                    first_num_index = text_pos.index("NUM", target_stop)
                    target_stop = first_num_index - 1
                except:
                    first_num_index = None
                # get second number
                try:
                    second_num_index = text_pos.index("NUM", first_num_index + 1)
                except:
                    second_num_index = None
                # get legal title
                for j in range(len(word_values[target_idx:target_stop])):
                    if word_values[target_idx+j][0] in ['/', ',']:
                        target += word_values[target_idx+j][0]
                        target += " " + word_values[target_idx+j][1:] if word_values[target_idx+j][1:] else ""
                    else:
                        target += word_values[target_idx+j]
                    if word_values[target_idx+j+1][0] not in ['/', ',']:
                        target += " "
                # handle legal number and year
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
    
    def convert_passive_to_active_verb(verb):
        active_verb = ""
        if verb[2] in ['k', 't', 's', 'p'] and verb[3] not in ['k', 't', 's', 'p']:
            if verb[2] == "k":
                active_verb += "meng" + verb[3:]
            elif verb[2] == "t":
                active_verb += "men" + verb[3:]
            elif verb[2] == "s":
                active_verb += "meny" + verb[3:]
            else:
                active_verb += "mem" + verb[3:]
        else:
            if verb[2] in ['l', 'm', 'n', 'r', 'w', 'y']:
                active_verb += 'me' + verb[2:]
            elif verb[2] in ['c', 'd', 'j', 's', 't', 'z']:
                active_verb += 'men' + verb[2:]
            elif verb[2] in ['b', 'f', 'p', 'v']:
                active_verb += 'mem' + verb[2:]
            else:
                active_verb += "meng" + verb[2:]
        return active_verb
    
    def get_subject_label(target_idx, head_values, word_head, word_values):
        subject_label = ""
        if word_head[target_idx] == head_values:
            target_stop = len(word_values) if word_values[-1] not in string.punctuation else len(word_values) - 1
            for j in range(len(word_values[target_idx:target_stop])):
                if word_values[target_idx+j][0] in ['/', ',']:
                    subject_label += word_values[target_idx+j][0]
                    subject_label += " " + word_values[target_idx+j][1:] if word_values[target_idx+j][1:] else ""
                else:
                    subject_label += word_values[target_idx+j]
                try:
                    if word_values[target_idx+j+1][0] not in ['/', ',']:
                        subject_label += " "
                except:
                    pass

        return subject_label.strip()
        
    def mapping(text):
        # result_prefix = ""
        # try:
        #     legal_ref = semantic_questions['legal_ref'][text]
        #     pasal_ref = semantic_questions['pasal_ref'][text]
        #     ayat_ref = semantic_questions['ayat_ref'][text]
        #     result_prefix = f"Berdasarkan {pasal_ref} {ayat_ref} {legal_ref}:\n" if ayat_ref \
        #                     else f"Berdasarkan {pasal_ref} {legal_ref}:\n"
        #     if ayat_ref != '':
        #         return set_query(12, legal_title=legal_ref,
        #                          pasal_num=pasal_ref, ayat_num=ayat_ref), 12, result_prefix
        #     return set_query(11, legal_title=legal_ref,
        #                      pasal_num=pasal_ref, ayat_num=ayat_ref), 11, result_prefix
        # except:
        #     pass
        
        doc = nlp(text)
        if len(doc.sentences) != 1:
            return "", "", -1

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

        # non-semantic question param
        question_type = 0
        legal_head = ""
        legal_index = 0
        target_pasal = ""
        target_ayat = ""
        question_info = get_question_type_and_legal_head(root, first, verb)

        # semantic question param
        subject_label = ""
        act_label = ""
        alt_act = ""
        if question_info:
            question_type = question_info['q_type']
            legal_head = question_info['legal_head']
            legal_index = word_deprel.index(
                              question_info['legal_rel']
                          ) if question_info['legal_rel'] in word_deprel else 0
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
                if root == "apa" and first == "apa" and verb != "":
                    if verb[:2] == "di":
                        act_label = convert_passive_to_active_verb(verb)
                        alt_act = verb
                        subject_rel = 'obl'
                    else:
                        act_label = verb
                        subject_rel = 'obj'
                    subject_index = word_deprel.index(subject_rel) if subject_rel in word_deprel else 0
                    subject_label =  get_subject_label(
                        subject_index, verb,
                        word_head, word_values
                    ) if subject_index != 0 else ''
                elif root == "apa" and first == "apa" and verb == "":
                    first_noun = word_values[text_pos.index("NOUN")] if 'NOUN' in  text_pos else ""
                    if first_noun:
                        act_label = first_noun
                        print(word_deprel)
                        subject_rel = ['flat', 'nmod', 'det', 'compound']
                        for rel in subject_rel:
                            if rel not in word_deprel:
                                continue
                            subject_index = word_deprel.index(rel, word_values.index(first_noun)+1)  
                            subject_label =  get_subject_label(
                                subject_index, first_noun,
                                word_head, word_values
                            ) if subject_index != 0 else ''
                            if subject_label != '':
                                break      
                else:
                    return '', "", -1
            
        legal_target = get_legal_target(legal_index, legal_head,
                                        word_head, text_pos, word_values) if legal_index != 0 else ''
        if legal_target != '':
            if target_pasal != '' and target_ayat != '':
                return set_query(question_type, False, legal_title=legal_target,
                                 pasal_num=target_pasal, ayat_num=target_ayat), '', question_type
            elif target_pasal != '':
                return set_query(question_type, False, legal_title=legal_target,
                                 pasal_num=target_pasal), '', question_type
            return set_query(question_type, False, legal_title=legal_target), '', question_type
        else:
            if subject_label != "" and act_label != "" and alt_act != "":
                return set_query(1, True, act_label=act_label, subject_label=subject_label),\
                       set_query(1, True, act_label=alt_act, subject_label=subject_label), 1
            elif subject_label != "" and act_label != "":
                return set_query(1, True, act_label=act_label, subject_label=subject_label), '', 1
            return '', '', -1
    
    return mapping