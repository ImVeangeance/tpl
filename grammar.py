import itertools
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Grammar:
    VT: list[str]
    VN: list[str]
    P: dict[str, list[str]]
    S: str

    def __eq__(self, other):
        p1 = {left: set(right) for left, right in self.P.items()}
        p2 = {left: set(right) for left, right in other.P.items()}
        return set(self.VT) == set(other.VT) and set(self.VN) == set(other.VN) and p1 == p2 and self.S == other.S

    def make_chains(self, min_length: int, max_length: int) -> list[str]:
        stack = [([], self.S)]
        was_in_stack = set()
        counter = 1
        sequences = []
        while stack:
            prev, sequence = stack.pop()
            prev = prev.copy()
            prev.append(sequence)
            if sequence in was_in_stack:
                continue
            was_in_stack.add(sequence)
            only_term = True
            for i, symbol in enumerate(sequence):
                #print(f'{i} {symbol}')
                if symbol in self.VN:
                    only_term = False
                    for elem in self.P[symbol]:
                        scopy = sequence[:i] + elem + sequence[i + 1:]
                        if len(scopy) <= max_length + 3:
                            stack.append((prev, scopy))
            if only_term and min_length <= len(sequence) <= max_length:
                sequences.append(sequence)
                counter += 1
        return sequences

    def find_child_free_non_terms(self) -> set[str]:
        prev_set = set()
        non_child_free = set(self.VT)
        while non_child_free != prev_set:
            prev_set = non_child_free.copy()
            for left, right in self.P.items():
                for rule in right:
                    if not set(rule) - non_child_free:
                        non_child_free.add(left)
                        break
        return set(self.VN) - non_child_free

    def remove_rules(self, rules: set):
        new_rules = defaultdict(list)
        for left, right in self.P.items():
            if left in rules:
                continue
            for rule in right:
                if not set(rule) & rules:
                    new_rules[left].append(rule)
        return Grammar(self.VT, [nt for nt in self.VN if nt not in rules], new_rules, self.S)

    def find_unreachable_rules(self) -> set[str]:
        prev_set = set()
        reachable = set(self.S)
        while prev_set != reachable:
            prev_set = reachable.copy()
            for left, right in self.P.items():
                if left in reachable:
                    for rule in right:
                        reachable.update(set(rule))
        return set(self.VN) - reachable

    @staticmethod
    def _gen_combos(rule: str, lambdas: set[str], left: str) -> list[str]:
        idxs = []
        for i, ch in enumerate(rule):
            if ch in lambdas:
                idxs.append(i)
        combos = []
        for i in range(len(idxs) + 1):
            combos.extend(itertools.combinations(idxs, i))
        new_rules = []
        for combo in combos:
            new_rule = []
            for i, ch in enumerate(rule):
                if i not in idxs or i in combo:
                    new_rule.append(ch)
            new_rule = ''.join(new_rule)
            if new_rule and new_rule != left:
                new_rules.append(new_rule)
        return new_rules

    def remove_empty_rules(self):
        lambdas = set()
        for left, right in self.P.items():
            for rule in right:
                if not rule:
                    lambdas.add(left)
                    break
        prev_set = set()
        while prev_set != lambdas:
            for left, right in self.P.items():
                prev_set = lambdas.copy()
                for rule in right:
                    if not set(rule) - lambdas:
                        lambdas.add(left)
                        break
        new_rules = defaultdict(list)
        for left, right in self.P.items():
            for rule in right:
                if rule:
                    new_rules[left].extend(self._gen_combos(rule, lambdas, left))
            new_rules[left] = list(set(new_rules[left]))

        start_sym = self.S
        new_vn = self.VN.copy()
        if self.S in lambdas:
            new_rules['$'] = [self.S, '']
            start_sym = '$'
            new_vn.append('$')
        return Grammar(self.VT, new_vn, dict(new_rules), start_sym)

    def remove_chain_rules(self):
        sets = defaultdict(set)
        for left, right in self.P.items():
            prev_set = set()
            sets[left].add(left)
            while prev_set != sets[left]:
                prev_set = sets[left].copy()
                for non_term in prev_set:
                    for rule in self.P[non_term]:
                        if rule in self.VN:
                            sets[left].add(rule)
            sets[left].remove(left)
        new_rules = self.P.copy()
        for left, right in new_rules.items():
            new_rules[left] = list(set(new_rules[left]) - sets[left])
        for left, set_ in sets.items():
            for rule in set_:
                new_rules[left] = list(set(new_rules[left]) | set(new_rules[rule]))
        return Grammar(self.VT, self.VN, new_rules, self.S)

    def remove_long_rules(self):
        old_rules = self.P
        new_rules = defaultdict(list)
        print(old_rules)
        dont_lose_it: dict = {}
        rule_counter: int = 1
        for key in old_rules:
            for rule in old_rules[key]:
                if len(rule) < 3:
                    new_rules[key].append(rule)
                    ...
                else:
                    temp = rule
                    temp1 = temp[1:]
                    new_rules[key].append(f'{temp[0]}{rule_counter}')
                    new_rules[f'{rule_counter}'].append(temp[1:])
                    rule_counter += 1
                    swap = False
                    while len(temp1) > 2:
                        for new_key in new_rules:
                            for item in new_rules[new_key]:
                                if len(item) > 2 and not item[-1].isnumeric():
                                    swap = True
                                    new_rules[new_key] = [f'{item[0]}{rule_counter}']
                                    dont_lose_it: dict = {f'{rule_counter}': [f'{item[1:]}']}
                                    rule_counter += 1
                                    break
                        temp1 = temp1[1:]
                addict: dict = {}
                addict.update(dont_lose_it)
                new_rules.update(addict)
        non_term = []
        for index in new_rules:
            non_term.append(index)
        print(non_term)
        new_gr = Grammar(self.VT, non_term, new_rules, self.S)
        return new_gr, dict(new_rules), rule_counter

    def remove_trash(self):
        print(self.P)
        new_rules = defaultdict(list)
        super_kostil: str = 'Ў¤Ё^®ЄџЂЃ‡€ЌЂ§№•~!;:?*()_+-/{}[]":;,.?'
        old_rules = self.P
        rules_count = 0
        dont_lose_it: dict = {}
        for key in old_rules:
            for rule in old_rules[key]:
                if len(rule) == 1:
                    new_rules[key].append(rule)
                elif not rule[0].islower() and not rule[1].islower():
                    new_rules[key].append(rule)
                    ...
                else:
                    if rule[0] == rule[1] and rule[0].islower():
                        print(f'!!!!!!!{key}  -> {rule}')
                        new_rules[key].append(f'{super_kostil[rules_count]}{super_kostil[rules_count]}')
                        dont_lose_it: dict = {f'{super_kostil[rules_count]}': [f'{rule[0]}']}
                        rules_count += 1
                    elif rule[0].islower():
                        print(f'{key}  -> {rule}')
                        new_rules[key].append(f'{super_kostil[rules_count]}{rule[1]}')
                        dont_lose_it: dict = {f'{super_kostil[rules_count]}': [f'{rule[0]}']}
                        rules_count += 1
                        #
                    elif rule[-1].islower():
                        print(f'{key}  -> {rule}')
                        new_rules[key].append(f'{rule[0]}{super_kostil[rules_count]}')
                        dont_lose_it: dict = {f'{super_kostil[rules_count]}': [f'{rule[1]}']}
                        rules_count += 1
                        #
                    #
                    #new_rules[key].append(rule)
                addict: dict = {}
                addict.update(dont_lose_it)
                new_rules.update(addict)
        print(dict(new_rules))
        non_term = []
        for index in new_rules:
            non_term.append(index)
        print(non_term)
        new_gr = Grammar(self.VT, non_term, new_rules, self.S)
        return new_gr, dict(new_rules)
