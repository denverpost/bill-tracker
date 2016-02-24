#!/usr/bin/env python
# Turn a multi-column CSV into a json object.
import os, sys, csv, json
import argparse
import doctest
import string

def escape(escapee):
    """ Return a js-safe string.
        >>> print escape('Escape "THIS"')
        Escape \\"THIS\\"
        """
    return string.replace(escapee, '"', '\\"')

def main(args):
    """ Loop through each filename, read the CSV and return a js object.
        >>> args = build_parser(['--verbose', 'csv/test.csv'])
        >>> print args.files[0]
        ['csv/test.csv']
        >>> main(args)
        Namespace(files=[['csv/test.csv']], verbose=True)
        matcher.lookup = {"Peyton Manning": "http://www.denverpost.com/peyton-manning"};
        """
    if args.verbose:
        print args
    for item in args.files[0]:
        c = {}
        f = open('%s' % item, 'rt')
        reader = csv.reader(f)

        for row in reader:
            if reader.line_num == 1:
                keys = row
                continue
            the_row = dict(zip(keys, row))

            # Trim fields we know need trimming
            the_row['name_first'] = the_row['name_first'].strip()
            the_row['name_last'] = the_row['name_last'].strip()

            # Separate committees into concomant parts
            committees_list = []
            comm = [the_row['committees']]
            if ';' in the_row['committees']:
                comm = the_row['committees'].split(';')
            for item in comm:
                comm_dict = {}
                if 'of' in item:
                    parts = item.split(' of ', 1)
                    comm_dict['role'] = parts[0].strip()
                    comm_dict['committee'] = parts[1].strip()
                else:
                    comm_dict['role'] = item.strip()

                committees_list.append(comm_dict)
            the_row['committees'] = committees_list

            # Separate the counties into its parts
            counties_list = []
            if ',' in the_row['counties']:
                for item in the_row['counties'].split(','):
                    counties_list.append(item.strip())
                the_row['counties'] = counties_list
                    

            c[the_row['name_last']] = the_row

        print json.dumps(c, sort_keys=True, indent=4)


def build_parser(args):
    """ A method to make arg parsing testable.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        >>> print args.files[0]
        []
        """
    parser = argparse.ArgumentParser(usage='', description='Handle the options.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("files", action="append", nargs="*")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
