try:
    import Image
except ImportError:
    from PIL import Image
import imghdr
import os
import re
from os import listdir, rename
from os.path import join
import math

from flask import Flask, render_template, send_from_directory, request
from database import *

app = Flask(__name__)

# VISITING THE HOMEPAGE RUNS ALL OF THE IMAGE-->OCR CODE ON FILES IN THE LOADING ZONE
@app.route('/')
def display_homepage():
    search_term = request.args.get('search')
    filenames = []
    result_filenames = []
    description = ''
    result_instances = search_term_in_metadata_and_text(search_term)
    for instance in result_instances:
        metamatches = []
        for key in instance.search_meta_matches:
            metamatches.append(key)
        if not metamatches:
            metamatches.append('No metadata matches found.')
        text_match_indices_list = instance.search_text_matches
        print(text_match_indices_list)
        if text_match_indices_list:
            index = len(text_match_indices_list) // 2
            print(index)
            description = get_text_preview(text_match_indices_list[index], instance.text_path)
        elif not text_match_indices_list:
            description = 'No text matches found.'
        print(instance.image_file)
        print('term: {}'.format(search_term))
        print('result description: {}'.format(description))
        result_filenames.append([instance.image_file, description, metamatches])
    for instance in read_documents():
        filenames.append(instance.image_file)
    return render_template('home.html', filenames=filenames, results=result_filenames)


@app.route('/scl/<file_name>')
def display_images(file_name):
    for instance in read_documents():
        if instance.image_file == file_name:
            image_file = instance.image_file
            text_file = instance.text_path
            text_content = instance.text
            metadata = instance.metadata
    return render_template('image.html',
                           image_file=image_file,
                           text_file=text_file,
                           text_content=text_content,
                           metadata=metadata)

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)

if __name__ == "__main__":

    run_images()
    app.run(debug=True)


# All code before Cal messes with it.
# This is also the location of Chloes OCR auto-rotate additions.
'''
    try:
    import Image
except ImportError:
    from PIL import Image
import imghdr
import os
import re
from os import listdir, rename
from os.path import join

import pytesseract
from flask import Flask, render_template, send_from_directory, request
from database import *

app = Flask(__name__)

# FOLDER PATHS
Loading_zone = "loading_zone"
Text_path = "completed_text_files"
Dest_path = "completed_files"


# This function returns True if anything besides a file is found in a path
def folder_check(path):
    folders = [f for f in listdir(path) if os.path.isdir(join(path, f))]
    if len(folders) <= 1:
        return False
    else:
        return True

# IMAGE --> OCR STRING
def ocr_extract(file):
    ocr_text = pytesseract.image_to_string(Image.open(file))
    return ocr_text

# CREATES NEW .TXT FILE WITH STRING, FILENAME, AND PATH
def text_file_creator(string, filename, path):
    new_file = open(join(path, filename), "w")
    new_file.write(string)

# ADDS A SET OF METADATA CATEGORIES FOR A FILENAME
def write_metadata_file(file_name):
    file = open('metadata.txt', 'a')
    file.write('\n\nFile Name: [{}]'
               '\nBox Number: []'
               '\nDate Added (mm/dd/yyyy): []'
               '\nName of Uploader (Last, First): []'
               '\nComments/Notes about File: []'
               .format(str(file_name)))
    file.close()

# RETURNS FILE COUNT LOCATED IN FILECOUNT.TXT
def check_file_number():
    string = open('filecount.txt', 'r')
    number = string.read()
    return number

# ADDS ONE TO FILE COUNT IN FILECOUNT.TXT
def count_plus_one():
    current_num = check_file_number()
    current_num = int(current_num)
    next_num = current_num + 1
    update = open('filecount.txt', 'w')
    update.write(str(next_num))

# RETURNS TRUE IF FILE NAME ALREADY EXISTS IN METADATA, FALSE IF NOT.
def metacheck(filename):
    metadata = open('metadata.txt', 'r')
    metastring = metadata.read()
    find_filename = metastring.find(filename)
    return find_filename is not -1

# FINDS METADATA FOR FILE NUMBER, RETURNS NESTED LIST OF CATEGORY INPUTS
def pull_metadata(filename):
    lines = []
    if metacheck(filename) is True:
        metadata = open('metadata.txt', 'r')
        metastring = metadata.read()
        print('metastring: {}'.format(metastring))
        find_filename = metastring.find(filename)
        current_location = find_filename - 12
        string = ''
        record = False
        category_count = 0
        for char in metastring[current_location:]:
            if category_count < 5:
                if char is ']':
                    record = False
                    lines.append(string)
                    string = ''
                    category_count += 1
                if record is True:
                    string = string + char
                if char is '[':
                    record = True
    return lines

def get_all_metadata():
    lines = []
    all_lines = []
    file = open('filecount.txt', 'r')
    count = int(file.read())
    counter = 0
    for x in range(count):
        filename = 'document' + str(counter) + 'image'
        counter += 1
        if metacheck(filename) is True:
            metadata = open('metadata.txt', 'r')
            metastring = metadata.read()
            find_filename = metastring.find(filename)
            current_location = find_filename - 12
            string = ''
            record = False
            category_count = 0
            for char in metastring[current_location:]:
                if category_count < 5:
                    if char is ']':
                        record = False
                        lines.append(string)
                        string = ''
                        category_count += 1
                        if category_count == 5:
                            all_lines.append(lines)
                            lines = []
                            category_count = 0
                    if record is True:
                        string = string + char
                    if char is '[':
                        record = True
    return all_lines


def search_word(term):
    all_lines = get_all_metadata()
    matching = [x for x in all_lines if term in x]
    filenames = [x[0] for x in matching]
    return filenames


# ZIPS METADATA CATEGORIES AND RESPECTIVE METADATA INTO NESTED LISTS
def zip_names(filename):
    print('filename: {}'.format(filename))
    categories = ['File Name:',
                  'Box Number:',
                  'Date Added (mm/dd/yyyy):',
                  'Name of Uploader (Last, First):',
                  'Notes/Comments:']
    entries = pull_metadata(filename)
    info_list = zip(categories, entries)
    result = []
    for each in info_list:
        result.append(each)
    return result


# RETURNS LIST OF FILE NAMES IN COMPLETED FILES FOLDER
def get_img_filenames():
    file_names = []
    dirs = listdir(Dest_path)
    for file in dirs:
        if file.startswith('document'):
            file_names.append(file)
    return file_names


# RETURNS LIST OF FILE NAMES IN COMPLETED TEXT FILES FOLDER
def get_txt_filenames():
    text_file_names = []
    dirs = listdir(Text_path)
    for file in dirs:
        if file.startswith('document'):
            text_file_names.append(file)
    return text_file_names


def read_metadata(folder):
    metadata = []
    path = os.path.join(Loading_zone, folder)
    for file in os.listdir(path):
        if file.endswith('.txt'):
            print('{} is a text file!'.format(file))
            text_path = os.path.join(path, file)
            metadata = open(text_path, 'r').read().splitlines()
            # find the opening bracket in the metadata[0] and isolate that place as where you will throw in
            # the filename
    return metadata


def metadata_insert_filename(metadata, filename):
    metadata[0] = 'File Name:' + '[' + filename + ']'
    return metadata

def append_metadata(metadata):
    # at this point, there is one copy of the metadata in Yusef's text file, and that just needs to be appended
    with open('metadata.txt', 'a') as file:
        file.writelines("%s\n" % item for item in metadata)
        file.write("\n")


# this function runs the images given a specific folder
def run_images():
    for folder in listdir(Loading_zone):
        if os.path.isdir(os.path.join(Loading_zone, folder)):
            metadata = read_metadata(folder)
            path = os.path.join(Loading_zone, folder)
            for file in listdir(path):
                filename_path = os.path.join(path, file)
                image_type = imghdr.what(filename_path)
                file_ext = file.split(".")
                if image_type:
                    print('{} is a {} file'.format(file, image_type))
                    # filename = os.path.join(folder, file)
                    count = check_file_number()
                    text_name = 'document' + str(count) + 'text'
                    image_name = 'document' + str(count) + 'image.' + file_ext[1]
                    metatext = metadata_insert_filename(metadata, image_name)
                    append_metadata(metatext)
                    image_file_dest = os.path.join(Dest_path, image_name)
                    text = ocr_extract(filename_path)
                    text_file_creator(text, text_name, Text_path)
                    rename(filename_path, image_file_dest)
                    count_plus_one()
                else:
                    print("{} is not an image file".format(file))


def search_text(term):
    filelist = []
    filenums = []
    for filename in listdir(Text_path):
        filepath = join(Text_path, filename)
        text = open(filepath, 'r')
        ocr_text = text.read()
        if term is not None:
            if term in ocr_text:
                filelist.append(filename)
    for filename in filelist:
        file_number = re.search('document(.*)text', filename)
        file_number = file_number.group(1)
        filenums.append(file_number)
    return filenums


def get_image_names_from_num(filenumbers):
    matches = []
    for filename in listdir(Dest_path):
        for each in filenumbers:
            if each in filename:
                matches.append(filename)
    return matches


# VISITING THE HOMEPAGE RUNS ALL OF THE IMAGE-->OCR CODE ON FILES IN THE LOADING ZONE
@app.route('/')
def display_homepage():
    search = request.args.get('search')
    meta_results = search_word(search)
    ocr_result_nums = search_text(search)
    ocr_results = get_image_names_from_num(ocr_result_nums)
    meta_set = set(meta_results)
    print("Combining search matches from metadata and OCR text files:")
    print("meta_set: {}".format(meta_set))
    ocr_set = set(ocr_results)
    print("ocr_set: {}".format(ocr_set))
    subtract_duplicates = ocr_set - meta_set
    results_no_duplicates = meta_results + list(subtract_duplicates)
    print("This is the final result with no duplicates: {}".format(results_no_duplicates))
    return render_template('home.html', text_file_names=get_img_filenames(),
                           results=results_no_duplicates)


@app.route('/scl/<file_name>')
def display_images(file_name):
    file_number = re.search('document(.*)image', file_name)
    file_number = file_number.group(1)
    file_ext = file_name.split(".")
    image_file_name = 'document' + str(file_number) + 'image.' + file_ext[1]
    text_file_name = 'document' + str(file_number) + 'text'
    text_location = "completed_text_files/" + text_file_name
    with open(text_location, "r") as f:
        txt_content = f.read()
    metadata = zip_names(image_file_name)
    print('this is the metadata list: {}'.format(metadata))
    return render_template('image.html',
                           image_file_name=image_file_name,
                           text_file_name=text_file_name,
                           txt_content=txt_content,
                           metadata=metadata)

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)


if __name__ == "__main__":
    run_images()
    app.run(debug=True)
'''
