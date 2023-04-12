# All code from this file from: https://discussions.apple.com/thread/250067410

import sys
import os
import subprocess

default_path = os.path.expanduser('~/Desktop')


def user_action(apath, cmd):
    ascript = '''
    -- apath - default path for dialogs to open too
    -- cmd   - "Select", "Save"
    on run argv
        set userCanceled to false
        if (count of argv) = 0 then
            tell application "System Events" to display dialog "argv is 0" ¬
                giving up after 10
        else
            set apath to POSIX file (item 1 of argv) as alias
            set action to (item 2 of argv) as text
        end if
        try
        if action contains "Select" then
            set fpath to POSIX path of (choose file default location apath ¬
                     without invisibles, multiple selections allowed and ¬
                     showing package contents)
            # return fpath as text
        else if action contains "Save" then
            set fpath to POSIX path of (choose file name default location apath)
        end if
        return fpath as text
        on error number -128
            set userCanceled to true
        end try
        if userCanceled then
            return "Cancel"
        else
            return fpath
        end if
    end run
    '''
    try:
        proc = subprocess.check_output(['osascript', '-e', ascript,
                                       apath, cmd])
        if 'Cancel' in proc.decode('utf-8'):  # User pressed Cancel button
            #sys.exit('User Canceled')
            return 'User Canceled'
        return proc.decode('utf-8')
    except subprocess.CalledProcessError as e:
            print('Python error: [%d]\n%s\n' % e.returncode, e.output)


def main():
    # opens AppleScript choose file dialog and returns UNIX filename
    fname = user_action(default_path, "Select").strip()
    print(fname)
    # opens AppleScript Save As file dialog and returns UNIX filename
    fname = user_action(default_path, "Save").strip()
    print(fname)

    # write data to filename returned from Save As dialog
    with open(fname, 'w') as f:
        outstr = "Filename: {}\n".format(fname)
        f.write(outstr)


if __name__ == '__main__':
    sys.exit(main())