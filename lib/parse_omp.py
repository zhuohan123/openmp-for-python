import sys

def parse_args(line):
    args = []
    line = line.lstrip()
    split_line = line.split()
    if (len(split_line)>0 and split_line[0] == '#omp') \
            or (len(split_line)>1 and split_line[0] == '#' and split_line[1] == 'omp'):
        args.append('#omp')
        spos = line.find('omp')
        line = line[spos+3:]
        pcnt = 0
        tstr = ''
        for ch in line:
            if ch == ' ' or ch == '\t' or ch =='\n' or ch == '\r':
                if pcnt == 0:
                    if tstr != '':
                        args.append(tstr)
                    tstr = ''
            else:
                if ch=='(':
                    pcnt+=1
                elif ch==')':
                    pcnt-=1
                tstr += ch
        if tstr != '':
            args.append(tstr)
    else:
        args.append('not omp')
    return args

if len(sys.argv)!=2:
    raise ValueError('File name needed!')

file = open(sys.argv[1])

lineno = 0
for line in file:
    lineno += 1
    args = parse_args(line)
    #print args
    n_of_args = len(args)
    if n_of_args > 0 and args[0] == '#omp':
        if n_of_args > 1:
            if args[1] == 'parallel':
                print 'parallel', lineno,
                if n_of_args > 2 and args[2] == 'end':
                    print 'end',
                    begin = False
                else:
                    print 'begin',
                    begin = True
                print

                if begin:
                    num_threads = 0
                    private_vars = []
                    for arg in args:
                        if arg.startswith('num_threads('):
                            start = arg.find('(')+1
                            end = arg.find(')')
                            num_threads = int(arg[start:end])
                        if arg.startswith('private('):
                            start = arg.find('(')+1
                            end = arg.find(')')
                            vars = arg[start:end].split(',')
                            vars = [var.strip() for var in vars]
                            private_vars += vars
                    print 'num_threads', num_threads
                    for var in private_vars:
                        print 'private_var', var
            elif args[1] == 'for':
                print 'for', lineno
                scheduling_type = 'static'
                nowait = False
                for arg in args:
                    if arg.startswith('reduction('):
                        start = arg.find('(') + 1
                        end = arg.find(')')
                        op, vars = arg[start:end].split(':')
                        op = op.strip()
                        vars = vars.split(',')
                        vars = [var.strip() for var in vars]
                        for var in vars:
                            print 'reduction', op, var
                    if arg.startswith('schedule('):
                        start = arg.find('(') + 1
                        end = arg.find(')')
                        scheduling_type = arg[start:end].strip()
                    if arg == 'nowait':
                        nowait = True
                print 'nowait', nowait
                print 'scheduling_type', scheduling_type
            elif args[1] == 'critical':
                print 'critical', lineno,
                if n_of_args > 2 and args[2] == 'end':
                    print 'end',
                else:
                    print 'begin',
                print
            elif args[1] == 'barrier':
                print 'barrier', lineno
            elif args[1] == 'sections':
                print 'sections', lineno,
                if n_of_args > 2 and args[2] == 'end':
                    print 'end',
                else:
                    print 'begin',
                print
            elif args[1] == 'section':
                print 'section', lineno,
                if n_of_args > 2 and args[2] == 'end':
                    print 'end',
                else:
                    print 'begin',
                print


        else:
            print 'warning: no arguments after "#omp"'