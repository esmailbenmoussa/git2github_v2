import os
import subprocess

class Reset:
    def __init__(self, project_path):
        self.project_path = project_path

    def folder_reset(self, folder_name, folder_path):
        os.chdir(f"{folder_path}")
        if(os.path.isdir(folder_path)):
            print(fr"Resetting {folder_name} folder")
            subprocess.check_call(["rm","-r","-f",folder_name])
            subprocess.check_call(["mkdir",folder_name])
            print(fr"{folder_name} folder reseted")
        else: 
            print(folder_name, "doesnt exist")
    
    def migration(self):
        project_path = self.project_path
        reset_scope = [
        {"folder_name":"repos", "path": fr"{project_path}"},
        {"folder_name":"error", "path" : fr"{project_path}/script"},
        {"folder_name":"error_lfs", "path" : fr"{project_path}/script"},
        {"folder_name":"result", "path"  : fr"{project_path}/script"},
        {"folder_name":"status", "path"  : fr"{project_path}/script"},
        {"folder_name":"status_lfs" , "path" : fr"{project_path}/script"},
        ]
        
        for obj in reset_scope:
            folder_name = obj["folder_name"]
            path = obj["path"]
            self.folder_reset(folder_name, path)