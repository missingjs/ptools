import os.path
import sys

def find(top_dir, blacklist):
    if not os.path.exists(top_dir):
        print(f'warn: directory {top_dir} not exist', file=sys.stderr)
        return

    if top_dir in blacklist:
        return

    html_index = f'{top_dir}/index.html'
    if os.path.exists(html_index):
        yield top_dir
        return

    for sub_name in os.listdir(top_dir):
        sub_path = f'{top_dir}/{sub_name}'
        if os.path.isdir(sub_path):
            yield from find(sub_path, blacklist)

def path_strip(path):
    return path[:-1] if path.endswith('/') else path

def main():
    if len(sys.argv) < 2:
        print('usage: python3 findweb.py <web-source-dirs> [<skip-dirs>]', file=sys.stderr)
        sys.exit(1)

    src_dirs = list(map(path_strip, sys.argv[1].split(':')))
    blacklist = set()

    if len(sys.argv) >= 3:
        blacklist = set(map(path_strip, sys.argv[2].split(':')))

    for d in src_dirs:
        for path in find(d, blacklist):
            print(path)

if __name__ == '__main__':
    main()

