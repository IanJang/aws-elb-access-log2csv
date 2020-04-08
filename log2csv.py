import getopt
import sys
import os

from config import FIELD_NAMES
from utils import aws_elb_access_log2csv


def main(argv):
    inputfile = ''
    outputfile = ''
    help_text = f'{argv[0]} -i <input(log)file> -o <output(csv)file>'

    try:
        opts, args = getopt.getopt(argv[1:], "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)

    config = None
    for opt, arg in opts:
        if opt == '-h':
            print(help_text)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if not os.path.isfile(inputfile):
        print("error message :", f"'{inputfile}' file does not exist")
        sys.exit(2)

    field_names = FIELD_NAMES
    try:
        aws_elb_access_log2csv(inputfile, outputfile, field_names=field_names)
    except Exception as e:
        print("command fail")
        print("error message :", e)

    print("COMPLETE")


if __name__ == "__main__":
    main(sys.argv)
