import os
import sys
import json
import global_config
import hashlib
import zipfile

def handle_options_status(cmd_parser):

    cmd_parser.add_argument('-v', '--version',
                          help="version",
                          action="store_true")

    cmd_parser.add_argument('-j', '--json',
                             action='store_true', 
                             default=False)

    cmd_parser.add_argument('-d', '--dir',
                          action="store",
                          dest="root_dir",
                          help="Staus of the repository")

    cmd_parser.set_defaults(func=status)

def write_status_to_file(status_file, current_status):
    with open(status_file, 'w') as f:
        f.write(json.dumps(current_status))

def has_diff(file1, file2):

    hash_value1 = hashlib.md5(open(file1, 'r', encoding="utf8", errors='ignore').read().encode()).hexdigest()
    hash_value2 = hashlib.md5(open(file2, 'r', encoding="utf8", errors='ignore').read().encode()).hexdigest()

    return hash_value1 != hash_value2

def get_push_status(current_branch):

    dlv_dir = os.path.join(global_config.root_dir, global_config.DLV_DIR)

    config_dict = {}
    with open(os.path.join(dlv_dir, global_config.CONFIG_FILE), 'r') as f:
        config_dict = json.load(f)

    local_branch_path = os.path.join(dlv_dir, current_branch)
    if 'username' not in config_dict:
        return "Not pushed to server\n" + \
               "local is ahead of server by " + str(global_config.commit_counter(local_branch_path) - 1) + " commits"

    project_server_dir = os.path.join(global_config.SERVER_PROJECT_DIR, config_dict['username'], config_dict['project_name'])

    server_branch_path = os.path.join(project_server_dir, global_config.DLV_DIR, current_branch)

    diff_of_commits = abs(global_config.commit_counter(server_branch_path) - global_config.commit_counter(local_branch_path))
    if diff_of_commits == 0:
        return "Updated"
    else:
        return "local is ahead of server by " + str(diff_of_commits) + " commits"
    

def get_status(orig_file):

    if orig_file.startswith("\\"): # only modify the text if it starts with the prefix
        orig_file = orig_file.replace("\\", "", 1)

    current_branch = global_config.get_current_branch()
    branch_path = os.path.join(global_config.root_dir, global_config.DLV_DIR, current_branch)

    index_file = os.path.join(branch_path, global_config.STAGE_DIR, orig_file)

    rel_orig_file = orig_file
    orig_file = os.path.join(global_config.root_dir, orig_file)
    file_version = str(global_config.get_last_file_version(branch_path, rel_orig_file))
    last_commit_file = os.path.join(branch_path, global_config.CACHE_DIR, rel_orig_file + "." + file_version)
    
    if os.path.exists(orig_file):
        if os.path.exists(index_file):
            if has_diff(orig_file, index_file):
                return "Modified Files"
            else:
                return "Staged Files"
        elif os.path.exists(last_commit_file):
            if has_diff(orig_file, last_commit_file):
                return "Modified Files"
            else:
                return "Tracked Files"
        else:
            return "Untracked Files"
    else:
        return "Deleted Files" # this case never happens - check from commit history log      

def print_status(file_status):
    for status in file_status.keys():
        if status == "Tracked Files":
            continue
        print(status)
        for f in file_status[status]:
            print("\t" + f)
        print("\n")

def status(args = {}):

    
    if args.root_dir != None:
        global_config.root_dir = args.root_dir

    if not global_config.check_dlv_exists():
        print("No dlv repository exists")
        sys.exit()


    current_branch = global_config.get_current_branch()
    branch_path = os.path.join(global_config.root_dir, global_config.DLV_DIR, current_branch)

    status_log = os.path.join(branch_path, global_config.STATUS_FILE)

    file_status = {}
    file_status["Untracked Files"] = []
    file_status["Modified Files"] = []
    file_status["Deleted Files"] = []
    file_status["Staged Files"] = []
    file_status["Tracked Files"] = []

    root_folder = ''
    for folder, subfolders, files in os.walk( global_config.root_dir ):

        if global_config.DLV_DIR in folder or global_config.GIT_DIR in folder:
            continue

        root_folder = folder.split(global_config.root_dir)[1]

        for f in files:
            orig_file = os.path.join(root_folder, f)
            if orig_file.startswith("\\"): # only modify the text if it starts with the prefix
                orig_file = orig_file.replace("\\", "", 1)
            file_status[get_status(orig_file)].append(orig_file)
           

    write_status_to_file(status_log, file_status)

    if args.json:
        print(json.dumps(file_status, indent=4))
    elif (len(file_status["Untracked Files"]) == 0) and (len(file_status["Modified Files"]) == 0) and (len(file_status["Staged Files"]) == 0) :
        print("All files in the current repository and branch: " + current_branch + " are up-to-date")
    else:
        print_status(file_status)
    
    # status about server and local
    if not args.json:
        server_status = get_push_status(current_branch)
        if server_status == "Updated":
            print("Server is up-to-date with all the commits")
        else:
            print(server_status) 
