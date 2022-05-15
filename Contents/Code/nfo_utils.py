import glob


def find_nfo_file_in_folder(folder):
    answer = None
    extension = "nfo"
    pattern = "{f}/*.{e}".format(f=folder, e=extension)
    nfo_files = glob.glob(pattern)
    if len(nfo_files) == 1:
        answer = nfo_files[0]
    
    return answer
    