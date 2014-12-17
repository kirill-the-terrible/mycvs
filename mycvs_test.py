import os
import tempfile
from sys import stdout

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
MYCVS = SOURCE_DIR + '/mycvs.py'


def start_test():
    TEST_DIR = tempfile.mkdtemp()
    os.chdir(TEST_DIR)
    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' init'
    os.system(command_line)


def end_test():
    pass


def comparator(condition):
    if condition:
        stdout.write("Test passed\n\n")
    else:
        stdout.write("Test failed\n\n")


def test_init_creates_directory_mycvs_if_not_existed():
    start_test()

    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' init'
    print('Running:', command_line)
    os.system(command_line)
    comparator(os.path.isdir('.mycvs'))

    end_test()


def test_init_notice_user_if_repo_is_already_created():
    start_test()

    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' init'
    print('Running:', command_line)
    ans = os.popen(command_line).read()
    comparator(ans[:8] == "Warning:")

    end_test()


def test_commit_create_commit_if_its_first_commit():
    start_test()

    f = open('1', 'w')
    f.write('1')
    f.close()
    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' commit'
    print('Running:', command_line)
    comparator(os.popen(command_line).read()[:6] != 'Error:')

    end_test()


def test_commit_notice_user_if_commit_is_already_created():
    start_test()

    f = open('1', 'w')
    f.write('1')
    f.close()
    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' commit'
    print('Running:', command_line)
    os.system(command_line)
    print('Running:', command_line)
    comparator(os.popen(command_line).read()[:8] == 'Warning:')

    end_test()


def test_commit_create_commit_if_there_is_no_such_commit():
    start_test()

    f = open('1', 'w')
    f.write('1')
    f.close()
    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' commit'
    print('Running:', command_line)
    os.system(command_line)
    f = open('2', 'w')
    f.write('2')
    f.close()
    print('Running:', command_line)
    comparator(os.popen(command_line).read()[:6] != 'Error:')

    end_test()


def test_checkout_last_version():
    start_test()

    f = open('1', 'w')
    f.write('1')
    f.close()
    os.system(('python3 ' if os.name != 'nt' else '') + MYCVS + ' commit')
    f = open('1', 'w')
    f.write('2')
    f.close()
    command_line = ('python3 ' if os.name != 'nt' else '') + MYCVS + ' checkout 1'
    print('Running:', command_line)
    ans = os.popen(command_line).read()
    f = open('1')
    comparator(f.read() == '1' and ans[:6] != 'Error:')

    end_test()



test_init_creates_directory_mycvs_if_not_existed()
test_init_notice_user_if_repo_is_already_created()
test_commit_create_commit_if_its_first_commit()
test_commit_notice_user_if_commit_is_already_created()
test_commit_create_commit_if_there_is_no_such_commit()
test_checkout_last_version()
