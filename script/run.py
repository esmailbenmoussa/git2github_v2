from stats import Analyzor
from migrator import Migrator
import os
from dotenv import load_dotenv
from reset import Reset

load_dotenv()

gh_handle = os.getenv("GH_HANDLE")  #
gh_token = os.getenv("GH_TOKEN")  #
gh_organization = os.getenv("GH_ORG_NAME")
git_server = os.getenv("GIT_SERVER")
working_path = os.getenv("WORKING_PATH")
script_path = os.getenv("SCRIPT_PATH")
project_path = os.getenv("PROJECT_PATH")
migrator = Migrator(gh_handle, gh_token, gh_organization,
                    git_server, working_path, script_path)
stats = Analyzor(gh_handle, gh_token, gh_organization,
                 git_server, working_path, script_path)
reset = Reset(project_path)

if __name__ == '__main__':
    # Step.0 Reset migration
    # reset.migration()

    # Step.1 Initiate regular git migration / delete repos
    migrator.initializer(lfs=False, delete=False)

    # Step.2 Generate statistics and result reports
    # stats.initializer(lfs=False)

    # Step.3 Initiate LFS git migration, 
    # migrator.initializer(lfs=True)  

    # Step.4 Generate statistics and result reports
    # stats.initializer(lfs=True)

