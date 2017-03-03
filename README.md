# firefox-profiles-recovery
A script to easily recover Firefox profiles after a system problem.

Simple output when runnig the code:
```
$ python main.py
usage: main.py [-h] [--list LIST_CMD] [--recover-all RECOVER_ALL_CMD]
               [--recover RECOVER_CMD [RECOVER_CMD ...]]
               [--ini INI_PATH [INI_PATH ...]]
               [--profile-dir PROFILE_DIR [PROFILE_DIR ...]]

Recovery utility for Firefox profiles

optional arguments:
  -h, --help            show this help message and exit
  --list LIST_CMD, -l LIST_CMD
                        The command to list available profiles to recover
  --recover-all RECOVER_ALL_CMD, -a RECOVER_ALL_CMD
                        Recover all the available profiles
  --recover RECOVER_CMD [RECOVER_CMD ...], -r RECOVER_CMD [RECOVER_CMD ...]
                        Recover specific profiles
  --ini INI_PATH [INI_PATH ...], -i INI_PATH [INI_PATH ...]
                        Path of the profile.ini file
  --profile-dir PROFILE_DIR [PROFILE_DIR ...], -p PROFILE_DIR [PROFILE_DIR ...]
                        Path of the profiles directory

so long and thanks for all the fish
```