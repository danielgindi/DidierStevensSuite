#!/usr/bin/env python

__description__ = "Program to convert decimal numbers into hex numbers"
__author__ = 'Didier Stevens'
__version__ = '0.0.1'
__date__ = '2016/01/06'

"""

Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

History:
  2015/12/18: start
  2016/01/06: wrote man; added option -i

Todo:
"""

import optparse
import glob
import collections
import re
import sys
import textwrap

def PrintManual():
    manual = '''
Manual:

This program reads lines from the given file(s) or standard input, and then extracts decimal numbers from each line. A decimal number is a sequence of digits. All numbers found in a line are converted to hexadecimal and outputed as a line. Hexadecimal numbers are separated by a space character. If a number is larger than 255/0xFF, an error is generated, except when option -i is used.

The hexadecimal numbers are written to standard output, except when option -o is used. When option -o is used, the numbers are written to the file specified by option -o.
'''
    for line in manual.split('\n'):
        print(textwrap.fill(line))

def File2Strings(filename):
    try:
        f = open(filename, 'r')
    except:
        return None
    try:
        return map(lambda line:line.rstrip('\n'), f.readlines())
    except:
        return None
    finally:
        f.close()

def ProcessAt(argument):
    if argument.startswith('@'):
        strings = File2Strings(argument[1:])
        if strings == None:
            raise Exception('Error reading %s' % argument)
        else:
            return strings
    else:
        return [argument]

# CIC: Call If Callable
def CIC(expression):
    if callable(expression):
        return expression()
    else:
        return expression

# IFF: IF Function
def IFF(expression, valueTrue, valueFalse):
    if expression:
        return CIC(valueTrue)
    else:
        return CIC(valueFalse)

class cOutput():
    def __init__(self, filename=None):
        self.filename = filename
        if self.filename and self.filename != '':
            self.f = open(self.filename, 'w')
        else:
            self.f = None

    def Line(self, line):
        if self.f:
            self.f.write(line + '\n')
        else:
            print(line)
#            sys.stdout.flush()

    def Close(self):
        if self.f:
            self.f.close()
            self.f = None

def ExpandFilenameArguments(filenames):
    return list(collections.OrderedDict.fromkeys(sum(map(glob.glob, sum(map(ProcessAt, filenames), [])), [])))

class cOutputResult():
    def __init__(self, options):
        if options.output:
            self.oOutput = cOutput(options.output)
        else:
            self.oOutput = cOutput()
        self.options = options

    def Line(self, line):
        self.oOutput.Line(line)

    def Close(self):
        self.oOutput.Close()

def ProcessFile(fIn, fullread):
    if fullread:
        yield fIn.read()
    else:
        for line in fIn:
            yield line.strip('\n')

def NumbersToHexSingle(filenames, oOutput, options):
    oRE = re.compile('\d+')
    numberTooLarge = False
    for filename in filenames:
        if filename == '':
            fIn = sys.stdin
        else:
            fIn = open(filename, 'r')
        for line in ProcessFile(fIn, False):
            numbers = [int(number) for number in oRE.findall(line)]
            numberTooLarge = max(numbers) > 255 and not options.ignore
            if numberTooLarge:
                print('Error: found number larger than 255: %d' % max(numbers))
                break
            oOutput.Line(' '.join(['%02x' % int(number) for number in oRE.findall(line)]))
        if fIn != sys.stdin:
            fIn.close()
        if numberTooLarge:
            break

def NumbersToHex(filenames, options):
    oOutput = cOutputResult(options)
    NumbersToHexSingle(filenames, oOutput, options)
    oOutput.Close()

def Main():
    moredesc = '''

Arguments:
@file: process each file listed in the text file specified
wildcards are supported

Source code put in the public domain by Didier Stevens, no Copyright
Use at your own risk
https://DidierStevens.com'''

    oParser = optparse.OptionParser(usage='usage: %prog [options] [[@]file ...]\n' + __description__ + moredesc, version='%prog ' + __version__)
    oParser.add_option('-m', '--man', action='store_true', default=False, help='Print manual')
    oParser.add_option('-o', '--output', type=str, default='', help='Output to file')
    oParser.add_option('-i', '--ignore', action='store_true', default=False, help='Do not generate an error when a number larger than 255 is found')
    (options, args) = oParser.parse_args()

    if options.man:
        oParser.print_help()
        PrintManual()
        return

    if len(args) == 0:
        NumbersToHex([''], options)
    else:
        NumbersToHex(ExpandFilenameArguments(args[1:]), options)

if __name__ == '__main__':
    Main()
