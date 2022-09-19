import json
import random
import pickle
import sqlite3


NO_RELATION = 4

RELATIONS = {"place_of_birth":0,
             "nationality":1,
             "child_of":3,
             "founded":2,
}

def create_data(database):
    conn = None
    try:
        conn = sqlite3.connect(database)
        print(sqlite3.version)
    except sqlite3.Error as e:
        print(e)

    cur = conn.cursor()

    dataset = []
    for relation in RELATIONS:
        label = RELATIONS[relation]


        sql = "SELECT r.data_2, r.response_2, r.data_3, r.response_3, s.data  FROM sentence s, " + relation + " r WHERE s.response > -2 AND s.article = r.article AND s.line = r.line " \
                "AND r.annotator_1 IS NOT NULL AND response_1 > -1 AND annotator_2 IS NOT NULL AND response_2 > -1 AND (response_1 = response_2 OR (annotator_3 IS NOT NULL AND response_3 > -1));"
        cur.execute(sql)

        rows = cur.fetchall()

        print("rows fetched: " + str(len(rows)))


        for row_idx in range(len(rows)):
            row = rows[row_idx]
            if row[2] is None:
                annotation = json.loads(row[0])
                response = row[1]
            else:
                annotation = json.loads(row[2])
                response = row[3]

            sentence = json.loads(row[4])['sentence']
            entities = annotation['entities']
            subjects = annotation['subjects']
            objects = annotation['objects']
            unidirectional = True

            if relation == 'spouse' or relation == "related_to" or relation == 'sibling' or relation == 'colleague':
                unidirectional = False

            if not unidirectional:
                new_subjects = set()
                new_subjects.update(set(subjects))
                new_subjects.update(set(objects))
                subjects = list(new_subjects)
                objects = []

            if response < 0:
                continue

            if response == 1:
                if unidirectional:
                    for s_idx in subjects:
                        for s_tuple in entities[s_idx]['positions']:
                            start = s_tuple[0]
                            length = s_tuple[1]

                            sample = sentence[:start] + "<e1>" + sentence[start:start+length] + "</e1>" + sentence[start+length:]
                            dataset.append({"sentence1":sample, "sentence2":"", "label":label})

                            sample = sentence[:start] + "<e2>" + sentence[start:start + length] + "</e2>" + sentence[start + length:]
                            dataset.append({"sentence1": sample, "sentence2": "", "label": NO_RELATION})

                    for o_idx in objects:
                        for o_tuple in entities[o_idx]['positions']:
                            start = o_tuple[0]
                            length = o_tuple[1]

                            sample = sentence[:start] + "<e2>" + sentence[start:start + length] + "</e2>" + sentence[start + length:]
                            dataset.append({"sentence1": sample, "sentence2": "", "label": label})

                            sample = sentence[:start] + "<e1>" + sentence[start:start + length] + "</e1>" + sentence[start + length:]
                            dataset.append({"sentence1": sample, "sentence2": "", "label": NO_RELATION})

                else:
                    for s_idx in subjects:
                        for s_tuple in entities[s_idx]['positions']:
                            start = s_tuple[0]
                            length = s_tuple[1]

                            sample = sentence[:start] + "<e1>" + sentence[start:start+length] + "</e1>" + sentence[start+length:]
                            dataset.append({"sentence1":sample, "sentence2":"", "label":label})

                            sample = sentence[:start] + "<e2>" + sentence[start:start+length] + "</e2>" + sentence[start+length:]
                            dataset.append({"sentence1":sample, "sentence2":"", "label":label})

                    for idx in range(len(entities)):
                        if idx not in subjects:
                            entity = entities[idx]
                            for s_tuple in entity['positions']:
                                start = s_tuple[0]
                                length = s_tuple[1]

                                sample = sentence[:start] + "<e1>" + sentence[start:start + length] + "</e1>" + sentence[start + length:]
                                dataset.append({"sentence1": sample, "sentence2": "", "label": NO_RELATION})

                                sample = sentence[:start] + "<e2>" + sentence[start:start + length] + "</e2>" + sentence[start + length:]
                                dataset.append({"sentence1": sample, "sentence2": "", "label": NO_RELATION})



    print("found: " + str(len(dataset)))
    random.shuffle(dataset)
    with open('data/freda_simple.json', 'w') as f:
        for o in dataset:
            f.write(json.dumps(o) + "\n")


def main():

    database = "data/freda_final.db"

    create_data(database)


if __name__ == "__main__":
    main()

