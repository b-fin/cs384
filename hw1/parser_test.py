from parser import *
import unittest

##############
# Test suite #
##############
class TestParser(unittest.TestCase):
    # First batch of cases test functioning of each grammatical unit
    def test_atom1(self):
        ast = TokenStream("3")
        self.assertEqual(parseExpn(ast), ['Num', 3])
    def test_atom2(self):
        ast = TokenStream("x")
        self.assertEqual(parseExpn(ast), ['Var', 'x'])
    def test_atom3(self):
        ast = TokenStream("true")
        self.assertEqual(parseExpn(ast), ['Bool', 'true'])
    def test_nega(self):
        ast = TokenStream("not true")
        self.assertEqual(parseExpn(ast), ['Not',['Bool', 'true']])
    def test_powr(self):
        ast = TokenStream("5 ** 3")
        self.assertEqual(parseExpn(ast), ['Powr', ["Num", 5], ["Num", 3]])
    def test_powr2(self):
        # Tests associativity
        ast = TokenStream("5 ** 3 ** 2")
        self.assertEqual(parseExpn(ast), ['Powr', ["Num",5], ["Powr", ["Num", 3], ["Num", 2]]])
    def test_mult(self):
        # Tests associativity
        ast = TokenStream("5 * 3 mod 4 div 6")
        self.assertEqual(parseExpn(ast), ['Div',["Mod", ["Tims", ["Num", 5], ["Num", 3]], ["Num", 4]],["Num",6]])
    def test_addn(self):
        # Tests associativity
        ast = TokenStream("5 + 3 - 4")
        self.assertEqual(parseExpn(ast), ["Mins", ["Plus",["Num",5],["Num",3]], ["Num",4]])
    def test_cmpn(self):
        # Tests =
        ast = TokenStream("5 + 3 = 4")
        self.assertEqual(parseExpn(ast), ["Eqls",["Plus",["Num",5],["Num",3]],["Num",4]])
    def test_cmpn2(self):
        ast = TokenStream("5 + 3 < 4")
        self.assertEqual(parseExpn(ast), ["LThn",["Plus",["Num",5],["Num",3]],["Num",4]])
    def test_conj(self):
        ast = TokenStream("5 + 3 andalso true")
        self.assertEqual(parseExpn(ast), ["AndA",["Plus",["Num",5],["Num",3]],["Bool", "true"]])
    def test_disj(self):
        ast = TokenStream("true orelse 6 * 3")
        self.assertEqual(parseExpn(ast), ["OrEl",["Bool", "true"],["Tims",["Num",6],["Num",3]]])
    def test_let(self):
        ast = TokenStream("let val foo = 29 in 3 + 4 mod foo end")
        self.assertEqual(parseExpn(ast), ["Let",["Var", "foo"],["Num", 29],["Plus",["Num",3],["Mod",["Num",4],["Var","foo"]]]])
    def test_if(self):
        ast = TokenStream("if true then 5 + 3 else 62")
        self.assertEqual(parseExpn(ast), ["If",["Bool","true"],["Plus",["Num",5],["Num",3]],["Num",62]])
    # Second batch of cases test grammatical units in combinations
if __name__ == '__main__':
    unittest.main()
