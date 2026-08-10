from email.mime import text
import os
import shutil
import unittest

from kojen.boolean import parse_tag_expression, eval_parsed_expr

class TestFeatures(unittest.TestCase):

    workingfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test")

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.workingfolder, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.workingfolder)

    def test_extract_IF(self):
        text = "Some text <<<IF condition1 AND condition2 OR condition3>>>"# more text <<<IF condition4 AND condition5>>>"
        result = parse_tag_expression(text, prefix="IF")
        self.assertEqual(len(result), 5, "Wrong length")
        self.assertEqual(result[0], "condition1", "Wrong 1")
        self.assertEqual(result[1], "AND", "Wrong A")
        self.assertEqual(result[2], "condition2", "Wrong 2")
        self.assertEqual(result[3], "OR", "Wrong B")
        self.assertEqual(result[4], "condition3", "Wrong 3")

    def test_extract_IF_NOT(self):
        text = "Some text <<<IF condition1 AND NOT condition2 OR NOT condition3>>>"# more text <<<IF condition4 AND condition5>>>"
        result = parse_tag_expression(text, prefix="IF")
        self.assertEqual(len(result), 7, "Wrong length")
        self.assertEqual(result[0], "condition1", "Wrong 1")
        self.assertEqual(result[1], "AND", "Wrong A")
        self.assertEqual(result[2], "NOT", "Wrong B")
        self.assertEqual(result[3], "condition2", "Wrong 2")
        self.assertEqual(result[4], "OR", "Wrong C")
        self.assertEqual(result[5], "NOT", "Wrong D")
        self.assertEqual(result[6], "condition3", "Wrong 3")

    def test_extract_IF_NOT2(self):
        text = "Some text <<<IF NOT condition1 AND NOT condition2 OR NOT condition3>>>"# more text <<<IF condition4 AND condition5>>>"
        result = parse_tag_expression(text, prefix="IF")
        self.assertEqual(len(result), 8, "Wrong length")
        self.assertEqual(result[0], "NOT", "Wrong A")
        self.assertEqual(result[1], "condition1", "Wrong 1")
        self.assertEqual(result[2], "AND", "Wrong B")
        self.assertEqual(result[3], "NOT", "Wrong C")
        self.assertEqual(result[4], "condition2", "Wrong 2")
        self.assertEqual(result[5], "OR", "Wrong D")
        self.assertEqual(result[6], "NOT", "Wrong E")
        self.assertEqual(result[7], "condition3", "Wrong 3")

    def test_extract_brackets(self):
        text = "Some text <<<IF (condition1 AND condition2) OR condition3 AND NOT (condition4 OR NOT condition5)>>>"# more text <<<IF condition4 AND condition5>>>"
        result = parse_tag_expression(text, prefix="IF")
        self.assertEqual(len(result), 6, "Wrong length")
        self.assertEqual(result[0], ["condition1", "AND", "condition2"], "Wrong A")
        self.assertEqual(result[1], "OR", "Wrong B")
        self.assertEqual(result[2], "condition3", "Wrong C")
        self.assertEqual(result[3], "AND", "Wrong D")
        self.assertEqual(result[4], "NOT", "Wrong E")
        self.assertEqual(result[5], ["condition4", "OR", "NOT", "condition5"], "Wrong F")

    def test_extract_brackets2(self):
        text = "Some text <<<ELSEIF NOT (condition1 OR condition2) OR NOT condition3 AND NOT (condition4 OR NOT condition5) OR condition6>>> bla bla bla"
        result = parse_tag_expression(text, prefix="ELSEIF")
        self.assertEqual(len(result), 10, "Wrong length")
        self.assertEqual(result[0], "NOT", "Wrong A")
        self.assertEqual(result[1], ["condition1", "OR", "condition2"], "Wrong B")
        self.assertEqual(result[2], "OR", "Wrong C")
        self.assertEqual(result[3], "NOT", "Wrong D")
        self.assertEqual(result[4], "condition3", "Wrong E")
        self.assertEqual(result[5], "AND", "Wrong F")
        self.assertEqual(result[6], "NOT", "Wrong G")
        self.assertEqual(result[7], ["condition4", "OR", "NOT", "condition5"], "Wrong H")
        self.assertEqual(result[8], "OR", "Wrong I")
        self.assertEqual(result[9], "condition6", "Wrong J")

    def test_evaluate_simple(self):
        text = "Some text <<<ELSEIF (condition1 OR condition2) AND NOT (condition3)>>> bla bla bla"
        result = parse_tag_expression(text, prefix="ELSEIF")
        def condition_fn(name: str, x) -> bool:
            mapping = {
                "condition1": True,
                "condition2": False,
                "condition3": False,
            }
            print(f"Evaluating condition {name} with x={x}")
            return mapping[name]

        result = eval_parsed_expr(result, condition_fn, "boo")
        self.assertTrue(result)

    def test_evaluate_simple_not(self):
        text = "Some text <<<ELSEIF NOT (condition1 OR condition2) AND NOT (condition3)>>> bla bla bla"
        result = parse_tag_expression(text, prefix="ELSEIF")
        def condition_fn(name: str) -> bool:
            mapping = {
                "condition1": True,
                "condition2": False,
                "condition3": False,
            }
            return mapping[name]

        result = eval_parsed_expr(result, condition_fn)
        condition1 = True
        condition2 = False
        condition3 = False
        c = not (condition1 or condition2) and not (condition3)
        self.assertEqual(result, c)

    def test_evaluate_simple2(self):
        text = "Some text <<<ELSEIF (condition1 OR condition2) AND (condition3)>>> bla bla bla"
        result = parse_tag_expression(text, prefix="ELSEIF")
        def condition_fn(name: str) -> bool:
            # replace with your real checks
            mapping = {
                "condition1": True,
                "condition2": False,
                "condition3": False,
            }
            return mapping[name]

        result = eval_parsed_expr(result, condition_fn)
        condition1 = True
        condition2 = False
        condition3 = False
        c = (condition1 or condition2) and (condition3)
        self.assertEqual(result, c)

    def test_evaluate_less_simple(self):
        text = "Some text <<<IF ((condition1 AND condition2) OR condition3) AND NOT (condition4 OR NOT condition5)>>>"# more text <<<IF condition4 AND condition5>>>"
        result = parse_tag_expression(text, prefix="IF")

        def condition_fn(name: str) -> bool:
            # replace with your real checks
            mapping = {
                "condition1": True,
                "condition2": False,
                "condition3": True,
                "condition4": True,
                "condition5": True,
            }
            return mapping[name]

        result = eval_parsed_expr(result, condition_fn)
        condition1 = True
        condition2 = False
        condition3 = True
        condition4 = True
        condition5 = True
        c = ((condition1 and condition2) or condition3) and not (condition4 or not condition5)
        self.assertEqual(result, c)