# Homework 01: a parser
### Reed CSCI 384 Fall 2019

*Due: Friday, 9/13 at 1pm.*

In class I showed you a recursive descent parser for a calculator language
that had the following grammar:

    <expn> ::= <expn> + <expn> | <expn> + <expn> | x | 5 | ( <expn> )   
    
To build a deterministic parser, we developed the following unambiguous
grammar, making multiplication have higher precedence than addition, and
making each left associative:

    <expn> ::= <addn>
    <addn> ::= <addn> + <mult> | <mult>
    <mult> ::= <mult> * <atom> | <atom>
    <atom> ::= x | 5 | ( <expn> )

I'd like you to make a few additions to the language, and then modify the
parser accordingly. For some of these additions, you will have to work out
some details, and I'll need you to essentially complete "written" parts of
those exercises. At the top of the source file `parser.py`give a comment
in the Python code, one for each written part of the exercises that
request one.

So at the top of your parser should include some basic comments, along with
your answers to the exercises like so:

    # 
    # Author: Your Name
    # Login:  yourreeduser
    # GitHub: yOuRgitHUBuser
    # 
    # A brief description of which exercises you got working, and how you
    # tested that. You can also add other files (test scripts, test output,
    # non-working code for attempts that may have failed) to this repository.
    # So you'd mention those things here in a comment.
    #
    # Written exercises:
    #
    # Exercise 1: ...
    # ...

Consider this top comment of `parser.py` your `README` for communicating to
me about the work you did for the assignment. If you happened to collaborate
with someone (you did the work yourself, but you hashed out ideas for the
code with someone else), tell me who that was in this comment, too. 

**Note:** *The exercises get increasingly challenging/trickier.
You should start before Monday, work to get exercises 1&2 done
by the end of the day Monday, get 3&4 done by Wednesday's lecture
and then try to finish the rest, polish what you've done with tests
and comments, in time to submit by Friday. My guess is that, if you
don't, you'll be in real trouble. My suggested schedule gives you
time to ask me questions during the week and in lecture. I won't
at all be willing to help you do everything on Thursday.*

Using GitHub you could commit and push changes, say, with each 
exercise that you complete.

### Exercise 1: subtraction and division

Let's extend the syntax to include several other integer arithmetic operations. First off,
we'd like to flesh out the "additive" and "muliplicative" parts of the grammar. We'll use
syntax that we borrow from Standard ML (or just SML), one of the dialects of Robin
Milner's ML functional language. In SML there is of course subtraction using
the minus sign, and then also the two integer division operations `div` and `mod`.
These each sit at the same "precedence level" of `+` and `*`, respectively, and
are also left associative. This means that an expression like:

    x mod 10 div 3 * x - 25 * x + x mod 6

should be read as

    (((((x mod 10) div 3) * x) - (25 * x)) + (x mod 6))
    
We can just enhance our grammar above like so:

    <expn> ::= <addn>
    <addn> ::= <addn> + <mult> | <addn> - <mult> | <mult>
    <mult> ::= <mult> * <atom> | <mult> div <atom> | <mult> mod <atom> | <atom>
    <atom> ::= x | 5 | ( <expn> )

Modify the parser so that it parses instead according to this grammar. You'll
need to generate abstract syntax tree nodes (AST nodes) labeled with `Minus`,
`Div`, and `Mod`, the analogs for `Plus` and `Times`.

Alternatively, if you like, you could instead invent a new AST label `"BinOp"`
for binary operations, and have ASTs like

    ["Binop", '<', ..., ...]
    ["Binop", '+', ..., ...]
    ["Binop", 'div', ..., ...]

for all the binary operations.

### Exercise 2: logic and comparison  

Now we'll imagine that our calculator language also has a boolean value type.
This will be in preparation for adding an `if` expression in a later exercise.
It will also allow us to have variables bound to boolean values so that we
can reason about program conditions.

We add two constants `true` and `false`. These are "atomic" expressions
just like integers and variable names. We also add comparison operators `=`
and `<`. To keep things simple, let's not allow them to be "strung out." So
we won't allow

    3 = 4 = 5

or

    3 < 4 = 5

etc. And they sit at the same precedence level, lower than plus and minus, so
that

    3 + 4 < 5 * 6        3 + 4 = 5 * 6

are interpreted as

    (3 + 4) < (5 * 6)    (3 + 4) = (5 * 6)
    
Finally we add logical AND, OR, and NOT to the syntax. Following SML, we
name these binary connectives `andalso`, `orelse`, and `not`.

This leads to the following changes to the grammar. We (1) replace

    <expn> ::= <addn>
    
with

    <expn> ::= <disj>

and then (2) we include the new productions

    <disj> ::= <disj> orelse <conj> | <conj>
    <conj> ::= <conj> andalso <cmpn> | <cmpn>
    <cmpn> ::= <addn> = <addn> | <addn> < <addn> | <addn>
    
Lastly, we (3) add the productions

    <nega> ::= not <atom> | <atom>
    <atom> ::= true | false 
    
and have the `<mult>` productions go to `<nega>` instead of `<atom>`.
    
Modify the parser so that it parses this updated grammar accordingly. As
a **written exercise**, tell me in your Python headed comments what you
chose to use as the AST nodes for these additions.

You can either represent `true` and `false` with their own leaf nodes

    ["True"]
    ["False"]
    
or with something similar to what I did with integers

    ["Boolean", true]  ["Boolean", false]
    
or you can modify what we did before and introduce a catch-all "literal
constant" node label like so

    ["Literal", True]
    ["Literal", 5]
    
Just let me know in the header comment.
    
**Note:** This is all going to introduce some nonsensical expressions that
we will consider syntactically correct. For example `not 3` and `3 + true`
and `3 + 5 andalso x` will be legal and parsable. (We'll fix this later
when we do *semantic analysis* (with typechecking) rather than *syntactic
analysis* (with parsing). Though it seems wrong, this division of labor
is typical in the staging of functional programming systems' levels of
analysis.

So here's the grammar now, in full glory.
  
    <expn> ::= <disj>
    <disj> ::= <disj> orelse <conj> | <conj>
    <disj> ::= <conj> andalso <cmpn> | <cmpn>
    <cmpn> ::= <addn> = <addn> | <addn> < <addn> | <addn>    
    <addn> ::= <addn> + <mult> | <mult>
    <mult> ::= <mult> * <nega> | <nega>
    <nega> ::= not <atom> | <atom>
    <atom> ::= x | 5 | true | false | ( <expn> )
    
### Exercise 3: pretty printing

In class I showed you a version of my parser that "pretty printed" (this 
is a standard phrase!) the AST constructed by the parser as a result of a
successful parse. Mine was fairly elaborate but, roughly, indented
the contents of a subtree's node labels so that they were further right
of their parent. It also put "sibling" nodes at the same indentation 
level.

Write *similar* code for reporting the AST of a successful parse. It
need not have node links, just the indenting. And it's also fine to just
have one each node level sit on its own line. Things to the left in the
expression should be on earlier lines than things to their right.

For example, a parse of `3 + 4 * 5` could be depicted as

    Plus
        Num
           3
        Times
             Num
                4
             Num
                5
 
 In my code, I distinguished "branching" nodes from "leaf" nodes
 by whether they were a list of length one that contained only a
 label (for example, some of you might have chosen to represent
 the boolean literals as ["True"] and ["False"].
 
 The code should be recursive, and is essentially an "in order"
 traversal of the AST. It will have two base cases: (1) labelled
 subtrees that have no subtrees, that is, are lists of length
 one and (2) data values in the trees (i.e. non-lists). So 
 a Python condition like
 
     isinstance(ast,list) and len(ast) >= 2
     
 would indicate a recursive case,
 
     isinstance(ast,list) and len(ast) == 1
     
 would be the one base case, and
 
      not isinstance(ast,list)
      
would be the other.
 
*Hint*: your pretty-printer function will need to be recursive. In 
addition to having a parameter for the subtree to be output, it
should have a second parameter descrbing, saym the length of the
indentation for that subtree's output.
 
For a *BONUS* version of this exercise, you could instead try to
mimic my fancier output. Mine produced these lines of text
 
    Plus-+-Num-+-3
         | 
         +-Times-+-Num-+-4
                 | 
                 +-Num-+-5

I'm willing to give lots of hints on how to do this.

### Exercise 4: if in let else then

Let's now add two "top-level" syntactic constucts, also found in Standard ML, one for a
"conditional" `if-then-else` expression and one for `let`-binding of variable names. These
have the expression syntax:

    <expn> ::= let val <name> = <expn> in <expn> end

and

    <expn> ::= if <expn> then <expn> else <expn>
    
Modify the parser to also parse these two kinds of expressions.

As a **written exercise** let's think a little about a small grammar similar to our
So-Not-Python language. Consider this grammar:

    <stmt> ::= if C then <stmt> else <stmt>
    <stmt> ::= if C then <stmt>
    <stmt> ::= S

I claim that this grammar is ambiguous. Why? Find a token sequence generated by this grammar
that has two different derivation trees. You can indicate the two different "parses" by adding
parentheses to suggest the two trees/interpretations of the sequence.

**BONUS written exercise** fix the grammar just above so that it is not ambiguous. It should
still generate the same token sequences of the grammar, but none of those should have more
than one derivation tree. Show how it would parse the example ambiguous you gave for the
above exercise.

### Exercise 5: exponentiation  

Though SML does not have an integer exponentiation binary operator, Python does. 
In Python, the binary operator is `**`. Using the Python interpreter, explore expressions
that are a mix of `+`, `*`, and `**`. 

**Written exercise:** What is the precedence of `**` relative to `+` and `*`? Give me expressions
(and their values when entered in Python) that you used to figure out this answer.

**Written exercise:** For integer expressions like `2 ** 3 ** 4`, there has to be an "associativity"
convention that we adopt. It's either left- or right- associative in Python. Which is it?
Explain.

**Written exercise:** Rewrite the grammar for our language as developed so far, but including
this new exponentiation binary operation with token `**`.

Note that `**` is a completely
different token from `*`, even though they share the symbol that makes them up. The
`parser.py` preprocessor already does this proper "tokenization" of a string before passing
things to the parser. So the string "x * y ** z" will be fed to the parser as:

    ['x', '*', 'y', '**', 'z']
    
Now complete the parser so that it parses calculations with `**` in them, following
Python's precedence and associativity conventions.
