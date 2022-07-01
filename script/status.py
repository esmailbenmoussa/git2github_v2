
class StatusManager:
    def list(self, step, repo_name="", repo_size=""):
        status = ""
        if(step == 0):
            status = f"""
                (0/4) {repo_name} - {repo_size}
                _git_clone_pull      => To do
                _create_gh_repo      => To do
                _push_repo_gh        => To do
                """
        if(step == 1):
            status = f"""
                (1/4) {repo_name} - {repo_size}
                _git_clone_pull      => In progress
                _create_gh_repo      => To do
                _push_repo_gh        => To do
                """
        if(step == 2):
            status = f"""
                (2/4) {repo_name} - {repo_size}
                _git_clone_pull      => Done
                _create_gh_repo      => In progress
                _push_repo_gh        => To do
                """
        if(step == 3):
            status = f"""
                (3/4) {repo_name} - {repo_size}
                _git_clone_pull      => Done
                _create_gh_repo      => Done
                _push_repo_gh        => In progress
                """
        if(step == 4):
            status = f"""
                (4/4) {repo_name} - {repo_size}
                _git_clone_pull      => Done
                _create_gh_repo      => Done
                _push_repo_gh        => Done
                """
        print(status)
