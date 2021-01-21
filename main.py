__theme__ = 'Написать программу, которая будет принимать на вход контекстно-свободную грамматику в каноническом виде ' \
            '(проверить корректность задания и при отрицательном результате выдать соответствующее сообщение) ' \
            'и приведёт' \
            ' её к нормальной форме Хомского. Программа должна проверить построенную грамматику (БНФ) ' \
            'на эквивалентность' \
            ' исходной: по обеим грамматикам сгенерировать множества всех цепочек в заданном пользователем диапазоне ' \
            'длин и проверить их на идентичность. Для подтверждения корректности выполняемых действий ' \
            'предусмотреть возможность корректировки любого из построенных множеств пользователем ' \
            '(изменение цепочки, ' \
            'добавление, удаление…).При обнаружении несовпадения должна выдаваться диагностика различий – где именно ' \
            'несовпадения и в чём они состоят. Построить дерево вывода для любой выбранной ' \
            'цепочки из числа сгенерированных.'

import json
import sys

from PySide2.QtCore import SIGNAL
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

import utils
from grammar import Grammar
from ui import Ui_MainWindow
#from graphical_tree import GraphicalTree, Vertex


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def fill_form_with_grammar(grammar: Grammar):
    if not (lam := get_lambda()):
        return
    ui = window.ui
    ui.lineEdit.setText(', '.join(grammar.VT))
    ui.lineEdit_2.setText(', '.join(grammar.VN))
    update_start_s(grammar.S)
    ui.plainTextEdit.clear()
    for sym, rules in grammar.P.items():
        rules = [rule if rule else lam for rule in rules]
        ui.plainTextEdit.appendPlainText(f'{sym} -> {" | ".join(rules)}')


def fill_form_with_grammar_h(grammar: Grammar):
    if not (lam := get_lambda()):
        return
    ui = window.ui
    ui.lineEdit.setText(', '.join(grammar.VT))
    #ui.lineEdit_2.setText(', '.join(grammar.VN))
    update_start_s(grammar.S)
    ui.plainTextEdit_6.clear()
    ui.plainTextEdit_6.appendPlainText(grammar_to_str(grammar))


def open_grammar_file():
    filename, _ = QFileDialog.getOpenFileName(filter='Text files (*.json)')
    if filename:
        try:
            grammar = Grammar(**json.load(open(filename)))
        except (json.JSONDecodeError, TypeError):
            print_to_pte5('Ошибка. Файл грамматики в неверном формате. '
                             'Откройте справку для получения информации о формате файла')
            return
        if not check_grammar(grammar):
            return
        fill_form_with_grammar(grammar)


def print_to_pte5(string: str):
    window.ui.plainTextEdit_5.appendPlainText(string)


def check_grammar(grammar: Grammar) -> bool:
    if not grammar.VN:
        print_to_pte5("В грамматике отсутствует список нетерминальных символов!")
        return False
    if not grammar.VT:
        print_to_pte5("В грамматике отсутствует список терминальных символов!")
        return False
    if not grammar.S:
        print_to_pte5("Стартовый символ не задан!")
        return False
    if intersection := set(grammar.VT) & set(grammar.VN):
        print_to_pte5(f'Символы {", ".join(intersection)} находятся как во множестве терминальных, так и во '
                         f'множестве нетерминальных символов. Грамматика задана неверно!')
        return False
    if grammar.S not in grammar.VN:
        print_to_pte5(f'Символ {grammar.S} не находится в списке терминальных символов. Грамматика задана неверно!')
        return False
    for sym, rules in grammar.P.items():
        if sym not in grammar.VN:
            print_to_pte5(f'Символ {sym} находится в списке правил, но его нет в списке нетерминальных символов. '
                             f'Грамматика задана неверно!')
            return False
        if not rules:
            print_to_pte5(f'Для символа {sym} в грамматике отсутствуют правила!')
            return False
        if sym in grammar.VT:
            print_to_pte5(f'Символ {sym} находится в списке терминальных символов, но при этом используется '
                             f'в левой части правил. Грамматика задана неверно!')
            return False
        for rule in rules:
            if rules.count(rule) != 1:
                print_to_pte5(f'Правило {rule} не может находиться в правой части правила более одного раза!')
                return False
            for chain_sym in rule:
                if chain_sym not in grammar.VN and chain_sym not in grammar.VT:
                    print_to_pte5(f'Символ {chain_sym} не находится ни во множестве терминальных, ни во множестве '
                                     f'нетерминальных символов, но при этом есть в грамматике. '
                                     f'Грамматика задана неверно!')
                    return False
    return True


def get_lambda() -> str:
    sym = window.ui.lineEdit_3.text()
    if not sym:
        print_to_pte5('Введите символ лямбды! Он не может быть пустым')
    return sym


def read_grammar_from_form() -> Grammar:
    if not (lam := get_lambda()):
        return False
    ui = window.ui
    try:
        print(ui.plainTextEdit.toPlainText())
        p = utils.parse_rules(ui.plainTextEdit.toPlainText(), lam)
        print('Can gramm rules - ', p)
    except utils.WrongRule as e:
        print_to_pte5(e.message)
        return False
    return Grammar(
        utils.split_by(ui.lineEdit.text(), ','),
        utils.split_by(ui.lineEdit_2.text(), ','),
        p,
        window.ui.comboBox.currentText()
    )


def read_grammar_from_form_h(vn) -> Grammar:
    if not (lam := get_lambda()):
        return False
    ui = window.ui
    try:
        print('DEBUG - ', ui.plainTextEdit_6.toPlainText()[2])
        print('D - ', ui.plainTextEdit_6.toPlainText().split('P:')[1])
        p = utils.parse_rules(ui.plainTextEdit_6.toPlainText().split('P:')[1], lam)
    except utils.WrongRule as e:
        print_to_pte5(e.message)
        return False
    return Grammar(
        utils.split_by(ui.lineEdit.text(), ','),
        vn,
        p,
        window.ui.comboBox.currentText()
    )


def update_start_s(sym=None):
    cbox = window.ui.comboBox
    current = cbox.currentText()
    text = window.ui.lineEdit_2.text()
    vals = utils.split_by(text, ',')
    cbox.clear()
    cbox.addItems(vals)
    if mb_new_sym := current or sym:
        if mb_new_sym in vals:
            cbox.setCurrentText(mb_new_sym)


def grammar_to_str(grammar: Grammar) -> str:
    rules = []
    for left, right in grammar.P.items():
        rules.append(f'  {left} -> {" | ".join([rule if rule else get_lambda() for rule in right])}')
    return (f'G({{{", ".join(grammar.VT)}}}, {{{", ".join(grammar.VN)}}}, P, {grammar.S})\n'
            f'P:\n' + '\n'.join(rules))


def remove_empty_and_chains_rules(grammar: Grammar) -> Grammar:
    child_free = grammar.find_child_free_non_terms()
    if child_free:
        print_to_pte5(f'Обнаружены бесплодные нетерминальные символы: {", ".join(child_free)}')
        grammar = grammar.remove_rules(child_free)
        print_to_pte5('Грамматика после удаления бесплодных символов:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Бесплодных нетерминальных символов не обнаружено!')
    unreacheble = grammar.find_unreachable_rules()
    if unreacheble:
        print_to_pte5(f'Обнаружены недостижимые нетерминальные символы: {", ".join(unreacheble)}')
        grammar = grammar.remove_rules(unreacheble)
        print_to_pte5('Грамматика после удаления недостижимых символов:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Недостижимых нетерминальных символов не обнаружено!')
    return grammar


def save_to_file():
    filename, _ = QFileDialog.getSaveFileName(filter='Text files (*.txt)')
    if not filename:
        return
    strings = []
    strings.append('Исходная грамматика:\n\n')
    strings.append(grammar_to_str(read_grammar_from_form()))
    if window.ui.plainTextEdit_2.toPlainText():
        strings.append('\nГрамматика в каноническом виде:\n\n')
        strings.append(window.ui.plainTextEdit_2.toPlainText())
        strings.append('\nЦепочки грамматики канонического виде:\n\n')
        strings.append(window.ui.plainTextEdit_3.toPlainText())
        strings.append('\nГрамматика Хомского}:\n\n')
        strings.append(window.ui.plainTextEdit_6.toPlainText())
        strings.append('\nЦепочки грамматики вида Хомского:\n\n')
        strings.append(window.ui.plainTextEdit_4.toPlainText())
    open(filename, 'w').writelines(strings)


def build_canon_grammar(grammar: Grammar) -> Grammar:
    print_to_pte5('{: ^200}'.format('Начато приведение грамматики в каноничный вид'))
    grammar_before_delete_empty_rules_and_chains = grammar
    grammar = remove_empty_and_chains_rules(grammar)
    grammar = grammar.remove_empty_rules()
    if grammar != grammar_before_delete_empty_rules_and_chains:
        print_to_pte5('Удаление пустых правил...')
        print_to_pte5('Грамматика после удаления пустых правил:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Пустых правил не обнаружено!')
    grammar_before_remove_chain_rulse = grammar
    grammar = grammar.remove_chain_rules()
    if grammar != grammar_before_remove_chain_rulse:
        print_to_pte5('Удаление цепных правил...')
        print_to_pte5('Грамматика после удаления цепных правил:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Цепных правил не обнаружено!')
    grammar = remove_empty_and_chains_rules(grammar)
    if grammar_before_delete_empty_rules_and_chains == grammar:
        print_to_pte5('{: ^200}'.format('Грамматика поданная на вход изначально является канонической'))
    else:
        print_to_pte5('{: ^200}'.format('Завершено приведение грамматики к каноничному виду\n'))
    return grammar


def start():
    if not (grammar := read_grammar_from_form()):
        return
    if not check_grammar(grammar):
        return
    #
    update_start_s()
    canon_grammar = build_canon_grammar(grammar)
    window.ui.plainTextEdit_2.setPlainText(grammar_to_str(canon_grammar))
    # print_to_actions()
    canon_sequences = canon_grammar.make_chains(window.ui.spinBox.value(), window.ui.spinBox_2.value())
    canon_sequences = [seq if seq else get_lambda() for seq in canon_sequences]
    window.ui.plainTextEdit_3.setPlainText('\n'.join(sorted(canon_sequences)))
    return holmsky(canon_grammar)


def compare_chains():
    canon_chains = set(window.ui.plainTextEdit_3.toPlainText().splitlines())
    h_chains = set(window.ui.plainTextEdit_4.toPlainText().splitlines())
    if h_chains == canon_chains:
        QMessageBox.information(window, 'Статус', 'Статус: множества цепочек равны')
    else:
        QMessageBox.information(window, 'Статус', 'Статус: множества цепочек не равны')


def holmsky(grammar: Grammar):
    print_to_pte5('{: ^200}'.format('Начато приведение канонической грамматики к бинарной грамматике Хомского'))
    print(grammar)
    # step 1 - remove long rules (2 <)
    old_gr: Grammar.P = grammar.P
    grammar, rules, rules_count = grammar.remove_long_rules()
    if rules != old_gr:
        print_to_pte5(f'Грамматика после удаления длинных правил:\n{grammar_to_str(grammar)}')
    else:
        print_to_pte5('Длинных правил не обнаружено!')
    print(grammar)
    grammar_before_del_empty_rules = grammar
    grammar = grammar.remove_empty_rules()
    if grammar != grammar_before_del_empty_rules:
        print_to_pte5('Удаление пустых правил...')
        print_to_pte5('Грамматика после удаления пустых правил:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Пустых правил не обнаружено!')
    grammar_before_remove_chain_rulse = grammar
    grammar = grammar.remove_chain_rules()
    if grammar != grammar_before_remove_chain_rulse:
        print_to_pte5('Удаление цепных правил...')
        print_to_pte5('Грамматика после удаления цепных правил:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Цепных правил не обнаружено!')
    child_free = grammar.find_child_free_non_terms()
    if child_free:
        print_to_pte5(f'Обнаружены бесплодные нетерминальные символы: {", ".join(child_free)}')
        grammar = grammar.remove_rules(child_free)
        print_to_pte5('Грамматика после удаления бесплодных символов:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Бесплодных нетерминальных символов не обнаружено!')
    #
    old_gr = grammar
    grammar, rules = grammar.remove_trash()
    #
    fill_form_with_grammar_h(grammar)
    if grammar != old_gr:
        print_to_pte5(f'Уберём ситуации, когда в правиле встречаются несколько терминалов')
        print_to_pte5('Грамматика после изменения:\n' + grammar_to_str(grammar))
    else:
        print_to_pte5('Повторений нескольких нетерминальных символов в правилах не обнаружено!')
    h_sequences = grammar.make_chains(window.ui.spinBox.value(), window.ui.spinBox_2.value())
    h_sequences = [seq if seq else get_lambda() for seq in h_sequences]
    window.ui.plainTextEdit_4.setPlainText('\n'.join(sorted(h_sequences)))
    print_to_pte5('{: ^200}'.format('Окончено приведение канонической грамматики к бинарной грамматике Хомского'))
    print('grammar - ', grammar)
    #tree_create(grammar)
    return grammar


def get_changes(grammar: Grammar, current, next):
    if len(next) < len(current):
        return "λ"
    for i, ch in enumerate(current[::-1]):
        i = len(current) - i - 1
        print(next[i: i + len(next) - len(current) + 1])
        print('get_changes()', grammar.VN)
        if ch in grammar.VN:
            return next[i: i + len(next) - len(current) + 1]


def get_right_vertex(gr: Grammar, tree):
    if not tree.children and tree.data in gr.VN:
        return tree
    for vert in tree.children[::-1]:
        gr, v = get_right_vertex(gr, vert)
        if v:
            return gr, v

'''
def tree_create(grammar):
    QMessageBox.information(MainWindow(), "Статус", "Готовится простроение дерева, пожалуйста подождите...")
    choise = window.ui.lineEdit_4.text()
    choise = 'cbbb'
    print(grammar)
    grammar = read_grammar_from_form_h(grammar.VN)
    print(grammar)
    if not choise:
        return
    print(choise)
    gr = grammar
    tree = Vertex(choise[0])
    print(tree)
    for curr, next in zip(choise, choise[1:]):
        print('curr - ' + curr)
        print('next - ' + next)
        changes = get_changes(grammar, curr, next)
        grm, v = get_right_vertex(grammar, tree)
        print(v)
        v.children = list(map(Vertex, changes))
    print('Start')
    gt = GraphicalTree(Vertex(choise))
    gt.start()
    print('END')
    ...'''


if __name__ == '__main__':
    #
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()
    grammar = False
    update_start_s()
    window.ui.action.connect(SIGNAL('triggered()'), save_to_file)
    window.ui.action_2.connect(SIGNAL('triggered()'), open_grammar_file)
    window.ui.action_3.connect(
        SIGNAL('triggered()'), lambda: QMessageBox.information(window, "Задание", __theme__)
    )
    window.ui.action_4.connect(
        SIGNAL('triggered()'), lambda: QMessageBox.information(window, "Автор", 'ImVengeance\n16 вариант\nИП - 712')
    )
    grammar = window.ui.pushButton.connect(SIGNAL('clicked()'), start)
    #grammar = holmsky(grammar)
    print(grammar)
    window.ui.pushButton_4.connect(SIGNAL('clicked()'), window.ui.plainTextEdit_5.clear)
    #
    grammar: Grammar = read_grammar_from_form()
    #window.ui.pushButton_3.connect(SIGNAL('clicked()'), lambda: tree_create(grammar))
    window.ui.pushButton_2.connect(SIGNAL('clicked()'), compare_chains)

    #grammar = calculate()
    exit(app.exec_())
