import os
import random

image_store = "/media/testing32/New Volume/Plant Images/"
print("getting directories")
plant_dirs = [os.path.join(image_store, name) for name in os.listdir(image_store) if os.path.isdir(os.path.join(image_store, name))]

def get_plants_and_labels():
    # Creates a list of 

    file_loc_label_pair_list = []

    print("getting files")
    label = 0
    for plant_dir in plant_dirs:
        plant_files = [os.path.join(plant_dir, name) for name in os.listdir(plant_dir) if os.path.isfile(os.path.join(plant_dir, name)) ]
        
        for plant_file in plant_files:
            file_loc_label_pair_list.append([plant_file, label])
            
        label += 1

    return file_loc_label_pair_list

def create_test_train_files():
    pair_list = get_plants_and_labels()
    random.shuffle(pair_list)
    test_size = len(pair_list) / 5
    
    test_list = pair_list[:test_size]
    train_list = pair_list[test_size:]
    
    f = open('train.txt','w')
    for train_pair in train_list:
        f.write(train_pair[0] + " " + str(train_pair[1]) + "\n")
    f.close() # you can omit in most cases as the destructor will call it
    
    f = open('test.txt','w')
    for test_pair in test_list:
        f.write(test_pair[0] + " " + str(test_pair[1]) + "\n")
    f.close() # you can omit in most cases as the destructor will call it

if __name__ == '__main__':
    create_test_train_files()
    