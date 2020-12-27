import argparse
import core
import sys
import config

arg_parser = None


def generate_argparser():
    ascii_logo = """
    Splunk Enterprise Security - Notables Notifier
    https://github.com/iomoath/ess-notifier
    """

    ap = argparse.ArgumentParser(ascii_logo)

    ap.add_argument("-s","--scan-unassigned", action='store_true',
                    help="Scan for unassigned notables [New state]")

    ap.add_argument("-e", "--process-notification-queue", action='store_true',
                    help="Send pending notifications.")

    ap.add_argument("-v", "--verbose", action='store_true',
                    help="Show more information while processing.")

    ap.add_argument("--version", action="version", version='Splunk Enterprise Security - Notables Notifier Version 1.1')
    return ap


def run(args):
    if args["verbose"]:
        config.VERBOSE_ENABLED = True

    if args['scan_unassigned']:
        core.scan_for_unassigned_notables()
    elif args['process_notification_queue']:
        core.process_notification_queue()
    else:
        arg_parser.print_help()
        sys.exit()



def main():
    global arg_parser
    arg_parser = generate_argparser()
    args = vars(arg_parser.parse_args())
    run(args)



if __name__ == "__main__":
    main()
