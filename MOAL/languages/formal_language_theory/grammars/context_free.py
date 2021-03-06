# -*- coding: utf-8 -*-

__author__ = """Chris Tabor (dxdstudio@gmail.com)"""

if __name__ == '__main__':
    from os import getcwd
    from os import sys
    sys.path.append(getcwd())

from MOAL.helpers.display import Section
from MOAL.helpers.display import prnt
from random import choice
from string import ascii_uppercase
from string import punctuation


DEBUG = True if __name__ == '__main__' else False


class InvalidTokenSet(Exception):
    pass


class ContextFreeGrammar(object):

    def __init__(self):
        self.rules = []
        self.terminus = '$'
        self.mapping_token = ' => '
        self.DEBUG = False
        self.indent = ' ' * 4

    def __delitem__(self, rule):
        for index, rule in enumerate(self.rules):
            if rule[0] == rule:
                del self.rules[index]

    def __contains__(self, word):
        """Tests if a word can be created using the
        existing internal grammar and rules."""
        return self.evaluate() == word

    def add_rule(self, string):
        if self.mapping_token not in string:
            raise TypeError('Invalid rule representation. '
                            'Use a {} to indicate mapping.'.format(
                                self.mapping_token))
        left, right = string.split(self.mapping_token)
        if '|' in right:
            right = right.split('|')
        self.rules.append([left, right])
        if self.DEBUG:
            print('Added rule: "{}"'.format(self.rules[-1]))

    def _get_rule(self, token):
        for rule in self.rules:
            left, right = rule
            if left == token:
                if isinstance(right, list):
                    return choice(right)
                else:
                    return right
        return ''

    def set_rules(self, rules):
        self.rules = []
        for rule_str in rules:
            self.add_rule(rule_str)

    def set_tokens(self, tokens):
        self.tokens = tokens

    def delete_rules(self):
        self.rules = []

    def delete_tokens(self):
        self.tokens = []

    def _is_terminal_or(self, char):
        is_terminal = False
        for option in char:
            if option.endswith(self.terminus):
                is_terminal = True
                break
        return is_terminal

    def _is_terminal(self, char):
        if isinstance(char, list):
            if self._is_terminal_or(char):
                return True
        else:
            if char.endswith(self.terminus):
                print('{}Completed'.format(' ' * 4))
                return True

    def evaluate_single(self, token, nonterminals, evaluation=''):
        """Recursively evaluates a single rule with a token and a given
        set of non-terminals"""
        # TODO: implement backtracking when encountering OR evaluation
        rule = self._get_rule(token)
        for char in rule:
            if self._is_terminal(char):
                return evaluation
            sub_rule = self._get_rule(char)
            print('{}Char: {}, Subrule: {}, (Parent rule: {})'.format(
                self.indent, char, sub_rule if sub_rule else '[empty]', rule))
            if sub_rule:
                for sub_char in sub_rule:
                    if sub_char in nonterminals:
                        print('{}Nonterminal: {}'.format(
                            self.indent * 2, sub_char))
                        evaluation += self.evaluate_single(
                            sub_char, nonterminals, evaluation=evaluation)
                    else:
                        print('{}Terminal: {}'.format(
                            self.indent * 2, sub_char))
                        if sub_char != self.terminus:
                            evaluation += sub_char
                        else:
                            return evaluation
            else:
                evaluation += char
            curr = '[{}]'.format(evaluation if evaluation else '[empty]')
            print('{}{}\n'.format('.' * abs(80 - len(curr)), curr))
        return evaluation

    def evaluate(self, tokens=None, evaluation=''):
        """A basic parser for a custom attribute grammar.

        One thing to note is that ambiguous grammars need to be iterated over,
        since the duplicate rules can't be mapped via dictionary key.
        Unambiguous grammars are therefore more performant,
        because the lookup is O(1) vs. O(N).
        """
        if tokens is None:
            if hasattr(self, 'tokens'):
                tokens = self.tokens
            else:
                raise InvalidTokenSet
        nonterminals = [r[0] for r in self.rules]
        print('Ruleset: {}, Tokens: {}'.format(self.rules, tokens))
        for token in tokens:
            print('\n<{}>\n\nToken: {}'.format('=' * 80, token))
            evaluation += self.evaluate_single(token, nonterminals)
        print('\nFinal value: "{}"\n'.format(evaluation))
        return evaluation


def cp():
    return choice(punctuation)


def cu():
    return choice(ascii_uppercase)


if DEBUG:
    with Section('Grammar parser - basic'):
        cfg = ContextFreeGrammar()

        # There are two rules for the same mapping "S"; thus, it's ambiguous.
        ambig_grammar = [
            'S => <{++>U<>',
            'U => {}VV',
            'B => \\{//U\\++}',
            'V => *&&&*!$'
        ]
        ambiguous_cfg = ContextFreeGrammar()
        map(ambiguous_cfg.add_rule, ambig_grammar)
        tokens = [choice(['S', 'U', 'B', 'V']) for _ in range(10)]

        wiki_grammar = [
            'S => UV',
            'U => aBc-bBac',
            'B => caa$',
            'V => ac B bca U']

        letters = ['S', 'U', 'B', 'V']
        cfg.set_rules(wiki_grammar)

        def cfg1():
            prnt('CFG result', '')
            cfg.evaluate(tokens=['B', 'B', 'B', 'V', 'U'])
            cfg.evaluate(tokens=['U', 'C', 'B', 'V', 'U', 'S'])
            cfg.evaluate(tokens=[choice(letters) for _ in range(10)])

        def cfg2():
            prnt('Ambiguous CFG result', ambiguous_cfg.evaluate(tokens=tokens))

        choices = {
            '1': cfg1,
            '2': cfg2
        }
        DEBUG = False
        if DEBUG:
            _choices = choices.keys()
            _choice = raw_input('Pick a CFG to run: {} ==> '.format(_choices))
            try:
                choices[_choice]()
            except KeyError:
                pass
        else:
            for func in choices:
                choices[func]()

        cfg.set_rules([
            'A => B|C|D|E|F',
            'B => b',
            'C => c',
            'D => h',
            'E => s',
            'F => G$',
            'G => ay|ey|iy|oy|uy',
            'Z => at$',
        ])
        # Test OR capability
        assert cfg.evaluate(['E', 'F']) in ['say', 'sey', 'siy', 'soy', 'suy']

        membership = [
            ('at', ['Z']),
            ('bat', ['B', 'Z']),
            ('cat', ['C', 'Z']),
            ('hat', ['D', 'Z']),
            ('sat', ['E', 'Z']),
        ]
        for test in membership:
            word, new_tokens = test
            cfg.set_tokens(new_tokens)
            assert word in cfg
