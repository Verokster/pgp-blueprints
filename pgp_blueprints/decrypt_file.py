import os
import glob
import re
import argparse
import pgpy
        
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--source-file-name-match-type',
        dest='PGP_SOURCE_FILE_NAME_MATCH_TYPE',
        default='exact_match',
        choices={
            'exact_match',
            'regex_match'},
        required=False)
    parser.add_argument(
        '--source-folder-name',
        dest='PGP_SOURCE_FOLDER_NAME',
        default='',
        required=False)
    parser.add_argument(
        '--source-file-name',
        dest='PGP_SOURCE_FILE_NAME',
        required=True)
    parser.add_argument(
        '--destination-file-name',
        dest='PGP_DESTINATION_FILE_NAME',
        default=None,
        required=False)
    parser.add_argument(
        '--destination-folder-name',
        dest='PGP_DESTINATION_FOLDER_NAME',
        default='',
        required=False)
    parser.add_argument(
        '--pgp-private-key',
        dest='PGP_PRIVATE_KEY',
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

def decrypt_file(
        source_file_name,
        destination_file_name,
        key):
        
    encrypted = pgpy.PGPMessage.from_file(source_file_name)
    pgp = key.decrypt(encrypted).message
    
    with open(destination_file_name, "w" if isinstance(pgp, str) else "wb") as f:
        f.write(pgp)

def main():
    args = get_args()

    key = pgpy.PGPKey()
    key.parse(args.PGP_PRIVATE_KEY)
    
    source_file_name = args.PGP_SOURCE_FILE_NAME
    source_folder_name = clean_folder_name(args.PGP_SOURCE_FOLDER_NAME)
    source_full_path = combine_folder_and_file_name(
        folder_name=source_folder_name, file_name=source_file_name)
    source_file_name_match_type = args.PGP_SOURCE_FILE_NAME_MATCH_TYPE
    destination_folder_name = clean_folder_name(args.PGP_DESTINATION_FOLDER_NAME)
    destination_file_name = args.PGP_DESTINATION_FILE_NAME
    destination_full_path = combine_folder_and_file_name(
        destination_folder_name, destination_file_name)

    if source_file_name_match_type == 'regex_match':
        file_paths = find_all_local_file_names(source_folder_name)
        matching_file_paths = find_all_file_matches(
            file_paths, re.compile(source_file_name))
        print(f'{len(matching_file_paths)} files found. Preparing to decrypt first match')
        if not os.path.exists(destination_folder_name) and (
                destination_folder_name != ''):
            os.makedirs(destination_folder_name)

        for source_file in matching_file_paths:
            decrypt_file(source_file, destination_file_name, key)
            break

    else:
        if not os.path.exists(destination_folder_name) and (
                destination_folder_name != ''):
            os.makedirs(destination_folder_name)
        decrypt_file(source_full_path, destination_full_path, key)
    
    print(f'File was decrypted into {destination_full_path}')

if __name__ == '__main__':
    main()