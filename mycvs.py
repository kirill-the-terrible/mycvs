import os
import sys
import shutil
import hashlib
import time
import gzip


structure = {
    'folders': [
        '.mycvs/commits',
        '.mycvs/objects'
    ],
    'files': [
        '.mycvs/status',
        '.mycvs/commits/last_version',
        '.mycvs/commits/checksums',
        '.mycvs/history'
    ]
}


def file_hash(path):
    input_file = open(path, 'rb')
    sha = hashlib.sha1()
    sha.update(input_file.read())
    return sha.hexdigest()


def string_list_hash(array):
    sha = hashlib.sha1()
    for elem in array:
        sha.update(elem.encode())
    return sha.hexdigest()


def commit_is_exist(commit_checksum):
    checksum_file = open('.mycvs/commits/checksums')
    checksums = checksum_file.readlines()
    checksum_file.close()
    for row in checksums:
        version, h = row.split()
        if h == commit_checksum:
            return version
    return False


def compress_and_copy_file(src, dst):
    source = open(src, 'rb')
    dist = gzip.open(dst, 'wb')
    dist.write(source.read())
    source.close()
    dist.close()


def decompress_and_copy_file(src, dst):
    source = gzip.open(src, 'rb')
    dist = open(dst, 'wb')
    dist.write(source.read())
    source.close()
    dist.close()


def init():
    if os.path.isdir('.mycvs'):
        print('Warning: Repository has been already created.')
    else:
        for folder in structure['folders']:
            os.makedirs(folder)
        for filename in structure['files']:
            open(filename, 'w').close()
        print('Repository has been created successfully')


def commit():
    version_file = open('.mycvs/commits/last_version')  # Takes number of last commit
    last_version = int((version_file.readline().rstrip() or 0))
    version_file.close()

    walk = os.walk(os.path.relpath(os.path.abspath(''), ''))  # Walk throught the project and collects all files and
    # directories
    files = []
    dirs = []
    hashes = []
    for root, dirnames, filenames in walk:
        if '.mycvs' in root[:9]:  # ignore config folder
            continue
        dirs.append(root)
        for single_file in filenames:
            path = os.path.join(root, single_file)
            h = file_hash(path)
            hashes.append(h)
            if not h in os.listdir('.mycvs/objects'):
                compress_and_copy_file(path, '.mycvs/objects/' + h)
            files.append(path + '\t' + h)

    out = '\n'.join(dirs) + '\n\n' + '\n'.join(files) + '\n'
    checksum = string_list_hash(sorted(hashes))
    same_commit = commit_is_exist(checksum)
    if same_commit:
        print('Warning: This commit is the same with ' + same_commit)
    else:
        last_version += 1
        commit_file = open('.mycvs/commits/' + str(last_version), 'w')
        commit_file.write(out)
        commit_file.close()

        checksum_file = open('.mycvs/commits/checksums', 'a')
        checksum_file.write(str(last_version) + '\t' + checksum + '\n')
        checksum_file.close()

        version_file = open('.mycvs/commits/last_version', 'w')
        version_file.write(str(last_version))
        version_file.close()

        hisory_file = open('.mycvs/history', 'a')
        info = "Version #" + str(last_version) + "\nWas created " + time.strftime('%d.%m.%Y %A %H:%M:%S UTC%z') + \
               "\nCommit signature " + checksum + '\n\n'
        hisory_file.write(info)
        hisory_file.close()

        print('Commit was created successfully. Current version is ' + str(last_version))


def status():
    status_file = open('.mycvs/history')
    print(status_file.read())
    status_file.close()


def checkout(version):
    if os.path.isfile('.mycvs/commits/' + version):
        project = os.listdir(os.path.abspath(''))
        project.remove('.mycvs')
        for obj in project:
            if os.path.isdir(obj):
                shutil.rmtree(obj)
            else:
                os.remove(obj)

        commit_file = open('.mycvs/commits/' + version)
        data = commit_file.readlines()
        commit_file.close()

        i = data.index('\n')
        dirs = data[:i]
        files = data[i + 1:]
        for folder in dirs[1:]:
            os.makedirs(folder.rstrip()[2:])
        for i in range(len(files)):
            files[i] = files[i].rstrip().split('\t')
        for file, h in files:
            decompress_and_copy_file('.mycvs/objects/' + h, file)
    else:
        print('Error: No such version.')


if __name__ == "__main__":
    command = sys.argv[1]

    if command == 'init':
        init()

    if command == 'commit':
        commit()

    if command == 'checkout':
        try:
            version = sys.argv[2]
            checkout(version)
        except IndexError:
            print("Error: command [checkout] takes exactly 1 argument - version number")

    if command == 'status':
        status()