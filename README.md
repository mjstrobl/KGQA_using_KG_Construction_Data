# KGQA using KG Construction Data

## Introduction

Our KGQA system aims to produce a model, which can be trained on questions as well as RE datasets in order to extract a relation for a given relation. This can be useful to translate natural language questions into SPARQL queries, especially for questions with a single entity/relation, i.e. involving a single fact from the KG.

## Execution

1. Download all datasets (see below) and store them in the data/ directory.
2. Install requirements.
3. Run data processors (order irrelevant):
    ```
   python3 freda_lcquad2_processor.py
   python3 freda_simple_processor.py
   python3 lcquad2_processor.py
   python3 simple_questions_processor.py
    ```
4. Find created datasets in data/:
   1. freda_lcquad2.json (FREDA dataset prepared for LC-QuaD 2.0)
   2. freda_simple.json (FREDA dataset prepared for SimpleQuestions)
   3. lcquad2_test_all.json (LC-QuaD 2.0 test dataset with all examples and all relevant relations)
   4. lcquad2_train_{10|25|50|100|all}.json (LC-QuaD 2.0 train dataset with a certain number of examples per relation)
   5. simple_test_all.json (SimpleQuestions test dataset with all relevant relations)
   6. simple_train_{10|25|50|100|all}.json (SimpleQuestions train dataset with a certain number of examples per relation)
   7. simple_valid_all.json (SimpleQuestions dev dataset with all relevant relations)
5. Model training:
   ```
   python3 training.py --train_file <data for training> --validation_file <data for testing> --results_file <results file> --model_name_or_path bert-large-cased --output_dir <model output directory> --num_train_epochs 5 --per_device_train_batch_size 32 --do_train --do_eval --no_relation <4 (simple) or 13 (complex)> --overwrite_output_dir
   ```
   The data file for training can either be used as is (see datasets in data/) or be compiled through combining some of them, e.g. freda_simple.json and simple_train_all.json, depending on the experiment conducted.
   One of the test files should be used for testing, e.g. simple_test_all.json or lcquad2_test_all.json

## Datasets

Download all datasets and move them to data/

### FREDA

1. Download database from https://drive.google.com/file/d/1iNQLjFWlYfMvhh5QdPi33H_qnR8njt_p/view?usp=sharing
2. Extract (freda_final.db should be in data/)

### LC-QuaD 2.0

1. Download data from https://github.com/AskNowQA/LC-QuAD2.0/tree/master/dataset
2. Move test.json and train.json to data/

### SimpleQuestions

1. Download data from https://github.com/davidgolub/SimpleQA/tree/master/datasets/SimpleQuestions
2. Move annotated_fb_data_{train|dev/|test}.txt to data/


### Freebase to names

1. Download Freebase Mid to names mapping: https://drive.google.com/file/d/1NM8Ti9qM_DB_m6OMREXfYubTisFsauCU/view?usp=sharing
2. Move to data/

### Wikidata to Wikipedia mapping

1. Download mapping: https://drive.google.com/file/d/1uM-i3MgRPDTfM2gtra7kRRmWXEs9zvh-/view?usp=sharing
2. Move to data/

### Wikipedia alias dictionary

1. Download alias dictionary: https://drive.google.com/file/d/1ahM7vJ_hlvqiEQO3K8FNj_HRU-kHWUGJ/view?usp=sharing
2. Move to data/
