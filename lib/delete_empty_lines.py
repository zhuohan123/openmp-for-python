import sys

if len(sys.argv)!=2:
    raise ValueError('File name needed!')

file = open(sys.argv[1])
for line in file:
    if len(line.lstrip().rstrip()) != 0:
        if line[-1] == '\n':
            print line,
        else:
            print line

print 'pass'