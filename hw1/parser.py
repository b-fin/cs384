#
# CSCI 384 : parser.py
#
# simple recursive-descent parser for arithmetic expressions
#
# The recursive descent parser for
#
# <expn> ::= <expn> + <expn> | <expn> + <expn> | x | 5 | ( <expn> )
#
# using the (new (ex2)) disambiguated grammar
#
#<expn> ::= let val <name> = <expn> in <expn> end
#<expn> ::= if <expn> then <expn> else <expn>
#<expn> ::= <disj>
#<disj> ::= <disj> orelse <conj> | <conj>
#<conj> ::= <conj> andalso <cmpn> | <cmpn>
#<cmpn> ::= <addn> = <addn> | <addn> < <addn> | <addn>
#<addn> ::= <addn> + <mult> | <mult>
# <mult> ::=  <mult> * <powr> | <mult> div <powr> | <mult> mod <powr> | <powr>
#<powr> ::= <nega> ** <powr> | <nega>
#<nega> ::= not <atom> | <atom>
#<atom> ::= x | 5 | true | false | ( <expn> )
#
# ------------------------------------------------------------
#
# Author: Brandon Finley
# Login: finleyb
# GitHub: b-fin
#
# A comment on your completed work should go here. What's working?
# What isn't? What other files were included in this submission and
# what are they?
#
# For exercise 1, my first attempt involved simply extending the logic in the
# parseX() functions to include the new possible tokens. Additionally, I changed
# the list e to include "binOp" as an AST node. Many of the additions for this
# and exercise 2 were largely mechanical. I made the labels generally 3 or 4 chars
# long just for some consistency. Other than that, I think the code is
# straightforward. Nothing fancy here.
#
# Now at the end of the assignment, everything parses at it should. Only thing
# I need to touch up on is the prettyPrint function to see if I can make it
# actually pretty.
# ------------------------------------------------------------
#
# WRITTEN EXERCISE ANSWERS
#
# Exercise 2: I chose to represent boolean literals with the AST node
#   ["Bool", true/false] for simplicity. Nothing special here. I considered
#   the idea of having a catch-all ["Literal",...] node but decided against it
#   for now, though it may come in handy later when we start evaluating.
#   UPDATE: For the updated grammar involving logical operators (AND,OR,NOT), I
#   chose to represent those in the AST with ["And",..,..]. I decided to remove
#   the "binOp" field from earlier just to simplify the AST a little.
#
# Exercise 4: An example of why the grammar is ambiguous:
#   Say the parser is given the string "if true then if 5 then .. else 6". The
#   ambiguity is that the parser doesn't know if the else belongs to the 'outer'
#   if construct or the 'inner'. Specifically, it can be validly (according to
#   grammer) parsed as either "if (true then (if 5 then .. ) else 6)" or
#   "if (true then (if 5 then .. else 6))". To disambiguate the grammer, you
#   would need to add extra derivation rules to account for whether an IF stmt
#   is "matched" or "unmatched", ie if the IF stmt has an ELSE attached or not.
#
# Exercise 5:
#   a) The precedence of ** in Python is higher than both * and +. I evaluated
#       3 + 2 * 10 ** 4, noted the value 20003, and proceeded to evaluate the
#       same expression with different parenthetical configurations, e.g.
#       (3+2)*10**4, 3+(2*10)**4. The expression that evaluated to the same as the
#   original expression was 3+2*(10**4).
#   b) Using a similar method as above, I evaluated 2**3**4 and noted the value
#       2417851639229258349412352. The expression (2**3)**4 produced a different
#       value while 2**(3**4) produced the original value, which implies that
#       Python has right-associativity with exponentiation.
# ------------------------------------------------------------
#

import sys
import unittest

def parseExpn(tokens):
    #
    # #<expn> ::= let val <name> = <expn> in <expn> end
    # <expn> ::= if <expn> then <expn> else <expn>
    # <expn> ::= <disj>
    #
    disj = True
    while tokens.next() == 'let':
        # my assumption is that if tokens.eat(..) will raise exception if
        # those arguments aren't present. is that the case? YES
        disj = False

        tokens.eat('let')
        tokens.eat('val')
        e1 = parseAtom(tokens)
        tokens.eat('=')
        e2 = parseExpn(tokens)
        tokens.eat('in')
        e3 = parseExpn(tokens)
        tokens.eat('end')

        e = ['Let',e1,e2,e3]
    while tokens.next() == 'if':
        disj = False

        e3 = []
        tokens.eat('if')
        e1 = parseExpn(tokens)
        tokens.eat('then')
        e2 = parseExpn(tokens)
        if tokens.next() == 'else':
            tokens.eat('else')
            e3 = parseExpn(tokens)
            e = ["If",e1,e2,e3]
        else:
            e = ["If",e1,e2,None]
    if disj:
        e = parseDisj(tokens)
    return e

def parseDisj(tokens):
    #
    # <disj> ::= <disj> orelse <conj> | <conj>
    #
    e = parseConj(tokens)
    while tokens.next() == 'orelse':
        tokens.eat('orelse')
        ep = parseConj(tokens)
        e = ['OrEl',e,ep]
    return e

def parseConj(tokens):
    #
    # <conj> ::= <conj> andalso <cmpn> | <cmpn>
    #
    e = parseCmpn(tokens)
    while tokens.next() == 'andalso':
        tokens.eat('andalso')
        ep = parseCmpn(tokens)
        e = ['AndA',e,ep]
    return e

def parseCmpn(tokens):
    #
    # <cmpn> ::= <addn> = <addn> | <addn> < <addn> | <addn>
    #
    e = parseAddn(tokens)
    while tokens.next() == '=' or tokens.next() == '<':
        if tokens.next() == '=':
            tokens.eat('=')
            ep = parseAddn(tokens)
            e = ['Eqls',e,ep]
        elif tokens.next() == '<':
            tokens.eat('<')
            ep = parseAddn(tokens)
            e = ['LThn',e,ep]
    return e

def parseAddn(tokens):
    #
    # <addn> ::= <addn> + <mult> | <addn> - <mult> | <mult>
    #
    e = parseMult(tokens)
    while tokens.next() == '+' or tokens.next() == '-':
        if tokens.next() == '+':
            tokens.eat('+')
            ep = parseMult(tokens)
            e = ["Plus",e,ep]
        else:
            tokens.eat('-')
            ep = parseMult(tokens)
            e = ["Mins",e,ep]
    return e

def parseMult(tokens):
    #
    # <mult> ::= <mult> * <powr> | <mult> div <powr> | <mult> mod <powr> | <powr>
    #

    e = parsePowr(tokens)
    while tokens.next() == '*' or tokens.next() == 'div' or tokens.next() == 'mod':
        if tokens.next() == '*':
            tokens.eat('*')
            ep = parsePowr(tokens)
            e = ["Tims",e,ep]
        elif tokens.next() == 'div':
            tokens.eat('div')
            ep = parsePowr(tokens)
            e = ["Div",e,ep]
        else:
            tokens.eat('mod')
            ep = parsePowr(tokens)
            e = ["Mod",e,ep]
    return e

def parsePowr(tokens):
    #
    # <powr> ::= <nega> ** <powr> | <nega>
    #
    e = parseNega(tokens)
    while tokens.next() == '**':
        tokens.eat('**')
        ep = parsePowr(tokens)
        e = ["Powr",e,ep]
    return e

def parseNega(tokens):
    #
    #  <nega> ::= not <atom> | <atom>
    #
    if tokens.next() == 'not':
        while tokens.next() == 'not':
            tokens.eat('not')
            ep = parseAtom(tokens)
            e = ['Not',ep]
    else:
        e = parseAtom(tokens)
    return e

def parseAtom(tokens):
    #
    # <atom> ::= 375
    #
    if tokens.nextIsInt():
        n = tokens.eatInt()
        return ["Num",n]

    #
    # <atom> ::= ( <expn> )
    #
    elif tokens.next() == '(':
        tokens.eat('(')
        e = parseExpn(tokens)
        tokens.eat(')')
        return e

    #
    # <atom> ::= <name>
    #
    elif tokens.nextIsName():
        x = tokens.eatName()
        return ["Var",x]

    #
    # <atom> ::= true | false
    #
    elif tokens.nextIsBool():
        x = tokens.eatBool()
        return ["Bool",x]


    else:
        where = tokens.report()
        err1 = "Unexpected token at "+where+". "
        err2 = "Saw: '"+tokens.next()+"'. "
        raise SyntaxError(err1 + err2)

#
# ------------------------------------------------------------
#

#
# The supporting code and driver follows below here
#

# Not the cleanest or most elegant. Works decently well for most derivations
# I tried. The numbers 5 and 6 in the two print statements are approximations
# for spacing that made the output look decent.
"""
def prettyPrint(ast,depth=0):
    # recursive case
    if isinstance(ast,list) and len(ast)>=2:
        # If the length of the list is >=2, then what?
        # we know [0] is the 'label' of the operation (plus, times, etc)
        # [1] is left subtree,
        # [2] is right subtree.
        # if length is == 2, then [0] is label, [1] is only child

        print(ast[0]+'-'+'+'+'-',end='')
        if len(ast)>2:
            depth = depth+1
            # recursive call on right subtree
            prettyPrint(ast[2],depth)
            print( (' '*5 + '|')*depth )
            print(' '*6*(depth) + '+',end='')
        # recursive call on left subtree (or only subtree, depending)
        prettyPrint(ast[1],depth)
    # base case
    elif not isinstance(ast,list):
        # ast is a literal
        print(ast)
        return
"""
# A much less fussy version of prettyPrint(). Doesn't display links but it's also
# more consistent, with a much clearer graphical relationship between nodes.
def prettyPrint(ast,depth=0):
    if isinstance(ast,list) and len(ast)>=2:
        print('\t'*depth + '['+ast[0]+']')

        depth = depth + 1
        prettyPrint(ast[1],depth)
        if len(ast)>2:
            prettyPrint(ast[2],depth)
            if len(ast)>3:
                depth = depth+1
                prettyPrint(ast[3],depth)

    elif not isinstance(ast,list):
        print('\t'*depth + '['+str(ast)+']')
        print()
        return

def parseAndReport(tks):
    ast = parseExpn(tks)
    tks.checkEOF()  # Check if everything was consumed.
    print()
    print(ast)
    print()
    prettyPrint(ast)
    print()

def loadAll(files):
    try:
        # Load definitions from the specified source files.
        for fname in files:
            print("[opening "+fname+"]")
            f = open(fname,"r")
            src = f.read()
            tks = TokenStream(src,filename=fname)
            ast = parseAndReport(tks)
    except SyntaxError as e:
        print("Syntax error.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except ParseError as e:
        print("Failed to consume all the input in the parse.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except LexError as e:
        print("Bad token reached.")
        print(e.args[0])
        print("Bailing command-line loading.")


#
# Exceptions
#
# These define the exception raised by the interpreter.
#
class ParseError(Exception):
    pass

class SyntaxError(Exception):
    pass

class LexError(Exception):
    pass

#
# Keywords, primitives, unary operations, and binary operations.
#
# The code below defines several strings or string lists used by
# the lexical analyzer (housed as class TokenStream, below).
#

RESERVED = ['if','then','else',
            'while','do','done',
            'let','ref','in', 'val',
            'begin','end',
            'not','mod',
            'true','false',
            'print_string','read_line','string_of_int','int_of_string',
            'eof']

# Characters that separate expressions.
DELIMITERS = '();,'

# Characters that make up unary and binary operations.
OPERATORS = '+-*/<>=&!:'


#
# LEXICAL ANALYSIS / TOKENIZER
#
# The code below converts ML source code text into a sequence
# of tokens (a list of strings).  It does so by defining the
#
#    class TokenStream
#
# which describes the methods of an object that supports this
# lexical conversion.  The key method is "analyze" which provides
# the conversion.  It is the lexical analyzer for ML source code.
#
# The lexical analyzer works by CHOMP methods that processes the
# individual characters of the source code's string, packaging
# them into a list of token strings.
#
# The class also provides a series of methods that can be used
# to consume (or EAT) the tokens of the token stream.  These are
# used by the parser.
#


class TokenStream:

    def __init__(self,src,filename="STDIN"):
        """
        Builds a new TokenStream object from a source code string.
        """
        self.sourcename = filename
        self.source = src # The char sequence that gets 'chomped' by the lexical analyzer.
        self.tokens = []  # The list of tokens constructed by the lexical analyzer.
        self.extents = []
        self.starts = []

        # Sets up and then runs the lexical analyzer.
        self.initIssue()
        self.analyze()
        self.tokens.append("eof")

    #
    # PARSING helper functions
    #

    def lexassert(self,c):
        if not c:
            self.raiseLex("Unrecognized character.")

    def raiseLex(self,msg):
        s = self.sourcename + " line "+str(self.line)+" column "+str(self.column)
        s += ": " + msg
        raise LexError(s)

    def next(self):
        """
        Returns the unchomped token at the front of the stream of tokens.
        """
        return self.tokens[0]

    def advance(self):
        """
        Advances the token stream to the next token, giving back the
        one at the front.
        """
        tk = self.next()
        del self.tokens[0]
        del self.starts[0]
        return tk

    def report(self):
        """
        Helper function used to report the location of errors in the
        source code.
        """
        lnum = self.starts[0][0]
        cnum = self.starts[0][1]
        return self.sourcename + " line "+str(lnum)+" column "+str(cnum)

    def eat(self,tk):
        """
        Eats a specified token, making sure that it is the next token
        in the stream.
        """
        if tk == self.next():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected: '"+tk+"'. "
            raise SyntaxError(err1 + err2 + err3)

    def eatInt(self):
        """
        Eats an integer literal token, making sure that such a token is next
        in the stream.
        """
        if self.nextIsInt():
            tk = self.advance()
            if tk[0] == '-':
                return -int(tk[1:])
            else:
                return int(tk)
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected an integer literal. "
            raise SyntaxError(err1 + err2 + err3)

    def eatName(self):
        """
        Eats a name token, making sure that such a token is next in the stream.
        """
        if self.nextIsName():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a name. "
            raise SyntaxError(err1 + err2 + err3)

    def eatString(self):
        """
        Eats a string literal token, making sure that such a token is next in the stream.
        """
        if self.nextIsString():
            return self.advance()[1:-1]
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a string literal. "
            raise SyntaxError(err1 + err2 + err3)

    def eatBool(self):
        if self.nextIsBool():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a bool literal. "
            raise SyntaxError(err1 + err2 + err3)

    def nextIsInt(self):
        """
        Checks if next token is an integer literal token.
        """
        tk = self.next()
        return tk.isdigit()

    def checkEOF(self):
        """
        Checks if next token is an integer literal token.
        """
        if self.next() != 'eof':
            raise ParseError("Parsing failed to consume tokens "+str(self.tokens[:-1])+".")


    def nextIsName(self):
        """
        Checks if next token is a name.
        """
        tk = self.next()
        isname = tk[0].isalpha() or tk[0] =='_'
        for c in tk[1:]:
            isname = isname and (c.isalnum() or c == '_')
        return isname and (tk not in RESERVED)

    def nextIsString(self):
        """
        Checks if next token is a string literal.
        """
        tk = self.next()
        return tk[0] == '"' and tk[-1] == '"'

    def nextIsBool(self):
        # Checks if next token is bool literal
        tk = self.next()
        isbool = (tk == 'true') or (tk == 'false')
        return isbool


    #
    # TOKENIZER helper functions
    #
    # These are used by the 'analysis' method defined below them.
    #
    # The parsing functions EAT the token stream, whereas
    # the lexcial analysis functions CHOMP the source text
    # and ISSUE the individual tokens that form the stream.
    #

    def initIssue(self):
        self.line = 1
        self.column = 1
        self.markIssue()

    def markIssue(self):
        self.mark = (self.line,self.column)

    def issue(self,token):
        self.tokens.append(token)
        self.starts.append(self.mark)
        self.markIssue()

    def nxt(self,lookahead=1):
        if len(self.source) == 0:
            return ''
        else:
            return self.source[lookahead-1]

    def chompSelector(self):
        self.lexassert(self.nxt() == '#' and self.nxt(2).isdigit())
        token = self.chompChar()
        token = '#'
        while self.nxt().isdigit():
            token += self.chompChar()
        self.issue(token)

    def chompWord(self):
        self.lexassert(self.nxt().isalpha() or self.nxt() == '_')
        token = self.chompChar()
        while self.nxt().isalnum() or self.nxt() == '_':
            token += self.chompChar()
        self.issue(token)

    def chompInt(self):
        ck = self.nxt().isdigit()
        self.lexassert(ck)
        token = ""
        token += self.chompChar()     # first digit
        while self.nxt().isdigit():
            token += self.chompChar() # remaining digits=
        self.issue(token)

    def chompString(self):
        self.lexassert(self.nxt() == '"')
        self.chompChar() # eat quote
        token = ""
        while self.nxt() != '' and self.nxt() != '"':
            if self.nxt() == '\\':
                self.chompChar()
                if self.nxt() == '\n':
                    self.chompWhitespace(True)
                elif self.nxt() == '\\':
                    token += self.chompChar()
                elif self.nxt() == 'n':
                    self.chompChar()
                    token += '\n'
                elif self.nxt() == 't':
                    self.chompChar()
                    token += '\t'
                elif self.nxt() == '"':
                    self.chompChar()
                    token += '"'
                else:
                    self.raiseLex("Bad string escape character")
            elif self.nxt() == '\n':
                self.raiseLex("End of line encountered within string")
            elif self.nxt() == '\t':
                self.raiseLex("Tab encountered within string")
            else:
                token += self.chompChar()

        if self.nxt() == '':
            self.raiseLex("EOF encountered within string")
        else:
            self.chompChar() # eat endquote
            self.issue('"'+token+'"')

    def chompComment(self):
        self.lexassert(len(self.source)>1 and self.source[0:1] == '(*')
        self.chompChar() # eat (*
        self.chompChar() #
        while len(self.source) >= 2 and self.source[0:1] != '*)':
            self.chomp()
        if len(self.source) < 2:
            self.raiseLex("EOF encountered within comment")
        else:
            self.chompChar() # eat *)
            self.chompChar() #

    def chomp(self):
        if self.nxt() in "\n\t\r ":
            self.chompWhitespace()
        else:
            self.chompChar()

    def chompChar(self):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        self.column += 1
        return c

    def chompWhitespace(self,withinToken=False):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        if c == ' ':
            self.column += 1
        elif c == '\t':
            self.column += 4
        elif c == '\n':
            self.line += 1
            self.column = 1
        if not withinToken:
            self.markIssue()

    def chompOperator(self):
        token = ''
        while self.nxt() in OPERATORS:
            token += self.chompChar()
        self.issue(token)

    #
    # TOKENIZER
    #
    # This method defines the main loop of the
    # lexical analysis algorithm, one that converts
    # the source text into a list of token strings.

    def analyze(self):
        while self.source != '':
            # CHOMP a string literal
            if self.source[0] == '"':
                self.chompString()
            # CHOMP a comment
            elif self.source[0:1] == '(*':
                self.chompComment()
            # CHOMP whitespace
            elif self.source[0] in ' \t\n\r':
                self.chompWhitespace()
            # CHOMP an integer literal
            elif self.source[0].isdigit():
                self.chompInt()
            # CHOMP a single "delimiter" character
            elif self.source[0] in DELIMITERS:
                self.issue(self.chompChar())
            # CHOMP an operator
            elif self.source[0] in OPERATORS:
                self.chompOperator()
            # CHOMP a reserved word or a name.
            else:
                self.chompWord()

#
#  usage:
#    python3 NaFPL.py <file 1> ... <file n>
#
#      - this runs the parser against the specified .ml files
#
if len(sys.argv) > 1:
    loadAll(sys.argv[1:])

#else:
    #print("Enter an expression to parse: ",end='')
    #parseAndReport(TokenStream(input()))
