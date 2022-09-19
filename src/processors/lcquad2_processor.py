import json
import random
import re

RE_ENTITY = re.compile(r'\{(.*?)\}', re.DOTALL | re.UNICODE)


RELATIONS = {
    "P551": ("place_of_residence",0),
    "P19": ("place_of_birth",1),
    "P27": ("nationality",2),
    #"": "employee_or_member_of",
    "P69": ("educated_at",3),
    #"": "political_affiliation",
    "P25": ("child_of",4),
    "P22": ("child_of",4),
    "P40": ("child_of",4, "inverse"),  # actually the inverse
    "P26": ("spouse", 5, "bidirectional"),
    "P159": ("headquarters",6),
    "P749": ("subsidiary_of", 7),
    "P355": ("subsidiary_of", 7, "inverse"),  # inverse
    "P112": ("founded", 8, "inverse"),   # it is actually the inverse
    "P169": ("ceo_of", 9),
    "P166": ("award", 10),
    #"": "alma_mater",
    "P20": ("place_of_death", 11),
    "P3373": ("sibling", 12, "bidirectional")
}
NO_RELATION = 13


mapping = json.load(open('data/wikidata_wikipedia_mapping.json'))
aliases = json.load(open("data/aliases_reverse.json"))

def find_positions(wikidata_entity, nnqt_entities, text):
    entity_found_in_nnqt = ""
    alternative_names = {}
    wikipedia_entity = ""
    if wikidata_entity in mapping:
        wikipedia_entity = mapping[wikidata_entity]
        for entity in nnqt_entities:
            if entity == wikipedia_entity:
                entity_found_in_nnqt = entity
        if wikipedia_entity in aliases:
            alternative_names = aliases[wikipedia_entity]
            if len(entity_found_in_nnqt) == 0:
                for entity in nnqt_entities:
                    if entity in alternative_names:
                        entity_found_in_nnqt = entity

    positions = []
    if len(entity_found_in_nnqt) > 0 and entity_found_in_nnqt in text:
        positions.extend([(m.start(),len(entity_found_in_nnqt)) for m in re.finditer(re.escape(entity_found_in_nnqt), text)])
    elif len(wikipedia_entity) > 0 and wikipedia_entity in text:
        positions.extend([(m.start(), len(wikipedia_entity)) for m in re.finditer(re.escape(wikipedia_entity), text)])
    elif len(alternative_names) > 0:
        names = set()
        for alt_name in alternative_names:
            names.add(alt_name)

        names = list(names)

        names.sort(key=lambda s: len(s), reverse=True)

        alt_text = text
        for alias in alternative_names:
            if len(alias) > 2:
                found = [(m.start(),len(alias)) for m in re.finditer(re.escape(alias), alt_text)]
                positions.extend(found)
                for f in found:
                    start = f[0]
                    length = f[1]
                    alt_text = alt_text[:start] + "#" * length + alt_text[start + length:]

    return positions

def process_sample(labels, subjects, objects, entity_positions, all_samples, text, label, sparql_wikidata, bidirectional):
    entities_dealt_with = set()

    for subject in subjects:
        if subject in entity_positions and subject not in entities_dealt_with:
            for subject_position in entity_positions[subject]:
                s_s = subject_position[0]
                s_l = subject_position[1]

                new_text = text[:s_s] + "<e1>" + text[s_s:s_s + s_l] + "</e1>" + text[s_s + s_l:]

                if label not in labels:
                    labels[label] = 0
                labels[label] += 1

                all_samples.append((new_text, label))

                if not bidirectional:
                    new_text = text[:s_s] + "<e2>" + text[s_s:s_s + s_l] + "</e2>" + text[s_s + s_l:]

                    if NO_RELATION not in labels:
                        labels[NO_RELATION] = 0
                    labels[NO_RELATION] += 1

                    all_samples.append((new_text, NO_RELATION))
                else:
                    new_text = text[:s_s] + "<e2>" + text[s_s:s_s + s_l] + "</e2>" + text[s_s + s_l:]

                    if label not in labels:
                        labels[label] = 0
                    labels[label] += 1

                    all_samples.append((new_text, label))


    for object in objects:
        if object in entity_positions and object not in entities_dealt_with:
            for object_position in entity_positions[object]:
                o_s = object_position[0]
                o_l = object_position[1]

                new_text = text[:o_s] + "<e2>" + text[o_s:o_s + o_l] + "</e2>" + text[o_s + o_l:]

                if label not in labels:
                    labels[label] = 0
                labels[label] += 1

                all_samples.append((new_text, label))

                if not bidirectional:
                    new_text = text[:o_s] + "<e1>" + text[o_s:o_s + o_l] + "</e1>" + text[o_s + o_l:]

                    if NO_RELATION not in labels:
                        labels[NO_RELATION] = 0
                    labels[NO_RELATION] += 1

                    all_samples.append((new_text, NO_RELATION))
                else:
                    new_text = text[:o_s] + "<e1>" + text[o_s:o_s + o_l] + "</e1>" + text[o_s + o_l:]

                    if label not in labels:
                        labels[label] = 0
                    labels[label] += 1

                    all_samples.append((new_text, label))



def process(labels, rs, parts, wikidata_entities, nnqt_entities, question, all_samples, sparql_wikidata):
    triples = {}
    related_pairs = set()
    subjects = set()
    objects = set()
    entity_positions_question = {}
    entity_positions_paraphrased_question = {}
    for part in parts:
        sub_parts = part.split()
        if len(sub_parts) == 3 and ":P" in sub_parts[1] and "wd:Q" in part:
            subject = sub_parts[0][3:]
            relation = sub_parts[1]
            relation = relation[relation.find(":")+1:]

            if relation not in RELATIONS:
                continue

            if relation not in rs:
                rs[relation] = 0
            rs[relation] += 1
            object = sub_parts[2][3:]

            d = {"subjects":set(), 'objects':set()}
            if relation in triples:
                d = triples[relation]

            if "Q" in subject:
                d["subjects"].add(subject)
                subjects.add(subject)

            if "Q" in object:
                d["objects"].add(object)
                objects.add(object)

            if "Q" in subject and "Q" in object:
                related_pairs.add(subject + "-" + object)

            triples[relation] = d

    for wikidata_entity in wikidata_entities:
        # find positions of entity in question
        positions = find_positions(wikidata_entity, nnqt_entities, question)
        if len(positions) > 0:
            entity_positions_question[wikidata_entity] = positions

    for relation in triples:
        subjects = triples[relation]['subjects']
        objects = triples[relation]['objects']

        bidirectional = False
        label = NO_RELATION
        if relation in RELATIONS:
            label = RELATIONS[relation][1]
            if RELATIONS[relation][-1] == "inverse":
                new_subjects = objects
                objects = subjects
                subjects = new_subjects

            if RELATIONS[relation][-1] == "bidirectional":
                bidirectional = True

        process_sample(labels, subjects, objects, entity_positions_question, all_samples, question, label, sparql_wikidata, bidirectional)

rs = {}
labels = {}
all_samples = []
starts = {}

for filename in ["train", "test"]:
    dataset = json.load(open("data/" + filename + ".json"))
    for sample in dataset:
        if type(sample['NNQT_question']) is str and type(sample['question']) is str and type(sample['paraphrased_question']) is str:
            nnqt_question = sample['NNQT_question']
            question = sample["question"].replace("_"," ")
            paraphrased_question = sample["paraphrased_question"].replace("_"," ")
            sparql_wikidata = sample["sparql_wikidata"]

            start = sparql_wikidata.split()[0].lower()
            if start not in starts:
                starts[start] = 0

            starts[start] += 1

            if question is None:
                continue

            nnqt_entities = set()
            idx = 0
            while True:
                match = re.search(RE_ENTITY, nnqt_question[idx:])
                if match:
                    entity = match.group(1)
                    nnqt_entities.add(entity)
                    idx += match.end()
                else:
                    break

            body_idx = sparql_wikidata.lower().find("where {")
            if body_idx > -1:
                end_idx = sparql_wikidata[body_idx:].find("}")
                if end_idx > -1:
                    body = sparql_wikidata[body_idx + 7:body_idx + end_idx].strip()
                    wikidata_entities = set([m.group(1) for m in re.finditer(r"wd:(Q[0-9]*)", body)])
                    parts = body.split(".")

                    okay = True

                    if okay:
                        process(labels, rs, parts, wikidata_entities, nnqt_entities, question, all_samples, sparql_wikidata)
                        process(labels, rs, parts, wikidata_entities, nnqt_entities, paraphrased_question, all_samples, sparql_wikidata)

    with open('data/lcquad2_' + filename + '_all.json', 'w') as f:
        for o in all_samples:
            d = {"sentence1": o[0], "sentence2":"", "label":o[1]}
            f.write(json.dumps(d) + "\n")

    if filename == 'train':
        random.seed(10)
        random.shuffle(all_samples)
    
        num_labels = [10, 25, 50, 100]
        for num in num_labels:
            current = {}
            with open('data/lcquad2_train_' + str(num) + '.json', 'w') as f:
                for o in all_samples:
                    label = o[1]
                    if label not in current:
                        current[label] = 0
    
                    if current[label] < num:
                        current[label] += 1
                    else:
                        continue
    
                    d = {"sentence1": o[0], "sentence2": "", "label": o[1]}
                    f.write(json.dumps(d) + "\n")


