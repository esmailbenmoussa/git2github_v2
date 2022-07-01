import os
from json import load, dump
from status import StatusManager
status = StatusManager()


class Analyzor:
    def __init__(self, gh_handle, gh_token, gh_organization, git_server, working_path, script_path):
        self.gh_org = gh_organization
        self.git_server = git_server
        self.working_path = working_path
        self.script_path = script_path
        self.list = {}


    def load_json_file(self, file_name: str):
        f = open(file_name)
        data = load(f)
        return data
        

    def create_json(self, folder_name, repo_name, key, attr):
        with open(fr"{self.script_path}/{folder_name}/{repo_name}.json", 'w+') as file:
            content = {fr"{repo_name}": {fr"{key}": attr}}
            dump(content, file)
            print("file created")

    def append_json(self, folder_name, repo_name, msg):
        with open(folder_name, 'r+') as file:
            file_data = load(file)
            if type(file_data) is dict:
                file_data[repo_name] = msg
            else:
                file_data.append(msg)
            file.seek(0)
            dump(file_data, file)
            file.truncate()

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True
            else:
                return False

    def initializer(self, lfs=False):
        path = self.script_path
        result_migrated = "result_migrated"
        result_failed = "result_failed"
        status_ = "status"
        repo_list = "git_repo_list_lfs"
        if lfs is True:
            result_migrated = "result_migrated_lfs"
            result_failed = "result_failed_lfs"
            status_ = "status_lfs"
            repo_list = "git_repo_list_lfs_leftovers"
        find_file = self.find(fr"{result_migrated}.json", fr"{path}/result")
        if find_file is True:
            files = []
            for root, dirs, files in os.walk(fr"{path}/{status_}"):
                files = files
            for file in files:
                status_file = self.load_json_file(
                    fr"{path}/{status_}/{file}")
                name = file[0: -5]
                print("Status on: ", name)
                if "level" in status_file[name]:
                    progress_level = status_file[name]["level"]
                    print("Level:", progress_level)
                    if progress_level < 4:
                        result = {"level": progress_level}
                        self.append_json(
                            fr"{self.script_path}/result/{result_failed}.json", name, result)
                        if progress_level == 2:
                            lfs_result = {
                                "Origin-repo": status_file[name]["Origin-repo"],
                                "Target-repo": status_file[name]["Target-repo"]
                            }
                            git_repo_list_lfs = self.load_json_file(fr"{self.script_path}/{repo_list}.json")
                            if lfs_result not in git_repo_list_lfs:
                                self.append_json(fr"{self.script_path}/{repo_list}.json", name, lfs_result)
                            

                    else:
                        result = "Migrated"
                        # Branch and tags check
                        branches_source = status_file[name]["branches_source"]
                        branches_github = status_file[name]["branches_github"]
                        tags_source = status_file[name]["tags_source"]
                        tags_github = status_file[name]["tags_github"]
                        size_source = status_file[name]["size_source"]
                        size_github = status_file[name]["size_github"]

                        res = {"branches_source": branches_source, "branches_github": branches_github, "tags_source": tags_source,
                               "tags_github": tags_github, "size_source": size_source, "size_github": size_github}
                        self.append_json(
                            fr"{self.script_path}/result/{result_migrated}.json", name, res)

        else:
            self.create_json("result", result_migrated, "Initialize", "result")
            self.create_json("result", result_failed,
                             "Initialize", "result")
            self.initializer(lfs)
