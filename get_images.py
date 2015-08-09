from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import ImageChops

import csv
import os
import cv2
import urllib
import shutil
import time
import math, operator
from PIL import Image

# CONSTANTS
next_page_selector = ""
search_box_id = "lst-ib"
containing_image_div_id = "rg_s"
image_class = "rg_i"
search_button_name = "btnG"
show_more_id = "smb"

additional_terms = ("plant", "leaf", "flower")

images_per_plant = 100
image_store = "/media/testing32/New Volume/Plant Images/"

def rmsdiff(im1, im2):
    "Calculate the root-mean-square difference between two images"

    try:
        diff = ImageChops.difference(im1, im2)
        return diff.getbbox()
    except:
        return 1
    
def image_dup_finder():
    print("getting directories")
    plant_dirs = [os.path.join(image_store, name) for name in os.listdir(image_store) if os.path.isdir(os.path.join(image_store, name))]
    
    plant_files = []
    
    print("getting files")
    for plant_dir in plant_dirs:
        plant_files = plant_files + [os.path.join(plant_dir, name) for name in os.listdir(plant_dir) if os.path.isfile(os.path.join(plant_dir, name)) ]

    plant_hash = {}
    
    print("finding plant matches")
    for plant_file in plant_files:
        size = os.stat(plant_file).st_size
        
        if plant_hash.has_key(size):
            plant_hash[size].append(plant_file)
        else:
            plant_hash[size] = [plant_file,]
    
    print("looping through keys - " + str(len(plant_hash.keys())))
    
    with open('dups.csv', 'w') as writer:
        csv_writer = csv.writer(writer, delimiter=',', quotechar='"')
    
        for key in plant_hash.keys():
            size_list = plant_hash[key]
            if len(size_list) == 1:
                continue
            
            for i in range(0, len(size_list)):
                img_1 = Image.open(size_list[i])
                for j in range(i+1, len(size_list)):
                    # you don't need to do a full n^2 to compare all of the images
                    img_2 = Image.open(size_list[j]) 
                    
                    if rmsdiff(img_1.resize((128, 128), Image.ANTIALIAS), img_2.resize((128, 128), Image.ANTIALIAS)) is None:
                        csv_writer.writerow([size_list[i], size_list[j]])
                        continue

def image_dup_cleaner():
    # We got a bunch of duplicate images
    # We are going to drop the ones that have the greatest search
    # number because those are probably the wrong ones
    
    def get_number(filename):
        split_list = filename.split(" ")
        return int(split_list[len(split_list) - 1])
    
    with open('dups.csv', 'r') as reader:
        csv_reader = csv.reader(reader, delimiter=',', quotechar='"')
            
        last_left_column = None
        current_low_number = None
        current_low_file = None
        for row in csv_reader:
            # if we have already removed the other file
            # skip this comparison
            if not os.path.isfile(row[1]):
                continue
            
            if row[0] != last_left_column:
                # this is the first time with this
                # file in the left column, if it doesn't exist skip
                if not os.path.isfile(row[0]):
                    continue
                last_left_column = row[0]
                current_low_number = get_number(row[0])
                current_low_file = row[0]
            
            new_number = get_number(row[1])
            
            if new_number < current_low_number:
                os.remove(current_low_file)
                current_low_number = new_number
                current_low_file = row[1]
                
    
def get_plants(file):
    plants = []
    with open(file, 'r') as reader:
        plant_reader = csv.reader(reader, delimiter=',')
        for row in plant_reader:
            plants.append(row[0])
            
    return plants

def scrape_plants(plants):
    
    driver = webdriver.Firefox()# Chrome()#s PhantomJS()
    skip = True
    start_plant = "Meadow holly"
    
    for plant in plants:
        
        if plant == start_plant:
            skip = False
            
        if skip:
            continue
        
        directory = image_store + plant.lower() + "/"
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        for term in additional_terms:

            driver.get("https://images.google.com/")
                        
            search_term = plant.lower() + " " + term
            
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, search_box_id)))
            search_box.clear()
            search_box.send_keys(search_term)
            
            search_button = driver.find_element_by_name(search_button_name)
            search_button.click()
            
            image_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, containing_image_div_id)))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            
            image_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, containing_image_div_id)))
            images = image_div.find_elements_by_class_name(image_class)
            
            current_count = 1
            
            for plant_img in images:
                
                if current_count > images_per_plant:
                    break
                
                src = plant_img.get_attribute('src')
                
                if src is None:
                    continue
                
                image_location = urllib.urlretrieve(src)[0]
                
                shutil.move(image_location, directory + search_term + " " + str(current_count))
                current_count += 1
                        
    driver.close()
            
if __name__ == '__main__':
    # Gets the plants from google images, finds duplicate images
    # and deletes the images that are mostly likely to be wrong
    
    # went from 186900 images to 136652 images
    
    #plants = get_plants('plants.csv')
    #scrape_plants(plants)
    #image_dup_finder()
    #image_dup_cleaner()