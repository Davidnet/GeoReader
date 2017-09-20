import obspy
import argparse
import os
import magic
import errno
from pathlib import Path
import sys
import tempfile
import shutil
import gzip
import glob
import subprocess


if __name__ == '__main__':
    # Parsing and owning hack
    subprocess.call("./ownership.sh", shell = True)
    subprocess.call("./usbreader.sh", shell = True)
    # reading usb disks
    with open('usbreader.txt','r') as f:
        first_line = f.readline().strip()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s',
        '--station',
        dest='station',
        type=str,
        required=True)
    parser.add_argument(
        '-o',
        '--output-format',
        dest='output_format',
        type=str,
        default="MSEED")
    parser.add_argument(
        '-d',
        '--directory',
        dest='walk_dir',
        type=str,
        default=first_line)
    parser.add_argument(
        '-od',
        '--output-directory',
        dest='out_dir',
        type=str,
        default=str(
            Path.home()))
    args = parser.parse_args()
    try:
        out_path = os.path.join(args.out_dir, 'Converted', args.station)
        os.makedirs(out_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print('Folder already exist, please delete the folder before running!')
            sys.exit()
    tempdir = tempfile.mkdtemp()
    pathtmp = ""
    print('Creating temporary folder at: ' + tempdir)
    walk_dir = args.walk_dir
    print('walk_dir = ' + walk_dir)
    # We revise every file and directory on the walk_dir file things might
    # broke if do not use abspath
    print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))
    for root, subdirs, files in os.walk(walk_dir):
        # print('--\nDirectory to read = ' + root)
        for subdir in subdirs:
            # print('\t- Subdirectory to read = ' + subdir)
        for filename in files:
            file_path = os.path.join(root, filename)
            # print('\t- file %s (full path: %s)' % (filename, file_path))
            file_type = magic.from_file(file_path)
            print('\n type of the file trying to read:' + file_type)
            # print('\n filename: ' + filename)
            with open('trouble_files', 'a') as txt_file:
                if file_type == 'data':
                    try:
                        name = filename.split('.')[0]
                        st = obspy.read(file_path)
                        print(st)
                        stsel = st.select(station=args.station)
                        print(stsel)
                        out_write = os.path.join(
                            out_path, name + '.' + args.output_format.lower())
                        stsel.write(
                            out_write, format=args.output_format.upper())
                    except BaseException:
                        txt_file.write(
                            'file problem with: ' + filename + ' at' + file_path)
                        pass
                elif 'compressed' in file_type:
                    try:
                        name = filename.split('.')[0]
                        compressed_file = shutil.copy2(file_path, tempdir)
                        with gzip.open(compressed_file, 'rb') as infile:
                            fd, pathtmp = tempfile.mkstemp()
                            with open(pathtmp, 'w') as temp_file:
                                for line in infile:
                                    temp_file.write(line)
                            os.close(fd)
                        file_type = magic.from_file(pathtmp)
                        if file_type == 'data':
                            try:
                                st = obspy.read(pathtmp)
                                print(st)
                                stsel = st.select(station=args.station)
                                print(stsel)
                                out_write = os.path.join(
                                    out_path, name + '.' + args.output_format.lower())
                                stsel.write(
                                    out_write, format=args.output_format.upper())
                            except BaseException:
                                txt_file.write(
                                    'file problem with: ' + filename + ' at' + file_path)
                                pass
                        elif 'tar' in file_type:
                            # print('TAR FILE AVOIDING!')  # TODO: tar file
                    except BaseException:
                        txt_file.write(
                            'file problem with: ' + filename + ' at' + file_path)
                        pass
                    else:
                        pass
                trash = glob.glob(os.path.join(tempdir, '*'))
                for tfiles in trash:
                    os.remove(tfiles)
                try:
                    if os.path.exists(pathtmp):
                        os.remove(pathtmp)
                except BaseException:
                    pass

    print('Execution of the program has finished!, Please support the developer')
