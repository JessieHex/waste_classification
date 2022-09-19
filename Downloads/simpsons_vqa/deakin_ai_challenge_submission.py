# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2022. Reda Bouadjenek, Deakin University                      +
#     Email:  reda.bouadjenek@deakin.edu.au                                    +
#                                                                              +
#  Licensed under the Apache License, Version 2.0 (the "License");             +
#   you may not use this file except in compliance with the License.           +
#    You may obtain a copy of the License at:                                  +
#                                                                              +
#                 http://www.apache.org/licenses/LICENSE-2.0                   +
#                                                                              +
#    Unless required by applicable law or agreed to in writing, software       +
#    distributed under the License is distributed on an "AS IS" BASIS,         +
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  +
#    See the License for the specific language governing permissions and       +
#    limitations under the License.                                            +
#                                                                              +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


import sys, os, h5py, json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras.saving import hdf5_format
import torch
from PIL import Image
from transformers import ViltProcessor, ViltForQuestionAnswering 
from transformers.tokenization_utils_base import BatchEncoding
from torch.utils.data import DataLoader

class VQADataset(torch.utils.data.Dataset):
    def __init__(self, images, questions, processor):
        self.images = images
        self.questions = questions
        self.processor = processor   

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        img = Image.open(self.images[idx]).convert("RGB")
        img = img.resize((256, 256))
        encoding = self.processor(img, self.questions[idx], padding="max_length", truncation=True, return_tensors="pt")
        item = {key: val.squeeze() for key, val in encoding.items()}
        return item

if __name__ == "__main__":
    if len(sys.argv) == 1:
        input_dir = '.'
        output_dir = '.'
    else:
        input_dir = os.path.abspath(sys.argv[1])
        output_dir = os.path.abspath(sys.argv[2])

    print("Using input_dir: " + input_dir)
    print("Using output_dir: " + output_dir)
    print(sys.version)
    print("Tensorflow version: " + tf.__version__)

    # Loading the model.
    processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa") 
    model = torch.load("model", map_location ='cpu')

    # Read test dataset
    imgs_path_test = input_dir + '/simpsons_test/'
    q_val_file = imgs_path_test + 'questions.json'
    q_test = json.load(open(q_val_file))


    def preprocessing(questions, imgs_path):
        # Make sure the questions and annotations are alligned
        questions['questions'] = sorted(questions['questions'], key=lambda x: x['question_id'])
        q_out = []
        imgs_out = []
        q_ids = []
        # Preprocess questions
        for q in questions['questions']:
            # Preprocessing the question
            q_text = q['question'].lower()
            q_text = q_text.replace('?', ' ? ')
            q_text = q_text.replace('.', ' . ')
            q_text = q_text.replace(',', ' . ')
            q_text = q_text.replace('!', ' . ').strip()
            q_out.append(q_text)
            file_name = imgs_path + str(q['image_id']) + '.png'
            imgs_out.append(file_name)
            q_ids.append(q['question_id'])
        return imgs_out, q_out, q_ids


    imgs_test, q_test, q_ids_test = preprocessing(q_test, imgs_path_test)

    # Define the test dataset
    test_dataset = VQADataset(imgs_test, q_test, processor)
    val_dataloader = DataLoader(test_dataset, batch_size=64)

    # Making predictions!
    
    y_predict = []
    with torch.no_grad():
        for local_batch in val_dataloader:
            local_batch = BatchEncoding(local_batch)
            outputs = model(**local_batch)
            pred = outputs.logits.numpy().argmax(1)
            y_predict += pred.tolist()

    y_predict = np.array(y_predict)
    y_predict[y_predict==9] = 1
    y_predict[y_predict==3] = 0
    y_predict[(y_predict !=1) & (y_predict !=0)] = 0

    # Writting predictions to file.
    answers = ['yes', 'no']
    with open(os.path.join(output_dir, 'answers.txt'), 'w') as result_file:
        for i in range(len(y_predict)):
            result_file.write(str(q_ids_test[i]) + ',' + answers[y_predict[i]] + '\n')
