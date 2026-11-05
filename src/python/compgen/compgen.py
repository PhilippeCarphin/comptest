import argparse
import textwrap
import sys

# TODO: WITH FUNCTIONS: If false, just have COMPREPLY=($(compgen ...)) directly
# in the case statements and don't create _X_{opt}_values functions.
def completion_from_parser(parser: argparse.ArgumentParser, namespace: str, commands: list[str], with_functions=True, with_descriptions=False, advanced=False):
    if isinstance(commands, str):
        raise TypeError("Argument commands must be a sequence, not 'str'")
    CompletionGenerator(parser=parser, namespace=namespace, commands=commands, with_descriptions=with_descriptions, advanced=advanced).generate()

# This could be more useful if it worked with some kind of spec
# Consider an already written completion, no python command with an argparse parser.
# Then we run a spec through this and for each thing in the spec
# we try the completion, and now we have a file that tests everything
# and we can get to work modifying it and having fun.
def analyze(p: argparse.ArgumentParser, test=False, save_test=False):
    """ Print info on the parser.  This is mainly a demonstration of how get
    info from a given parser or tests"""
    tests = []
    bingbong = []
    base_actions = []
    subparser_action = None
    for a in p._actions:
        if isinstance(a, argparse._SubParsersAction):
            subparser_action = a
        else:
            base_actions.append(a)

    print(f"Toplevel options")
    base_option_strings = []
    for a in base_actions:
        base_option_strings.extend(a.option_strings)
        print(f"    {a.option_strings}: {a.help}")
        for os in a.option_strings:
            bingbong.append((f"chef {os} ", c.get_comp(f"chef {os} ")))
            if a.choices:
                tests.append(f"test('chef {os} ', {a.choices})")

    if subparser_action:
        subcommands = list(subparser_action.choices.keys())
        for ca in subparser_action._choices_actions:
            print(f"Subcommand {ca.dest}: {ca.help}")

        bingbong.append(("chef ", c.get_comp("chef ")))
        tests.append(f"test('chef ', {[*subcommands, *base_option_strings]})")
        for subcommand, sp in subparser_action.choices.items():
            print(f"    {subcommand}")
            arguments = []
            for a in sp._actions:
                print(f"        {a.option_strings}: {a.choices or ''} {a.help}")
                arguments.extend(a.option_strings)
                if a.choices:
                    bingbong.append((f"chef {os} ", c.get_comp(f"chef {os} ")))
                    for os in a.option_strings:
                        tests.append(f"test('chef {subcommand} {os} ', {a.choices})")
            tests.append(f"test('chef {subcommand} ', {arguments})")

    for t in tests:
        print(t)

    for x, y in bingbong:
        print(f"test('{x}', {y})")


# TODO: Never decided to handle positional arguments

class CompletionGenerator():
    def __init__(self, parser, namespace, commands, with_functions=False, with_descriptions=False, advanced=False, parent=None):
        self.parser = parser
        self.namespace = namespace
        self.arg_actions = []
        self.flag_actions = []
        self.posarg_actions = []
        self.subparser_action = None
        self.subgenerartors = None
        self.commands = commands
        self.with_descriptions = with_descriptions
        self.advanced = advanced
        self.with_functions = with_functions
        self.parent = parent

        self.get_action()
        if self.subparser_action:
            self.subgenerators = []
            for choice, sp in self.subparser_action.choices.items():
                self.subgenerators.append(CompletionGenerator(sp, f'{self.namespace}_{choice}', [], with_descriptions=with_descriptions, with_functions=with_functions, advanced=advanced, parent=self))

    def get_action(self):
        for a in self.parser._actions:
            if isinstance(a, argparse._StoreTrueAction) \
               or isinstance(a, argparse._HelpAction):
                self.flag_actions.append(a)
            elif isinstance(a, argparse._StoreAction):
                if not a.option_strings:
                    self.posarg_actions.append(a)
                else:
                    self.arg_actions.append(a)
            elif isinstance(a, argparse._SubParsersAction):
                self.subparser_action = a
            else:
                print(f"Unhandled type {type(a)}", file=sys.stderr)

    def generate(self):
        print("#!/usr/bin/env bash # hint for editors")
        self.print_arrays()
        print()
        self.print_main_function()
        if self.subparser_action:
            for subgen in self.subgenerators:
                subgen.print_main_function()
        if self.with_descriptions:
            self.print_description_adder()
        if self.with_functions:
            self.print_value_function_stubs()
            for subgen in self.subgenerators:
                subgen.print_value_function_stubs()
        if self.advanced:
            self.print_get_completed_option()
        if self.commands:
            print(f"complete -F _{self.namespace} {' '.join(self.commands)}")

    def print_arrays(self):
        print(textwrap.dedent( f"""
            _{self.namespace}_arg_options=({' '.join((' '.join(o.option_strings) for o in self.arg_actions))})
            _{self.namespace}_flag_options=({' '.join((' '.join(o.option_strings) for o in self.flag_actions))})
            _{self.namespace}_options=("${{_{self.namespace}_arg_options[@]}}" "${{_{self.namespace}_flag_options[@]}}")"""))
        if self.subparser_action:
            print(f"_{self.namespace}_subcommands=({' '.join(self.subparser_action.choices.keys())})")
        if self.with_descriptions:
            self.print_description_array()

        if self.subparser_action:
            for subgen in self.subgenerators:
                subgen.print_arrays()

    def print_main_function(self):
        print(f"_{self.namespace}(){{", end='')
        print(textwrap.indent(textwrap.dedent(f"""
            local cur prev words cword
            _init_completion || return"""), '    '))

        sc_indent = '    '
        if self.subparser_action is not None:
            self.get_subcommand()

            print("    if [[ -z ${subcommand} ]] ; then", end='')
            sc_indent = '        '

        self.option_case_statement(indent=sc_indent)
        if self.with_descriptions and not self.parent:
            print(f"\n{sc_indent}_{self.namespace}_add_descriptions_by_ref _{self.namespace}_descriptions")

        if self.subparser_action:
            print("    else")
            print(f"        _{self.namespace}_${{subcommand}}")
            print(f"        _{self.namespace}_add_descriptions_by_ref _{self.namespace}_${{subcommand}}_descriptions")
            print("    fi")

        print("}\n")

    def get_subcommand(self):
        print(textwrap.indent(textwrap.dedent("""
            local subcommand
            for((i=0;i<${#words[@]};i++)) ; do
                case ${words[i]} in"""), '    '))

        for a in self.parser._actions:
            if isinstance(a, argparse._StoreTrueAction):
                print(f"            {'|'.join(a.option_strings)}) ;;")
            elif isinstance(a, argparse._StoreAction):
                print(f"            {'|'.join(a.option_strings)}) ((i++)) ;;")

        print(f"            {'|'.join(self.subparser_action.choices.keys())}) subcommand=${{words[i]}} ; break ;;")
        print(f"        esac")
        print(f"    done")
        print()

    def option_case_statement(self, indent=''):
        if self.advanced:
            print(f"\n{indent}local opt=$(_{self.namespace}_get_completed_option)")
            print(f"{indent}case $opt in")
        else:
            print(f"\n{indent}case $prev in")

        for a in self.arg_actions:
            # Usually the long option is given first and the short on second
            # Putting the short option first (reversed(...)) will make for
            # nicer alignment.
            case = '|'.join(reversed(a.option_strings))
            if self.with_functions:
                print(f"    {indent}{case}) _{self.namespace}_{a.dest}_values ;;")
            else:
                print(f"    {indent}{case}) ", end='')
                if a.choices:
                    print(f"COMPREPLY+=($(compgen -W \"{' '.join(a.choices)}\" -- \"${{cur}}\")) ;;")
                else:
                    print(f" : TODO ;;")

        if self.subparser_action:
            print(f"    {indent}*) COMPREPLY=($(compgen -W \"${{_{self.namespace}_subcommands[*]}} ${{_{self.namespace}_options[*]}}\" -- \"${{cur}}\")) ;;")
        else:
            print(f"    {indent}*) COMPREPLY=($(compgen -W \"${{_{self.namespace}_options[*]}}\" -- \"${{cur}}\")) ;;")

        print(f"{indent}esac")

    def print_value_function_stubs(self):
        for opt in self.arg_actions:
            print(f"_{self.namespace}_{opt.dest}_values(){{")
            if opt.choices:
                print(f"    COMPREPLY=($(compgen -W '{' '.join(opt.choices)}' -- \"${{cur}}\"))")
            else:
                print(f"    : TODO")
            print("}\n")

    def print_generic_options(self):
        print(f"_{self.namespace}_options(){{")
        print(f"    COMPREPLY+=(")
        print(f"        $(compgen -W \"${{_{self.namespace}_arg_options[*]}}\" -- \"${{cur}}\")")
        print(f"        $(compgen -W \"${{_{self.namespace}_flag_options[*]}}\" -- \"${{cur}}\")")
        print(f"    )")
        print("}")

    def print_description_adder(self):
        print(f"_{self.namespace}_add_descriptions_by_ref(){{")
        print(textwrap.indent(textwrap.dedent("""
                local -n _descriptions=$1

                if (( ${#COMPREPLY[@]} <= 1 )) ; then
                    return
                fi

                local max_comp=0
                for c in "${COMPREPLY[@]}" ; do
                    if ((${#c} > max_comp)) ; then
                        max_comp=${#c}
                    fi
                done

                local i max_desc_len=$((COLUMNS - max_comp - 4))
                if ((max_desc_len < 10 )) ; then
                    return 1
                fi

                for((i=0;i<${#COMPREPLY[@]};i++));do
                    local comp=${COMPREPLY[i]}
                    local desc=${_descriptions[$comp]}

                    if [[ -z ${desc} ]] ; then
                        continue
                    fi
                    if ((${#desc} > max_desc_len)) ; then
                        desc=${desc:0:$((max_desc_len-1))}
                        desc+='…'
                    fi
                    printf -v COMPREPLY[i] "%-${max_comp}s (%s)" "${comp}" "${desc}"
                done
            """), '    '))
        print("}")


    def print_description_array(self):
        print(f"declare -gA _{self.namespace}_descriptions=(")
        self.print_description_array_elements(self.parser)
        if self.subparser_action:
            for ca in self.subparser_action._choices_actions:
                print(f"    [{ca.dest}]=\"subcommand: {ca.help}\"")
        print(")")

    def print_description_array_elements(self, p):
        for a in self.parser._actions:
            if not a.help:
                continue
            if isinstance(a, argparse._StoreTrueAction):
                desc=f"flag: {a.help}"
            elif isinstance(a, argparse._StoreAction):
                desc=f"arg: {a.help}"
            else:
                desc=f" - : {a.help}"
            for s in a.option_strings:
                print(f"    [{s}]=\"{desc}\"")
    #
    # WIP: Can be improved to make nicer code.  Even though this code is
    # generated my goal with this package is to generate exemplary completion
    # code since the goal is to generate a script that I will continue myself
    #
    # For each option, check "am I completing arguments for that option" which
    # means
    # - with word = ${words[cword-i]} for i in range(a.nargs+1)
    #   - if word is the option: we are completing the option
    #   - if along the way we encounter a word that starts with '-' that
    #     is not the option, we are not completing that option.
    #
    # If we try to do this with one for-loop, then the cases to check at
    # each iteration will change so although it is repetitive code, we'll never
    # have to write it.
    #
    def print_get_completed_option(self):
        print(f"_{self.namespace}_get_completed_option(){{")
        print(f"    if [[ ${{cur}} == -* ]] ; then return ; fi")
        for a in self.parser._actions:
            if a.nargs is None:
                # Options that take one argument
                print(f"    case ${{prev}} in {'|'.join(a.option_strings)}) echo {a.option_strings[0]} ; return ;; esac")
            elif a.nargs == "*":
                print(textwrap.indent(textwrap.dedent(f"""
                for ((i=0;i<=${{#words[@]}};i++)) ; do
                    word=${{words[cword-i]}}
                    case $word in {'|'.join(a.option_strings)}) echo "{a.option_strings[0]}" ; return ;; esac
                    if [[ $word == -* ]] ; then break ; fi
                done"""), "    "))
            elif a.nargs == "+":
                print(textwrap.indent(textwrap.dedent(f"""
                for ((i=0;i<=${{#words[@]}};i++)) ; do
                    word=${{words[cword-i]}}
                    case $word in {'|'.join(a.option_strings)}) echo "{a.option_strings[0]}" ; return ;; esac
                    if [[ $word == -* ]] ; then break ; fi
                done"""), "    "))
            elif a.nargs == 0:
                pass # nothing to do, flag options don't have args
            elif isinstance(a.nargs, int):
                print(textwrap.indent(textwrap.dedent(f"""
                for ((i=0;i<={a.nargs};i++)) ; do
                    word=${{words[cword-i]}}
                    case $word in {'|'.join(a.option_strings)}) echo "{a.option_strings[0]}" ; return ;; esac
                    if [[ $word == -* ]] ; then break ; fi
                done"""), "    "))
        print("}")
