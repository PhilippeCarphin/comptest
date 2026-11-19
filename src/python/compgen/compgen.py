import argparse
import textwrap
import pathlib
import sys

# TODO: WITH FUNCTIONS: If false, just have COMPREPLY=($(compgen ...)) directly
# in the case statements and don't create _X_{opt}_values functions.
def completion_from_parser(parser: argparse.ArgumentParser, namespace: str, commands: list[str], with_functions=False, with_descriptions=False, advanced=False):
    if isinstance(commands, str):
        raise TypeError("Argument commands must be a sequence, not 'str'")
    CompletionGenerator(parser=parser, namespace=namespace, commands=commands, with_functions=with_functions, with_descriptions=with_descriptions).generate()

def analyze(p: argparse.ArgumentParser, test=False, indent=''):
    """ Print info on the parser.  This is mainly a demonstration of how get
    info from a given parser or tests"""
    if indent == '':
        print(textwrap.dedent("""
            import comptest
            import os
            import sys

            bash_comp = comptest.find_bash_completion()
            try:
                c = comptest.CompletionRunner(
                    init_files=[bash_comp, sys.argv[1]],
                )
            except RuntimeError as e:
                print(f"FAILURE: Init: {e}")
                raise SystemExit(1) from e
        """))

    tests = []
    base_actions = []
    subparser_action = None
    posarg_actions = []
    base_option_strings = []
    subcommands = []
    print(f"{indent}\033[4;37m\033[1;33m{p.prog}\033[0m", file=sys.stderr)
    for a in p._actions:
        if isinstance(a, argparse._SubParsersAction):
            subparser_action = a
            subcommands = a.choices.keys()
        elif a.option_strings:
            base_actions.append(a)
            base_option_strings.extend(a.option_strings)
        else:
            posarg_actions.append(a)

    if posarg_actions:
        extra_arg = ''
        for i,a in enumerate(posarg_actions):
            print(f"  {indent}\033[36m{a.dest}\033[0m (posarg {i}): {a.help}", file=sys.stderr)
            if a.choices:
                print(f"c.test('{p.prog}{extra_arg} ', {[*base_option_strings, *a.choices]})")
            extra_arg += f' posart_{i}_value'
    else:
        print(f"c.test('{p.prog} ', {[*subcommands, *base_option_strings]})")

    for a in base_actions:
        print(f"  {indent}{a.option_strings}: {a.help}", file=sys.stderr)
        if a.choices:
            for o in a.option_strings:
                print(f"c.test('{p.prog} {o} ', {a.choices})")

    if subparser_action:
        for ca in subparser_action._choices_actions:
            print(f"  {indent}\033[33m{ca.dest}\033[0m (subcommand): {ca.help}",file=sys.stderr)
        for subcommand, sp in subparser_action.choices.items():
            analyze(sp, test=True, indent=indent+'    ')

    if indent == '':
        print("\nsys.exit(1 if c.has_failed_tests else 0)")

# TODO: Never decided to handle positional arguments

class CompletionGenerator():
    def __init__(self, parser, namespace, commands, with_functions=False, with_descriptions=False, parent=None):
        self.parser = parser
        self.namespace = namespace
        self.arg_actions = []
        self.flag_actions = []
        self.posarg_actions = []
        self.options_with_more_args = []
        self.options_with_one_arg = []
        self.options_with_fixed_nargs = []
        self.subparser_action = None
        self.subgenerators = []
        self.commands = commands
        self.with_descriptions = with_descriptions
        self.with_functions = with_functions
        self.parent = parent

        self.description_adder = f"_{self.namespace}_add_descriptions_by_ref" if self.parent is None else self.parent.description_adder
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
                continue
            else:
                print(f"Unhandled type {type(a)}", file=sys.stderr)

            if a.nargs in ['+', '*']:
                self.options_with_more_args.append(a)
            elif a.nargs is None and a.option_strings:
                self.options_with_one_arg.append(a)
            elif isinstance(a.nargs, int) and a.nargs > 0:
                self.options_with_fixed_nargs.append(a)

        self.advanced = (self.options_with_more_args or self.options_with_fixed_nargs)

        if self.subparser_action:
            for choice, sp in self.subparser_action.choices.items():
                id_choice = choice.replace('-','_')
                self.subgenerators.append(CompletionGenerator(
                    parser=sp,
                    namespace=f'{self.namespace}_{id_choice}',
                    commands=[],
                    with_descriptions=with_descriptions,
                    with_functions=with_functions,
                    parent=self)
                )

    def generate(self):
        print("#!/usr/bin/env bash # hint for editors")
        self.print_arrays()
        print()
        self.print_main_function()
        if self.with_descriptions:
            self.print_description_adder()
        if self.with_functions:
            self.print_value_function_stubs()

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
        if self.parent is None:
            print(textwrap.indent(textwrap.dedent(f"""
                local cur prev words cword completed_option posarg_number=0
                _init_completion || return"""), '    '))
        else:
            print(f"\n    local completed_option posarg_number=0")

        sc_indent = '    '
        if self.subparser_action is not None:
            self.get_subcommand()

            print("    if [[ -z ${subcommand} ]] ; then", end='')
            sc_indent = '        '

        self.option_case_statement(indent=sc_indent)
        if self.with_descriptions and not self.parent:
            print(f"\n{sc_indent}{self.description_adder} _{self.namespace}_descriptions")

        if self.subparser_action:
            print("    else")
            print(f"        _{self.namespace}_${{subcommand}}")
            print(f"        {self.description_adder} _{self.namespace}_${{subcommand}}_descriptions")
            print("    fi")

        print("}\n")

        for sg in self.subgenerators:
            sg.print_main_function()

    def get_subcommand(self):
        print(textwrap.indent(textwrap.dedent("""
            local subcommand subcommand_index=${subcommand_index:-0}
            for((i=subcommand_index+1;i<${#words[@]};i++)) ; do
                case ${words[i]} in"""), '    '))

        if self.advanced:
            for a in self.options_with_one_arg:
                print(f"            {'|'.join(a.option_strings)}) ((i++)) ;;")
            for a in self.options_with_fixed_nargs:
                print(f"            {'|'.join(a.option_strings)}) i=$((i+{a.nargs})) ;;")
            if self.options_with_more_args:
                print(f"            {'|'.join(['|'.join(a.option_strings) for a in self.options_with_more_args])})")
                print(f"                while [[ ${{words[i+1]}} != -* ]] ; do ((i++)) ; done ;;")


        print(f"            {'|'.join(self.subparser_action.choices.keys())}) subcommand=${{words[i]}}; subcommand_index=$i ; break ;;")
        print(f"        esac")
        print(f"    done")
        print()

    def option_case_statement(self, indent=''):
        if self.advanced:
            print(f"\n{indent}_{self.namespace}_get_completed_option")
            print(f"{indent}case $completed_option in")
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
                elif a.type is pathlib.Path:
                    print(f"_filedir ;;")
                else:
                    print(f" : TODO ;;")

        if self.subparser_action or not self.posarg_actions:
            print(f"    {indent}*) COMPREPLY=($(compgen -W \"${{_{self.namespace}_subcommands[*]}} ${{_{self.namespace}_options[*]}}\" -- \"${{cur}}\")) ;;")
        else:
            if self.posarg_actions:

                print(f"    {indent}'') COMPREPLY=($(compgen -W \"${{_{self.namespace}_options[*]}}\" -- \"${{cur}}\"))")
                print(f"        {indent}case ${{posarg_number}} in")
                for i,a in enumerate(self.posarg_actions):
                    print(f"            {indent}{i}) COMPREPLY+=($(compgen -W \"{' '.join(a.choices)}\" -- \"${{cur}}\")) ;;")
                print(f"    {indent}    esac ;;")

        print(f"{indent}esac")


    def print_value_function_stubs(self):
        for opt in self.arg_actions:
            print(f"_{self.namespace}_{opt.dest}_values(){{")
            if opt.choices:
                print(f"    COMPREPLY=($(compgen -W '{' '.join(opt.choices)}' -- \"${{cur}}\"))")
            elif opt.type is pathlib.Path:
                print(f"    _filedir")
            else:
                print(f"    : TODO")
            print("}\n")
        for subgen in self.subgenerators:
            subgen.print_value_function_stubs()

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
            for s in a.option_strings:
                print(f"    [{s}]=\"{a.help}\"")
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
        if self.advanced:
            print(textwrap.dedent("""
                # First check if ${prev} is an option that takes exactly one argument, then
                # starting from the end, read backwards.  If word[cword-i] is an option that
                # can take $i or more args, then that is the option we are completing.  However
                # as soon as we encounter an argument that starts with '-' that is not one
                # of these options, everything stops.  This is how argparse works also.
                #
                # It is technically possible to have aguments.
                # - Choice arguments with choices that start with '-',
                # - Using the --opt=-value
                # but these possibilities are not handled."""))

            opts_with_more_args = []
            opts_with_fixed_nargs = []
            opts_with_single_arg = []
            opts_with_zero_args = []
            actions_with_fixed_nargs = []
            for a in self.parser._actions:
                if a.nargs is None and a.option_strings:
                    # a.nargs is None for options that take exactly one argument and for subcommands
                    # which we want to leave out
                    opts_with_single_arg.extend(a.option_strings)
                elif a.nargs in ['*', '+']:
                    opts_with_more_args.extend(a.option_strings)
                elif isinstance(a.nargs, int) and a.nargs > 0:
                    actions_with_fixed_nargs.append(a)
                    opts_with_fixed_nargs.extend(a.option_strings)
                elif a.nargs == 0:
                    opts_with_zero_args.extend(a.option_strings)
                    pass # nothing to do, flag options don't have args

            print(f"_{self.namespace}_get_completed_option(){{")
            print(f"    for((i=subcommand_index+1;i<cword;i++)) ; do")
            print(f"        local nargs=0 type=''")
            print(f"        local word=${{words[i]}}")
            print(f"        case ${{word}} in")
            if opts_with_zero_args:
                print(f"            {'|'.join(opts_with_zero_args)}) : nargs=0 ;;")
            if opts_with_single_arg:
                print(f"            {'|'.join(opts_with_single_arg)}) nargs=1 ;;")
            if opts_with_more_args:
                print(f"            {'|'.join(opts_with_more_args)}) nargs=${{cword}} ; type='*' ;;")
            for a in actions_with_fixed_nargs:
                print(f"            {'|'.join(a.option_strings)}) nargs={a.nargs} ;;")
            print(f"            *) ((posarg_number++)) ;;")
            print(f"        esac")

            print(f"        for((x=1;x<=nargs;x++)) ; do")
            print(f"            if ((i+x >= cword)) ; then")
            print(f"                completed_option=${{word}}")
            print(f"                return")
            print(f"            elif [[ ${{type}} == '*' ]] && [[ ${{words[i+x]}} == -* ]] ; then")
            print(f"                break")
            print(f"            fi")
            print(f"        done")
            print(f"        i=$((i+x-1))")
            print("    done")

            print("}")

        for subgen in self.subgenerators:
            subgen.print_get_completed_option()
