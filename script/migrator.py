import base64
import requests
from multiprocessing import Pool
import subprocess
import os
from json import load, dump
from status import StatusManager
from git_commands import GitCommands
status = StatusManager()
git = GitCommands()


class Migrator:
    def __init__(self, gh_handle, gh_token, gh_organization, git_server, working_path, script_path):
        self.gh_org = gh_organization
        self.auth_header_gh = self._authorization_header_gh(gh_token)
        self.script_path = script_path
        self.repo_list = self.load_json_file(
            fr"{self.script_path}/", "git_repo_list.json")
        self.repo_list_lfs = self.load_json_file(
            fr"{self.script_path}/", "git_repo_list_lfs.json")
        self.git_server = git_server
        self.working_path = working_path
        self.gh_token = gh_token
        self.gh_handle = gh_handle
        self.lfs = False

    @staticmethod
    def _authorization_header_gh(pat: str) -> str:
        return "Basic " + base64.b64encode(f":{pat}".encode("ascii")).decode("ascii")

    @staticmethod
    def _authorization_header_ado(pat: str) -> str:
        return "Basic " + base64.b64encode(f":{pat}".encode("ascii")).decode("ascii")

    @staticmethod
    def _authorization_header_gitlab(token: str) -> str:
        return "Bearer " + token

    def _git_clone_pull(self, origin_repo, target_repo, lfs=False):
        status_, error_, working_path, git_server = "status", "error", self.working_path, self.git_server
        if lfs == True:
            status_, error_ = "status_lfs", "error_lfs"
        os.chdir(f"{working_path}")
        if(os.path.isdir(f"{working_path}/{target_repo}")):
            os.chdir(f"{working_path}/{target_repo}")
            status.list(1, target_repo)
            git.set_remote_url(self.script_path,self.working_path, target_repo,
                               fr"{git_server}/{origin_repo}", error_)
            git.fetch(self.script_path,self.working_path, target_repo, error_)
        else:
            status.list(1, target_repo)
            git.clone_bare(self.script_path,self.working_path, git_server,
                           origin_repo, target_repo, error_)
        self.append_json(status_, target_repo,
                         {"level": 1, "check": True})
        self.amount_tags_branches_source(
            fr"{working_path}/{target_repo}", target_repo, lfs)
        self.checking_repo_size(
            fr"{working_path}/{target_repo}", target_repo, "source", lfs)

    def _git_clone_gh(self,  target_repo, lfs=False):
        error_ = "error"
        if lfs == True:
            error_ = "error_lfs"
        working_path = self.working_path
        os.chdir(f"{working_path}")
        res = True
        if(os.path.isdir(f"{working_path}/{target_repo}_github")):
            os.chdir(f"{working_path}/{target_repo}_github")
            git.fetch(self.script_path,self.working_path, target_repo, error_)
            if res == True:
                self.checking_repo_size(
                    fr"{working_path}/{target_repo}_github", target_repo, "github", lfs)
        else:
            res = git.clone_bare_gh(self.script_path,
                self.working_path, target_repo, error_, self.gh_token, self.gh_handle,self.gh_org)
            if res == True:
                self.checking_repo_size(
                    fr"{working_path}/{target_repo}_github", target_repo, "github", lfs)

    def _push_repo_gh(self, gh_repo, target_repo, lfs=False):
        status.list(3, target_repo)
        status_ = "status"
        error_ = "error"
        if lfs == True:
            error_ = "error_lfs"
            status_ = "status_lfs"
        working_path = self.working_path
        os.chdir(f"{working_path}/{target_repo}")
        remote_url = fr"https://{self.gh_handle}:{self.gh_token}@github.com/{self.gh_org}/{target_repo}.git"
        git.set_remote_url(self.script_path,self.working_path, target_repo, remote_url, error_)
        git.mk_main_default_branch(self.script_path,self.working_path, target_repo, error_)

        # Following git commmands will clean the repo form old garbage and decrease the size of the repo.
        # git.run_gc_prune(self.script_path,self.working_path, target_repo)
        # git.run_gc_repack(self.script_path,self.working_path, target_repo)        

        if lfs == True:
                lfs_initl = git.initialize_lfs(self.script_path,
                    self.working_path, target_repo, "error_lfs")
                if lfs_initl == True:
                    push_repo = git.push_all(self.script_path,
                        self.working_path, target_repo, "error_lfs", True)
                    if push_repo == True:
                        git.push_tags(self.script_path,self.working_path, target_repo, "error_lfs")
                        self.append_json(status_, target_repo, {
                            "level": 3, "check": True})
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            push_repo = git.push_all(self.script_path,self.working_path, target_repo, error_, False)
            if push_repo == True:
                git.push_tags(self.script_path,self.working_path, target_repo, error_)
                self.append_json(status_, target_repo, {
                    "level": 3, "check": True})
                return True
            else:
                return False

    def _create_gh_repo(self, repo_name, lfs=True):
        status.list(2, repo_name)
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        repo_details = {
            "name": f"{repo_name}",
            "description": "",
            "homepage": "",
            "visibility": "internal"
        }
        res = requests.post(
            f"https://api.github.com/orgs/{self.gh_org}/repos",
            headers={
                "Authorization": self.auth_header_gh,
                "Content-Type": "application/json",
            },
            json=repo_details,
        ).json()
        self.append_json(status_, repo_name, {
            "level": 2, "check": True})
        return res

    def _delete_gh_repo(self, repo):
        repo_name = repo["Target-repo"]
        print(f"Deleting {repo_name}")
        requests.delete(
            fr"https://api.github.com/repos/{self.gh_org}/{repo_name}",
            headers={
                "Authorization": self.auth_header_gh,
                "Content-Type": "application/json",
            },
        )

    def _get_gh_repo(self):
        print("Getting gh repo")
        res = requests.get(
            f"https://api.github.com/orgs/{self.gh_org}/repos?per_page=100",
            headers={
                "Authorization": self.auth_header_gh,
                "Content-Type": "application/json",
            },
        ).json()
        list = {}
        for item in res:
            list[item["name"]] = item["size"]
        response = {"res": res, "list": list}
        return response

    def _delete_local_repo(self, repo_name):
        os.chdir(self.working_path)
        subprocess.check_call(["rm", "-r", repo_name])

    def load_json_file(self, working_path, file_name: str):
        f = open(fr"{working_path}/{file_name}")
        data = load(f)
        return data

    def create_json(self, folder_name, repo_name, key, attr):
        with open(fr"{self.script_path}/{folder_name}/{repo_name}.json", 'w+') as file:
            content = {fr"{repo_name}": {fr"{key}": attr}}
            dump(content, file)
            print("file created")

    def append_json(self, folder_name, repo_name, msg):
        with open(fr"{self.script_path}/{folder_name}/{repo_name}.json", 'r+') as file:
            file_data = load(file)
            file_data[fr"{repo_name}"].update(msg)
            file.seek(0)
            dump(file_data, file)
            file.truncate()

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True
            else:
                return False

    def _error_manager(self, repo_name, lfs=False):
        error_ = "error"
        if lfs == True:
            error_ = "error_lfs"
        path = fr"{self.script_path}/{error_}"
        find_file = self.find(fr"{repo_name}.json", path)
        if find_file == True and lfs == False:
            error_file = self.load_json_file(
                fr"{self.script_path}/{error_}/", fr"{repo_name}.json")
            if "msg" in error_file[repo_name]:
                return False
            else:
                return True
        else:
            self.create_json(error_, repo_name, "Initialize", error_)
            return True

    def _status_manager(self, repo_name, lfs=False):
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        path = fr"{self.script_path}/{status_}"
        find_file = self.find(fr"{repo_name}.json", path)
        if find_file == True:
            status_file = self.load_json_file(
                fr"{self.script_path}/{status_}/", fr"{repo_name}.json")
            if "level" in status_file[repo_name]:
                progress_level = status_file[repo_name]["level"]
                print("Level:", progress_level)
                res = {"level": progress_level, "check": True}
                return res
            else:
                res = {"level": progress_level, "check": True}
                return res
        else:
            self.create_json(status_, repo_name, "level", 0)
            res = {"level": 0, "check": True}
            return res

    def checking_repo_size(self, working_path, target_repo, source, lfs=False):
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        if(os.path.isdir(f"{working_path}")):
            os.chdir(f"{working_path}")
            size = subprocess.Popen(
                "du -skh", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            size = size.replace('\t.', '')
            self.append_json(status_, target_repo, {
                fr"size_{source}": size})

    def checking_repo_size_github(self, target_repo, lfs=False):
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        size = 0
        res = requests.get(
            f"https://api.github.com/repos/{self.gh_org}/{target_repo}",
            headers={
                "Authorization": self.auth_header_gh,
                "Content-Type": "application/json",
            },
        ).json()
        size = res["size"]
        self.append_json(status_, target_repo, {
            "size_github": size})

    def amount_tags_branches_source(self, working_path, target_repo, lfs=False):
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        if(os.path.isdir(f"{working_path}")):
            os.chdir(f"{working_path}")
            tags = subprocess.Popen(
                "git tag |wc -l", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            branches = subprocess.Popen(
                "git branch |wc -l", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            if branches == '':
                branches = 0
            else:
                branches = int(branches)
            if tags == '':
                tags = 0
            else:
                tags = int(tags)
            self.append_json(status_, target_repo, {
                "branches_source": branches})
            self.append_json(status_, target_repo, {
                "tags_source": tags})
            return True

    def amount_tags_branches_gh(self, working_path, target_repo, lfs=False):
        status_ = "status"
        if lfs == True:
            status_ = "status_lfs"
        if(os.path.isdir(f"{working_path}_github")):
            os.chdir(f"{working_path}_github")
            tags = subprocess.Popen(
                "git tag |wc -l", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            branches = subprocess.Popen(
                "git branch |wc -l", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            if branches == '':
                branches = 0
            else:
                branches = int(branches)
            if tags == '':
                tags = 0
            else:
                tags = int(tags)
            self.append_json(status_, target_repo, {
                "branches_github": branches})
            self.append_json(status_, target_repo, {
                "tags_github": tags})
            return True

    def _runner(self, repo, gh_repo=""):
        lfs = self.lfs
        status_, origin_repo, target_repo,  = "status", repo[
            "Origin-repo"], repo["Target-repo"], 
        _error_manager, _status_manager = self._error_manager(target_repo, lfs), self._status_manager(target_repo, lfs)
        if lfs == True:
            status_ = "status_lfs"
        if _error_manager == True and _status_manager["check"] == True:
            if _status_manager["level"] < 4:
                match _status_manager["level"]:
                    case 0:
                        status.list(0, target_repo, 0)
                        self._git_clone_pull(
                            origin_repo, target_repo, lfs)
                        self._runner(repo, gh_repo)
                    case 1:
                        gh_repo = self._create_gh_repo(target_repo, lfs)
                        self._runner(repo, gh_repo)
                    case 2:
                        status_report = {
                            "Origin-repo": origin_repo,
                            "Target-repo": target_repo
                        }
                        self.append_json(status_, target_repo, status_report)
                        if isinstance(gh_repo, dict):
                            res = self._push_repo_gh(
                                gh_repo,  target_repo, lfs)
                            if res == True:
                                self._runner(repo, gh_repo)
                        else:
                            gh_repo, res = {"errors": "errors"}, self._push_repo_gh(
                                gh_repo, target_repo, lfs)
                            if res == True:
                                self._runner(repo, gh_repo)
                    case 3:
                        status.list(4, target_repo, 0)
                        status_report = {
                            "level": 4,
                        }
                        self.append_json(status_, target_repo, status_report)
                        self._git_clone_gh(target_repo, lfs)
                        self.amount_tags_branches_gh(
                            fr"{self.working_path}/{target_repo}", target_repo, lfs)
                        self._runner(repo, gh_repo)
            else:
                print(target_repo, " Already migrated!",)
        else:
            print(target_repo, "Other issue, check error/status report")

    def initializer(self, lfs=False, delete=False):
        pool, self.lfs, repos = Pool(), lfs, self.repo_list
        if lfs == True:
            repos = self.repo_list_lfs

        # Deletes all repos in GitHub, that exist in git_repo_list.json file
        if delete == True:
            pool.map(self._delete_gh_repo, repos)
        else:
            # Migration flow
            pool.map(self._runner, repos)
