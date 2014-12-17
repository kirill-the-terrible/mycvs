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


def list_hash(array):
    sha = hashlib.sha1()
    for elem in array:
        sha.update(bytearray(elem, encoding='utf-8') + b' ')
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
        root = root[2:]
        if '.mycvs' in root[:6]:  # ignore config folder
            continue
        if len(root):
            dirs.append(root)

        for single_file in filenames:
            path = os.path.join(root, single_file)
            h = file_hash(path)
            hashes.append(h)
            if not h in os.listdir('.mycvs/objects'):
                compress_and_copy_file(path, '.mycvs/objects/' + h)
            files.append(path + '\t' + h)

    out = '\n'.join(dirs) + '\n' + '\n'.join(files) + '\n'
    checksum = list_hash(sorted(hashes))
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
        for folder in dirs:
            os.makedirs(folder.rstrip())
        for i in range(len(files)):
            files[i] = files[i].rstrip().split('\t')
        for file, h in files:
            decompress_and_copy_file('.mycvs/objects/' + h, file)
    else:
        print('Error: No such version.')


def diff(before, after):
    import difflib
    if os.path.isfile(".mycvs/commits/" + before):
        f_in = open(".mycvs/commits/" + before)
        data = f_in.readlines()
        f_in.close()
        i = data.index('\n')
        before_files = {}
        for elem in data[i+1:]:
            name, obj = list(elem.rstrip().split('\t'))
            before_files[name] = obj
    else:
        print("Error: There is no such version - " + before)
        return

    if os.path.isfile(".mycvs/commits/" + after):
        f_in = open(".mycvs/commits/" + after)
        data = f_in.readlines()
        f_in.close()
        i = data.index('\n')
        after_files = {}
        for elem in data[i+1:]:
            name, obj = list(elem.rstrip().split('\t'))
            after_files[name] = obj
    else:
        print("Error: There is no such version - " + after)
        return

    for elem in before_files:
        if elem in after_files:
            i = elem.rfind('\\')
            filename = elem[i+1:].rstrip()
            before_file = gzip.open(".mycvs/objects/" + before_files[elem])
            after_file = gzip.open(".mycvs/objects/" + after_files.pop(elem))
            for line in difflib.context_diff(before_file.readlines(), after_file.readlines(), fromfile=filename, tofile=filename):
                sys.stdout.write(line)
            sys.stdout.write('\n')
            before_file.close()
            after_file.close()
        else:
            sys.stdout.write("Deleted " + elem + '\n\n')
    for elem in after_files:
        sys.stdout.write("Created " + elem + '\n\n')


if __name__ == "__main__":
    command = sys.argv[1]

    if command == 'init':
        init()

    if command == 'commit':
        commit()

    if command == 'checkout':
        try:
            checkout(sys.argv[2])
        except IndexError:
            print("Error: command [checkout] takes exactly 1 argument - version number")

    if command == 'status':
        status()

    if command == 'diff':
        try:
            diff(sys.argv[2], sys.argv[3])
        except IndexError:
            print("Error: command [diff] takes exactly 2 arguments - number of versions to be compared")
