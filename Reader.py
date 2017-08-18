import obspy
import argparse
import os
import magic
import tarfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--file-id', dest = 'file_id', type = str)
    parser.add_argument('-s', '--station', dest = 'station', type = str)
    parser.add_argument('-o', '--output-format', dest = 'output_format', type = str)
    parser.add_argument('-d','--directory', dest = 'walk_dir', type = str)
    args = parser.parse_args()

    walk_dir = args.walk_dir

    print('walk_dir = ' + walk_dir)

    # We revise every file and directory on the walk_dir file things might broke if do not use abspath
    print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

    for root, subdirs, files in os.walk(walk_dir):
        print('--\nDirectory to read = ' + root)
        list_file_path = os.path.join(root, 'my-directory-list.txt')
        print('list_file_path = ' + list_file_path)

        with open(list_file_path, 'wb') as list_file:
            for subdir in subdirs:
                print('\t- Subdirectory to Read ' + subdir)

            for filename in files:
                file_path = os.path.join(root, filename)

                print('\t- file %s (full path: %s)' % (filename, file_path))

                file_type = magic.from_file(file_path)

                print('\n type of the file trying to read:' + file_type)

                if file_type == 'data':
                    st = obspy.read(file_path)
                    print(st)
                    stsel = st.select(station=args.station)
                    print(stsel)
                    stsel.write(file_path + args.station + "." + args.output_format.lower(), format=args.output_format.upper())

                else:
                    continue
