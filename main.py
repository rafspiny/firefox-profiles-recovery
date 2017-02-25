import argparse
import logic.profile_crawler, logic.profile_generator
from os.path import expanduser


def main():
    parser = argparse.ArgumentParser(description='Recovery utility for Firefox profiles', add_help=True,
                                     epilog='so long and thanks for all the fish')
    parser.add_argument('--list', '-l', type=bool, default=False, required=False, help='The command to list available profiles to recover', dest='list_cmd')
    parser.add_argument('--recover-all', '-a', type=bool, required=False, default=False, dest='recover_all_cmd', help='Recover all the available profiles')
    parser.add_argument('--recover', '-r', type=str, nargs='+', required=False, default=None, dest='recover_cmd', help='Recover specific profiles')
    parser.add_argument('--ini', '-i', type=str, nargs='+', required=False, default=None, dest='ini_path', help='Path of the profile.ini file')
    parser.add_argument('--profile-dir', '-p', type=str, nargs='+', required=False, default=None, dest='profile_dir', help='Path of the profiles directory')

    args = parser.parse_args()
    if args.list_cmd is False and args.recover_all_cmd is False and args.recover_cmd is None:
        parser.print_help()
        exit(-1)

    # Handle ini_path and profile_dir
    if args.ini_path is None:
        # Default to...
        args.ini_path = '%s/.mozilla/firefox/profiles.ini' % expanduser('~')
    if args.profile_dir is None:
        # Default to...
        args.profile_dir = '%s/.mozilla/firefox/' % expanduser('~')

    crawler = logic.profile_crawler.ProfileSearcher(ini_path=args.ini_path, profile_dir=args.profile_dir)
    crawler.compute_recoverable()
    # handle command
    if args.list_cmd is True:
        # list profiles
        for recoverable_profile in crawler.recoverable_profiles:
            print("Profile path %s" % recoverable_profile.name)

    generator = logic.profile_generator.ProfileGenerator(ini_path=args.ini_path,
                                                         profiles=[p for p in crawler.present_in_profile_file.values()])

    if args.recover_all_cmd is True:
        for recoverable_profile in crawler.recoverable_profiles:
            print("Recovering profile named %s" % recoverable_profile.name)
            generator.add_profile(recoverable_profile)

    if args.recover_cmd is not None:
        for requested_profile_name in args.recover_cmd:
            found_recoverable_profiles = [current_profile for current_profile in crawler.recoverable_profiles if current_profile.name == requested_profile_name]
            if len(found_recoverable_profiles) == 1:
                print("Recovering specific profile named %s" % found_recoverable_profiles[0].name)
                generator.add_profile(found_recoverable_profiles[0])
            if len(found_recoverable_profiles) == 0:
                print("Profile named %s not found" % requested_profile_name)
            if len(found_recoverable_profiles) > 1:
                print("Multiple profiles with name %s found. Can't proceed." % requested_profile_name)


if __name__ == '__main__':
    main()