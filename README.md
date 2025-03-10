<p align="center">
  <a href="README.ru.md"><img src="https://img.shields.io/badge/Русский-Readme-blue" alt="Russian" /></a>&nbsp;&nbsp;
  <a href="README.md"><img src="https://img.shields.io/badge/English-Readme-blue" alt="English" /></a>&nbsp;&nbsp;
  <img src="https://visitor-badge.laobi.icu/badge?page_id=White-Tiger-PX.auto-moving-files" alt="visitors" />&nbsp;&nbsp;
  <img src="https://img.shields.io/github/stars/White-Tiger-PX/auto-moving-files?style=social" alt="GitHub stars" />
</p>

# auto-moving-files

This script is designed to move or copy files and folders based on specific conditions, such as the last modified time or the first detection time of the file.

## Description

The script performs the following tasks:

- Scans the specified directory and its subdirectories.
- Checks files based on their last modified time and first seen time.
- Copies or moves files that meet the specified conditions.
- Creates logs of the operations, if the corresponding setting is enabled.

## Configuration

The script settings are located in the `config.py` file. Example of the configuration file:

```python
LOG_FOLDER                         = "logs"
DIRECTORY_WITH_SCANNED_DIRECTORIES = "data/scanned_directories"
DIRECTORIES_SETTINGS = [
    {
        "input":  "C:/Users/user/Pictures",
        "output": "D:/Backup/Pictures",
        "time_limit_for_modified_time": 604800,
        "time_limit_for_first_seen":    604800,
        "action_by_last_modified": True,
        "action_by_first_seen":    True,
        "save_folders":            True,
        "copy":                    True,
        "overwrite_files":         False,
        "file_name_exceptions": [

        ],
        "directory_name_exceptions": [

        ],
        "date_grouping_options": {
            "create_date_folders_in_root": False,
            "group_by_days":   False,
            "group_by_months": False,
            "group_by_years":  False
        }
    }
]
```

### Description of Configuration Fields

- **LOG_FOLDER**: The folder for saving logs (used if `LOG_FOLDER` is not 'None').
- **DIRECTORY_WITH_SCANNED_DIRECTORIES**: The folder where data about scanned directories will be stored.
- **DIRECTORIES_SETTINGS**: A list of directories to process. Each directory includes the following parameters:
  - **input**: The path to the source folder to scan.
  - **output**: The path to the folder where files will be moved or copied.
  - **time_limit_for_modified_time**: The time (in seconds) since the last modification after which a file meets the action criteria.
  - **time_limit_for_first_seen**: The time (in seconds) since the file was first seen, after which the file meets the action criteria.
  - **action_by_last_modified**: A boolean value indicating whether the last modified time of the file should be considered.
  - **action_by_first_seen**: A boolean value indicating whether the first seen time of the file should be considered.
  - **save_folders**: A boolean value indicating whether the folder structure should be preserved when copying or moving files.
  - **copy**: A boolean value indicating whether files should be copied (if `True`) or moved (if `False`).
  - **overwrite_files**: A boolean value indicating whether to overwrite existing files in the `output` folder (if `True`).
  - **file_name_exceptions**: A list of file name exceptions, indicating files that should not be moved or copied.
  - **directory_name_exceptions**: A list of directory name exceptions, indicating directories that should not be processed.
  - **date_grouping_options**: Options for grouping files by date. Possible parameters:
    - **create_date_folders_in_root**: A boolean value indicating whether to create date folders in the root of the destination folder.
    - **group_by_days**: A boolean value indicating whether to group files by day.
    - **group_by_months**: A boolean value indicating whether to group files by month.
    - **group_by_years**: A boolean value indicating whether to group files by year.

## Notes

- The script uses Python's standard libraries, so no additional dependencies are required except for the standard library.
- The script may take some time to run for large amounts of data.
- Ensure that the paths in `config.py` are correct for your operating system.

### Automatic Execution

On Windows (using Task Scheduler):

1. Open the **Task Scheduler** by searching for it in the Start menu.
2. Click on **Create task** in the right-hand panel.
3. Give your task a name (e.g., "Telegram Bot Task").
4. Go to the **Triggers** tab, and click **New**.
    - Set the **Begin the task** option to **At logon** to make sure the task starts when you log into your system.
    - Check **Repeat task every** and set it to repeat every X minutes (e.g., every 10 minutes).
5. Go to the **Actions** tab, click **New**, and choose **Start a Program**.
6. Browse and select the Python executable (`python.exe`).
7. In the **Add arguments** field, enter the path to your script (e.g., `C:\programs\auto_delete_files.py`).
8. Click **OK** to save the task.

<div style="justify-content: space-between; align-items: center;">
  <div style="text-align: center;">
    <img src="Task Scheduler - General.png" alt="Task Scheduler - General" width="75%" />
  </div>

  <div style="text-align: center;">
    <img src="Task Scheduler - Triggers.png" alt="Task Scheduler - Triggers" width="75%" />
  </div>

  <div style="text-align: center;">
    <img src="Task Scheduler - Actions.png" alt="Task Scheduler - Actions" width="75%" />
  </div>
</div>
