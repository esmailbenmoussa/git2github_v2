# Git server to GitHub migration

## Table of contents

1. [Introduction](#1)
2. [Pre-requisites and configuration](#2)
   1. [Software dependencies](#21)
   2. [Configuration](#22)
      1. [Folder structure](#221)
      2. [Personal Access Token](#222)
      3. [.env file](#223)
      4. [git_repo_list.json file](#224)
3. [Migration](#3)
   1. [Flags](#31)
   2. [Commands](#32)
   3. [Stages](#33)
      1. [Stage 0](#331)
      2. [Stage 1](#332)
      3. [Stage 2](#333)
      4. [Stage 3](#334)
      5. [Stage 4](#335)
4. [Progress report](#4)
5. [Migration reports](#5)
6. [Use cases end-to-end migration](#6)
   1. [Pre migration](#61)
   2. [Migration](#62)
   3. [Post Migration Successful](#63)
   4. [Post Migration Failed](#64)
   5. [Git-LFS Migration](#65)
   6. [Post Git-LFS Migration](#66)

## 1. Introduction <a id="1"></a>

This project contains a script for migrating git repositories from git-server to GitHub. It supports both normal and large sized repos, with branch and tag counter.

## 2. Pre-requisites and configuration <a id="2"></a>

### 2.1. Software dependencies <a id="21"></a>

- Python version 3.10
- Git-lfs version 2.13.2

### 2.2. Configuration <a id="22"></a>

#### 2.2.1. Folder structure <a id="221"></a>

```
/home/roamware/YourDir
└───repos
│   │   repo_example_A
│   │   repo_example_B
│
└───script
│   │   .env
│   │   .gitignore
│   │   git_commands.py
│   │   git_repo_list_lfs.json
│   │   git_repo_list.json
│   │   migrator.py
│   │   README.md
│   │   run.py
│   │   stats.py
│   │   status.-py
│   │
│   └───result
│   │   │   result_migrated.json
│   │   │   result_failed.json
│   │   │   ...
│   │
│   └───error
│   │   │   repo_example_A.json
│   │   │   ...
│   │
│   └───error_lfs
│   │   │   repo_example_A.json
│   │   │   ...
│   │
│   └───status
│   │   │   repo_example_A.json
│   │   │   ...
│   │
│   └───status_lfs
│   │   │   repo_example_A.json
│   │   │   ...
│   │
```

#### 2.2.2. Personal Access Token <a id="222"></a>

All interfacing with GitHub requires a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
granting read+write access to repositories, and which we refer to as `pat` below.

#### 2.2.3. .env file <a id="223"></a>

Create an .env file in the root with following attributes, and populate them with your details:

```.env
GH_HANDLE=YourGithubHandle
GH_TOKEN=ghp_YourPAT
GH_ORG_NAME=GithubOrganizationsName
GIT_SERVER=GitServerName
WORKING_PATH=/home/roamware/Replace/repos
SCRIPT_PATH=/home/roamware/Replace/script
```

WORKING_PATH is where the repositories will be cloned to.

SCRIPT_PATH is where the actual migration script will be stored.

#### 2.2.4. git_repo_list.json file <a id="224"></a>

Populate this JSON-file with git repositories that are in scope for the migration.

Example:

```
[
	{

	"Origin-repo":  "tools.git",

	"Target-repo":  "RNS-tools"

	},
	{

	"Origin-repo":  "actionsystem.git",

	"Target-repo":  "RNS-actionsystem"

	},
]
```

## 3. Migration <a id="3"></a>

Multiprocessing package is used to fully leverage multiple processors on a given machine. Allowing the script to run multiple migrations simultaneously.

The migration is triggered from run.py, with four different commands and flags.

### 3.1. Flags <a id="31"></a>

LFS: Set flag True to initiate a git-lfs migration.
Delete: Set flag True to delete repositories from the git_repo_list.json file on GitHub.

### 3.2. Commands <a id="32"></a>

```
# Step.1 Initiate git migration / git-lfs migration / delete repos
migrator.initializer(lfs=False,  delete=False)


# Step.2 Generate reports on the git migration
# stats.initializer(lfs=False)


# Step.3 Initiate git-lfs migration,
# migrator.initializer(lfs=True)


# Step.4 Generate reports on the git-lfs migration
# stats.initializer(lfs=True)
```

The actual migration script works through five stages before completion. Each stage reports a progress report in the command line interface

### 3.3. Stages <a id="33"></a>

##### 3.3.1. Stage 0 <a id="331"></a>

- Migration initiated
- Cloning repository from git-server

##### 3.3.2. Stage 1 <a id="332"></a>

- New repository on GitHub

##### 3.3.3. Stage 2 <a id="333"></a>

- Uploading repository to GitHub

##### 3.3.4. Stage 3 <a id="334"></a>

- Cloning repository from GitHub
- Checking branches and tags

##### 3.3.5. Stage 4 <a id="335"></a>

- Migration completed

## 4. Progress report <a id="4"></a>

Progression status will be displayed in the terminal for each major migration step.

Example:

```
               (x/4) repo_example_A,
                _git_clone_pull      => Done
                _create_gh_repo      => In progress
                _push_repo_gh        => In progress
```

## 5. Migration reports <a id="5"></a>

Reports are produced with following commands:

```

# Step.2 Generate reports on the git migration
# stats.initializer(lfs=False)


# Step.4 Generate reports on the git-lfs migration
# stats.initializer(lfs=True)
```

And stored in the results folder within result_failed.json or result_migrated.

Example result_migrated.json:

```
{
	{
  "RNS-aiwb": {
    "branches_source": 2,
    "branches_github": 2,
    "tags_source": 1,
    "tags_github": 1,
    "size_source": "3.0M",
    "size_github": "3.0M"
  },
  "RNS-tools": {
    "branches_source": 58,
    "branches_github": 58,
    "tags_source": 3088,
    "tags_github": 3088,
    "size_source": "624K",
    "size_github": "620K"
  },
}
```

Example result_failed.json:

```
{
  "RNS-roaminganalytics": { "level": 2 },
  "RNS-rcem": { "level": 2 },
}
```

Level indicates at what stage the migration failed at.
For more details, navigate to error folder, identify repo file and read the error message.

## 6. Use case: End-to-end migration <a id="6"></a>

**Goal**: Migrate http://gitserver.mobileum.com/web/tools.git to GitHub

6.1 **Pre migration** <a id="61"></a>

1. End-user configurates .env file.
2. Script is configured with pat, urls, path.
3. End-user resets the migration.
4. Script folders (error, error_lfs, status, status_lfs, nd result) are empty.
5. End-user adds object to `git_repo_list.json`.

```
  {
    "Origin-repo": "tools.git",
    "Target-repo": "RNS-tools"
  },
```

6. Script is prepared to run git migration.

6.2 **Migration** <a id="62"></a>

1. End-user triggers git migration in `run.py`.

```
migrator.initializer(lfs=False, delete=False)
```

2. Script migrates objects in `git_repo_list.json`.

6.3 **Post Migration Successful** <a id="63"></a>

1. End-user triggers report generator.

```
stats.initializer(lfs=False)
```

2. Script generates `result_failed.json` and `result_migrated.json` in result folder.

```
{
   "RNS-tools": {
    "branches_source": 58,
    "branches_github": 58,
    "tags_source": 3088,
    "tags_github": 3088,
    "size_source": "624K",
    "size_github": "620K"
  },
}
```

6.4 **Post Migration Failed** <a id="64"></a>

1. End-user triggers report generator.

```
stats.initializer(lfs=False)
```

2. Script generates `result_failed.json` and `result_migrated.json` in result folder.

```
{
 "RNS-tools": { "level": 2 }
}
```

3. End-user identifies repo in error folder and analyzes error message.
   If level is 2, the migration most likly failed due to a object being to large within that repository.

6.5 **Git-LFS Migration** <a id="65"></a>
This use case continues from 6.4 with assumption of repo level is stuck on 2:

1. End-user triggers git-lfs migration in `run.py`.

```
migrator.initializer(lfs=True)
```

2. Script migrates objects in `git_repo_list_lfs.json`.

6.6 **Post Git-LFS Migration** <a id="66"></a>

1. End-user triggers report generator.

```
stats.initializer(lfs=True)
```

2. Script generates `result_failed_lfs.json` and `result_migrated_lfs.json` in result folder.

```
{
   "RNS-tools": {
    "branches_source": 58,
    "branches_github": 58,
    "tags_source": 3088,
    "tags_github": 3088,
    "size_source": "624K",
    "size_github": "620K"
  },
}
```
