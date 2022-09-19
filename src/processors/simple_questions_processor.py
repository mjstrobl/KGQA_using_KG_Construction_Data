import json
import re
import glob, os
import random

RELATIONS = {"www.freebase.com/people/person/place_of_birth":0,
             "www.freebase.com/people/person/nationality":1,
             "www.freebase.com/location/location/people_born_here":0,
             "www.freebase.com/people/person/children":3,
             "www.freebase.com/people/person/parents":3,
             "www.freebase.com/organization/organization/founders":2,
             "www.freebase.com/organization/organization_founder/organizations_founded":2
}

INVERSE = {"www.freebase.com/location/location/people_born_here",
           "www.freebase.com/people/person/children",
           "www.freebase.com/organization/organization/founders"}

mid2names = json.load(open("data/mid2names.json"))

results = []

for filename in ["test", "train", "valid"]:
    with open('data/annotated_fb_data_' + filename + '.txt') as f:
        for line in f:
            line = line.strip()
            parts = line.split('\t')

            if len(parts) < 4:
                continue

            subject = parts[0][16:]
            object = parts[2][16:]
            question = parts[3]

            relation = parts[1]
            if relation not in RELATIONS:
                continue

            if subject in mid2names:
                subject_names = mid2names[subject]
                found = False
                for subject_name in subject_names:
                    if subject_name.lower() in question.lower():
                        insensitive_hippo = re.compile(re.escape(subject_name), re.IGNORECASE)
                        if relation in INVERSE:
                            question = insensitive_hippo.sub("<e2>" + subject_name + "</e2>", question)
                        else:
                            question = insensitive_hippo.sub("<e1>" + subject_name + "</e1>", question)
                        found = True
                        actual_name = subject_name
                        break
                if found:
                    results.append({"sentence1":question, "sentence2":"", "label":RELATIONS[relation]})

                    if relation in INVERSE:
                        question = question.replace("<e2>", "<e1>")
                        question = question.replace("</e2>", "</e1>")
                    else:
                        question = question.replace("<e1>","<e2>")
                        question = question.replace("</e1>", "</e2>")
                    results.append({"sentence1": question, "sentence2": "", "label": 4})

    with open('data/simple_' + filename + '_all.json', 'w') as f:
        for o in results:
            f.write(json.dumps(o) + "\n")

    if filename == 'train':
        random.seed(10)
        random.shuffle(results)

        num_labels = [10, 25, 50, 100]
        for num in num_labels:
            current = {}
            with open('data/simple_train_' + str(num) + '.json', 'w') as f:
                for o in results:
                    label = o["label"]
                    if label not in current:
                        current[label] = 0

                    if current[label] < num:
                        current[label] += 1
                    else:
                        continue

                    f.write(json.dumps(o) + "\n")


