#!/usr/bin/env python

import sys
import os
import shutil
import argparse
import glob

# Main Function
if __name__ == "__main__" :

    parser = argparse.ArgumentParser(description="Perform a filtering action on a csv",
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", dest="input_file", default="",
                      help="Input file or glob pattern to process")

    parser.add_argument("--consolidate-ids", dest="consolidate_ids", action="store_true",
                      help="Use a ball tree for the searchable index")

    parser.add_argument("--decrease-fid", dest="decrease_fid", action="store_true",
                      help="Use a ball tree for the searchable index")

    parser.add_argument("--assign-uid", dest="assign_uid", action="store_true",
                      help="Assign unique detection ids to all entries in volume")

    parser.add_argument("--filter-single", dest="filter_single", action="store_true",
                      help="Filter single state tracks")

    args = parser.parse_args()

    input_files = []

    if len( args.input_file ) == 0:
        print( "No valid input files provided, exiting." )
        sys.exit(0)

    if '*' in args.input_file:
        input_files = glob.glob( args.input_file )
    else:
        input_files.append( args.input_file )

    id_counter = 1

    for input_file in input_files:

        print( "Processing " + input_file )

        fin = open( input_file, "r" )
        output = []

        id_mappings = dict()
        id_states = dict()
        has_non_single = False

        for line in fin:
            if len( line ) > 0 and line[0] == '#' or line[0:9] == 'target_id':
                continue
            parsed_line = line.rstrip().split(',')
            if len( parsed_line ) < 2:
                continue
            if args.consolidate_ids:
                parsed_line[0] = str( 100 * int( int( parsed_line[0] ) / 100 ) )
            if args.decrease_fid:
                parsed_line[2] = str( int( parsed_line[2] ) - 1 )
            if args.assign_uid:
                if parsed_line[0] in id_mappings:
                    parsed_line[0] = id_mappings[ parsed_line[0] ]
                    has_non_single = True
                else:
                    id_mappings[parsed_line[0]] = str(id_counter)
                    parsed_line[0] = str(id_counter)
                    id_counter = id_counter + 1
            if args.filter_single:
                if parsed_line[0] not in id_states:
                    id_states[ parsed_line[0] ] = 1
                else:
                    id_states[ parsed_line[0] ] = id_states[ parsed_line[0] ] + 1
                    has_non_single = True
            output.append( ','.join( parsed_line ) + '\n' )
        fin.close()

        if ( args.assign_uid or args.filter_single ) and not has_non_single:
            print( "Sequence " + input_file + " has all single states" )

        if args.filter_single:
            output = [ e for e in output if id_states[ e.split(',')[ 0 ] ] > 1 ]

        fout = open( input_file, "w" )
        for line in output:
            fout.write( line )
        fout.close()
  
