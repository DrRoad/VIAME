#!/usr/bin/python

import os
import sys
import re
import matplotlib.pyplot as plt
import numpy as np
import argparse
import atexit
import tempfile
import subprocess
import shutil

temp_dir = tempfile.mkdtemp(prefix='score-tmp')
atexit.register(lambda: shutil.rmtree(temp_dir))

linestyles = ['-', '--', '-.', ':']
linecolors = ['#25233d', '#161891', '#316f6a', '#662e43']

def get_stat_cmd():
  if os.name == 'nt':
    return ['score_tracks.exe','--hadwav']
  else:
    return ['score_tracks','--hadwav']

def get_roc_cmd():
  if os.name == 'nt':
    return ['score_events.exe']
  else:
    return ['score_events']

def load_roc( fn ):

  x_fa = np.array( [] )
  y_pd = np.array( [] )

  with open(fn) as f:
    while (1):
      raw_line = f.readline()
      if not raw_line:
        break
      fields = raw_line.split()
      x_fa = np.append( x_fa, float( fields[47] ) )
      y_pd = np.append( y_pd, float( fields[7] ) )

  return ( x_fa, y_pd )

def list_categories( filename ):

  unique_ids = set()

  with open( filename ) as f:
    for line in f:
      lis = line.strip().split(',')
      if len( lis ) < 10:
        continue
      if len( lis[0] ) > 0 and lis[0][0] == '#':
        continue
      idx = 9
      while idx < len( lis ):
        unique_ids.add( lis[idx] )
        idx = idx + 2

  return list( unique_ids )

def filter_by_category( filename, category, threshold=0.0 ):

  (fd, handle) = tempfile.mkstemp( prefix='viame-score-',
                                   suffix='.csv',
                                   text=True,
                                   dir=temp_dir )

  fout = os.fdopen( fd, 'w' )

  with open( filename ) as f:
    for line in f:
      lis = line.strip().split(',')
      if len( lis ) < 10:
        continue
      if len( lis[0] ) > 0 and lis[0][0] == '#':
        continue
      idx = 9
      use_detection = False
      confidence = 0.0
      object_label = ""
      while idx < len( lis ):
        if lis[idx] == category and \
           ( args.threshold == 0.0 or float( lis[idx+1] ) >= float( args.threshold ) ):
          use_detection = True
          confidence = float( lis[idx+1] )
          object_label = lis[idx]
          break
        idx = idx + 2

      if use_detection:
        fout.write( lis[0] + ',' + lis[1] + ',' + lis[2] + ',' + lis[3] + ',' )
        fout.write( lis[4] + ',' + lis[5] + ',' + lis[6] + ',' + str( confidence ) + ',' )
        if len( object_label ) > 0:
          fout.write( lis[8] + ',' + object_label + ',' + str( confidence ) + '\n' )
        else:
          fout.write( lis[8] + '\n' )

  fout.close()

  return fd, handle

def generate_stats( args, categories ):

  # Generate roc files
  base, ext = os.path.splitext( args.stats )

  base_cmd = get_stat_cmd()
  base_cmd += [ '--computed-format', args.input_format, '--truth-format', args.input_format ]
  base_cmd += [ '--fn2ts' ]

  for cat in categories:
    stat_file = base + "." + cat + ext
    _, filtered_computed = filter_by_category( args.computed, cat, args.threshold )
    _, filtered_truth = filter_by_category( args.truth, cat, args.threshold )
    cmd = base_cmd + [ '--computed-tracks', filtered_computed, '--truth-tracks', filtered_truth ]
    with open( stat_file, 'w' ) as fout:
      subprocess.call( cmd, stdout=fout, stderr=fout )

  if len( categories ) != 1:
    cmd = base_cmd + [ '--computed-tracks', args.computed, '--truth-tracks', args.truth ]
    with open( args.stats, 'w' ) as fout:
      subprocess.call( cmd, stdout=fout, stderr=fout )

def generate_rocs( args, categories ):

  # Generate roc files
  base, ext = os.path.splitext( args.roc )

  roc_files = []

  base_cmd = get_roc_cmd()
  base_cmd += [ '--computed-format', args.input_format, '--truth-format', args.input_format ]
  base_cmd += [ '--fn2ts', '--gt-prefiltered', '--ct-prefiltered' ]

  if ',' in args.computed:
    input_files = [ i.lstrip() for i in args.computed.split(',') ]
  else:
    input_files = args.computed

  for filename in input_files:
    for cat in categories:
      roc_file = base + "." + cat + ".txt"
      if len( input_files ) > 1:
        roc_file = filename + '.' + roc_file
      print( roc_file )
      sys.exit(0)
      _, filtered_computed = filter_by_category( filename, cat )
      _, filtered_truth = filter_by_category( args.truth, cat )
      cmd = base_cmd + [ '--roc-dump', roc_file ]
      cmd += [ '--computed-tracks', filtered_computed, '--truth-tracks', filtered_truth ]
      subprocess.call( cmd )
      roc_files.append( roc_file )

    if len( categories ) != 1:
      net_roc_file = base + ".txt"
      if len( input_files ) > 1:
        net_roc_file = filename + '.' + net_roc_file
      cmd = base_cmd + [ '--roc-dump', net_roc_file ]
      cmd += [ '--computed-tracks', filename, '--truth-tracks', args.truth ]
      subprocess.call( cmd )
      roc_files.append( net_roc_file )

  # Generate plot
  fig = plt.figure()

  xscale_arg = 'log' if args.logx else 'linear'

  rocplot = plt.subplot( 1, 1, 1, xscale=xscale_arg )
  rocplot.set_title( args.title ) if args.title else None

  plt.xlabel( args.xlabel )
  plt.ylabel( args.ylabel )

  plt.xticks()
  plt.yticks()

  user_titles = args.key.split(',') if args.key else None
  i = 0
  for i, fn in enumerate( roc_files ):
    (x,y) = load_roc( fn )
    display_label = ""
    if user_titles and i < len( user_titles ):
      display_label = user_titles[i]
    else:
      display_label = fn.replace( ".txt", "" )
      display_label = display_label.replace( ".csv", "" )
      display_label = display_label.replace( base + ".", "" )
      display_label = display_label.replace( base, "" )
      if len( display_label ) == 0:
        display_label = "aggregate"
      if display_label.endswith("."):
        display_label = display_label[:-1]
    sys.stderr.write("Info: %d: loading %s as '%s'...\n" % (i, fn, display_label) )
    stl = linestyles[ i % len(linestyles) ]
    if i < len(linecolors):
      cl = linecolors[ i ]
    else:
      cl = np.random.rand(3)
    if len( display_label ) > 0:
      rocplot.plot( x, y, linestyle=stl, color=cl, linewidth=args.lw, label=display_label )
    else:
      rocplot.plot( x, y, linestyle=stl, color=cl, linewidth=args.lw )
    rocplot.set_xlim(xmin=0)
    i += 1

  if args.autoscale:
    rocplot.autoscale()
  else:
    tmp = args.rangey.split(':')
    if len(tmp) != 2:
      sys.stderr.write('Error: rangey option must be two floats ')
      sys.stderr.write('separated by a colon, e.g. 0.2:0.7\n')
      sys.exit(1)
    (ymin, ymax) = (float(tmp[0]), float(tmp[1]))
    rocplot.set_ylim(ymin,ymax)

    if args.rangex:
      tmp = args.rangex.split(':')
      if len(tmp) != 2:
        sys.stderr.write('Error: rangex option must be two floats ')
        sys.stderr.write('separated by a colon, e.g. 0.2:0.7\n')
        sys.exit(1)
      (xmin, xmax) = (float(tmp[0]), float(tmp[1]))
      rocplot.set_xlim(xmin,xmax)

  if not args.nokey:
    plt.legend( loc=args.keyloc )

  plt.savefig( args.roc )


if __name__ == "__main__":
  parser = argparse.ArgumentParser( description = 'Generate detection scores and ROCs' )

  # Inputs
  parser.add_argument( '-computed', default=None,
             help='Input filename for computed file.' )
  parser.add_argument( '-truth', default=None,
             help='Input filename for groundtruth file.' )
  parser.add_argument( '-threshold', type=float, default=0.05,
             help='Input threshold for statistics.' )
  parser.add_argument( '-input-format', dest="input_format", default="noaa-csv",
             help='Input file format.' )

  # Outputs
  parser.add_argument( '-stats', default=None,
             help='Filename for output track statistics.' )
  parser.add_argument( '-roc', default=None,
             help='Filename for output roc curves.' )
  parser.add_argument("--per-category", dest="per_category", action="store_true",
             help="Utilize categories in the files and generate plots per category")

  # Plot settings
  parser.add_argument( '-rangey', metavar='rangey', nargs='?', default='0:1',
             help='ymin:ymax (quote w/ spc for negative, i.e. " -0.1:5")' )
  parser.add_argument( '-rangex', metavar='rangex', nargs='?',
             help='xmin:xmax (quote w/ spc for negative, i.e. " -0.1:5")' )
  parser.add_argument( '-autoscale', action='store_true',
             help='Ignore -rangex -rangey and autoscale both axes of the plot.' )
  parser.add_argument( '-logx', action='store_true',
             help='Use logscale for x' )
  parser.add_argument( '-xlabel', nargs='?', default='Detection FA count',
             help='title for x axis' )
  parser.add_argument( '-ylabel', nargs='?', default='Detection PD',
             help='title for y axis' )
  parser.add_argument( '-title', nargs='?',
             help='title for plot' )
  parser.add_argument( '-lw', nargs='?', type=float, default=2,
             help='line width' )
  parser.add_argument( '-key', nargs='?', default=None,
             help='comma-separated set of strings labeling each line in order read' )
  parser.add_argument( '-keyloc', nargs='?', default='best',
             help='Key location ("upper left", "lower right", etc; help for list)' )
  parser.add_argument( '-nokey', action='store_true',
             help='Set to suppress plot legend' )

  args = parser.parse_args()

  if not args.computed or not args.truth:
    print( "Error: both computed and truth file must be specified" )
    sys.exit( 0 )

  if not args.roc and not args.stats:
    print( "Error: either 'stats' or 'roc' output files must be specified" )
    sys.exit( 0 )

  categories = []

  if args.per_category:
    if args.input_format != "noaa-csv":
      print( "Error: only noaa-csv currently supported for multi-category" )
      sys.exit( 0 )
    categories = list_categories( args.truth )

  if args.stats:
    generate_stats( args, categories )

  if args.roc:
    generate_rocs( args, categories )
