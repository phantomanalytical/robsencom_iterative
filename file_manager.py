import os
import gzip

def get_file_info(file_path):
    size = os.path.getsize(file_path)
    print(f"File: {file_path}, Size: {size} bytes")
    return file_path, size

def compress_file(file_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            f_out.writelines(f_in)
    return file_path + '.gz'

def decompress_file(file_path):
    with gzip.open(file_path, 'rb') as f_in:
        with open(file_path.replace('.gz', ''), 'wb') as f_out:
            f_out.writelines(f_in)
    return file_path.replace('.gz', '')
