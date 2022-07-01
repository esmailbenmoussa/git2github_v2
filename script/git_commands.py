import subprocess
import os
from json import load, dump


class GitCommands:
    def write_json(self, folder_path, folder_name, repo_name, msg):
        with open(fr"{folder_path}/{folder_name}/{repo_name}.json", 'r+') as file:
            file_data = load(file)
            file_data[repo_name] = msg
            file.seek(0)
            dump(file_data, file)
            file.truncate()

    def push_tags(self, script_path, working_path, repo_name, write_json_file):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            subprocess.check_call(
                ["git", "push", "--tags", "origin"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg})

    def run_gc_prune(self, script_path,working_path, repo_name):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            subprocess.check_call(
                ["git", "gc", "--prune=now"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,"error", repo_name, {"msg": error_msg})

    def run_gc_repack(self,script_path, working_path, repo_name):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            subprocess.check_call(
                ["git", "repack", "-a", "-d", "-f"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,"error", repo_name, {"msg": error_msg})

    def set_remote_url(self,script_path, working_path, repo_name, remote_url, write_json_file):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            subprocess.check_call(
                ["git", "remote", "set-url", "origin", remote_url])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg})
    
    def mk_main_default_branch(self,script_path, working_path, repo_name, write_json_file):
        os.chdir(f"{working_path}/{repo_name}")
        branch = subprocess.Popen(
                "cat HEAD", shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
        if(branch == fr"ref: refs/heads/main"):
            return True
        else:
            if(branch == fr"ref: refs/heads/master"):
                try:
                    subprocess.check_call(
                        ["git", "branch", "-m", "master", "main"])
                    subprocess.check_call(
                        ["cat", "HEAD"])
                except subprocess.CalledProcessError as e:
                    error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output)))
                    self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg})
            else:
               try:
                    subprocess.check_call(
                        ["git", "branch", "-m", "main"])
               except subprocess.CalledProcessError as e:
                    error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output)))
                    self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg}) 


    def push_all(self,script_path, working_path, repo_name, write_json_file, lfs):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            if lfs==True:
                subprocess.check_call(
                ["git", "push", "--all", "origin"])
            else:
                subprocess.check_call(
                ["git", "push", "--all", "origin"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg})
            return False
        else:
            return True

    def clone_bare(self,script_path, working_path, git_server, origin_repo, target_repo, write_json_file):
        os.chdir(f"{working_path}")
        try:
            subprocess.check_call(
                ["git", "clone", "--bare",
                 fr"{git_server}/{origin_repo}",
                 target_repo])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, target_repo, {"msg": error_msg})
            return False
        else:
            return True

    def clone_bare_gh(self, script_path,working_path,  target_repo, write_json_file, gh_token, gh_handle,gh_org):
        os.chdir(f"{working_path}")
        try:
            subprocess.check_call(
                ["git", "clone", "--bare",
                 fr"https://{gh_handle}:{gh_token}@github.com/{gh_org}/{target_repo}.git",
                 fr"{target_repo}_github"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, target_repo, {"msg": error_msg})
            return False
        else:
            return True

    def fetch(self,script_path, working_path, repo_name, write_json_file):
        os.chdir(f"{working_path}/{repo_name}")
        try:
            subprocess.check_call(
                ["git", "fetch"])
        except subprocess.CalledProcessError as e:
            error_msg = str(RuntimeError("command '{}' return with error (code {}): {}".format(
                e.cmd, e.returncode, e.output)))
            self.write_json(script_path,write_json_file, repo_name, {"msg": error_msg})
