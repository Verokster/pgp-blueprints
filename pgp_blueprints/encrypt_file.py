import os
import sys
import glob
import re
import argparse
import pgpy
import shipyard_utils as shipyard
try:
    import exit_codes as ec
except BaseException:
    from . import exit_codes as ec
        
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--source-file-name-match-type',
        dest='source_file_name_match_type',
        default='exact_match',
        choices={
            'exact_match',
            'regex_match'},
        required=False)
    parser.add_argument(
        '--source-folder-name',
        dest='source_folder_name',
        default='',
        required=False)
    parser.add_argument(
        '--source-file-name',
        dest='source_file_name',
        required=True)
    parser.add_argument(
        '--destination-file-name',
        dest='destination_file_name',
        default=None,
        required=False)
    parser.add_argument(
        '--destination-folder-name',
        dest='destination_folder_name',
        default='',
        required=False)
    parser.add_argument(
        '--pgp-private-key',
        dest='pgp_private_key',
        default=None,
        required=True)
    return parser.parse_args()

def clean_folder_name(folder_name):
    """
    Cleans folders name by removing duplicate '/' as well as leading and trailing '/' characters.
    """
    folder_name = folder_name.strip('/')
    if folder_name != '':
        folder_name = os.path.normpath(folder_name)
    return folder_name


def combine_folder_and_file_name(folder_name, file_name):
    """
    Combine together the provided folder_name and file_name into one path variable.
    """
    combined_name = os.path.normpath(
        f'{folder_name}{"/" if folder_name else ""}{file_name}')
    combined_name = os.path.normpath(combined_name)

    return combined_name


def find_all_local_file_names(source_folder_name):
    """
    Returns a list of all files that exist in the current working directory,
    filtered by source_folder_name if provided.
    """
    cwd = os.getcwd()
    cwd_extension = os.path.normpath(f'{cwd}/{source_folder_name}/**')
    file_names = glob.glob(cwd_extension, recursive=True)
    return [file_name for file_name in file_names if os.path.isfile(file_name)]


def find_all_file_matches(file_names, file_name_re):
    """
    Return a list of all file_names that matched the regular expression.
    """
    matching_file_names = []
    for file in file_names:
        if re.search(file_name_re, file):
            matching_file_names.append(file)

    return matching_file_names

def encrypt_file(
        source_file_name,
        destination_file_name,
        key):
        
    with open(source_file_name, "rb") as fin:
        message = pgpy.PGPMessage.new(fin.read())
        enc_message = key.pubkey.encrypt(message)
        
        with open(destination_file_name, "wb") as fout:
            fout.write(bytes(enc_message))
            
def encrypt_files(
        source_file_names,
        destination_file_name,
        key):
        
    for source_file_n in source_file_names:
        encrypt_file(source_file_n, destination_file_name, key)
        
    

def main():
    args = get_args()

    key = pgpy.PGPKey()
    key.parse(args.pgp_private_key)
    
    source_file_name = args.source_file_name
    source_folder_name = clean_folder_name(args.source_folder_name)
    source_full_path = combine_folder_and_file_name(
        folder_name=source_folder_name, file_name=source_file_name)
    source_file_name_match_type = args.source_file_name_match_type
    destination_folder_name = clean_folder_name(args.destination_folder_name)
    destination_file_name = args.destination_file_name
    destination_full_path = combine_folder_and_file_name(
        destination_folder_name, destination_file_name)

    if source_file_name_match_type == 'regex_match':
        file_paths = find_all_local_file_names(source_folder_name)
        matching_file_paths = find_all_file_matches(
            file_paths, re.compile(source_file_name))
        print(f'{len(matching_file_paths)} files found. Preparing to encrypt')
        if not os.path.exists(destination_folder_name) and (
                destination_folder_name != ''):
            os.makedirs(destination_folder_name)
        encrypt_files(matching_file_paths, destination_full_path, key)
        print(f'All files were encrypted into {destination_full_path}')
    else:
        if not os.path.exists(destination_folder_name) and (
                destination_folder_name != ''):
            os.makedirs(destination_folder_name)
        encrypt_file(source_full_path, destination_full_path, key)
        print(f'All files were encrypted into {destination_full_path}')

if __name__ == '__main__':
    main()