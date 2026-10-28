import argparse
import textwrap
import sys

def completion_from_parser(parser: argparse.ArgumentParser, namespace: str, commands: list[str], with_descriptions=False, advanced=False):
    if isinstance(commands, str):
        raise TypeError("Argument commands must be a sequence, not 'str'")
    CompletionGenerator(parser=parser, namespace=namespace, commands=commands, with_descriptions=with_descriptions, advanced=advanced).generate()

class CompletionGenerator():
    def __init__(self, parser, namespace, commands, with_descriptions=False, advanced=False):
        self.parser = parser
        self.namespace = namespace
        self.arg_actions = []
        self.flag_actions = []
        self.posarg_actions = []
        self.get_action()
        self.commands = commands
        self.with_descriptions = with_descriptions
        self.advanced = advanced

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
            else:
                print(f"Unhandled type {type(a)}", file=sys.stderr)

    def generate(self):
        print("#!/usr/bin/env bash # hint for editors\n")
        self.print_arrays()
        self.print_main_function()
        if self.with_descriptions:
            self.print_description_adder()
        self.print_generic_options()
        self.print_value_function_stubs()
        if self.advanced:
            self.print_get_completed_option()
        print(f"complete -F _{self.namespace} {' '.join(self.commands)}")

    def print_arrays(self):
        print(textwrap.dedent( f"""
            _{self.namespace}_arg_options=({' '.join((' '.join(o.option_strings) for o in self.arg_actions))})
            _{self.namespace}_flag_options=({' '.join((' '.join(o.option_strings) for o in self.flag_actions))})
        """))
        if self.with_descriptions:
            self.print_description_array()

    def print_main_function(self):
        print(textwrap.dedent(f"""
            _{self.namespace}(){{
            local cur prev words cword
            _init_completion || return
        """))

        if self.advanced:
            print(f"    local opt=$(_{self.namespace}_get_completed_option)")
            print(f"    case $opt in")
        else:
            print("    case $prev in")

        for opt in self.arg_actions:
            case = '|'.join(opt.option_strings)
            print(f"        {case}) _{self.namespace}_{opt.dest}_values ;;")

        print(f"        *) _{self.namespace}_options ;;")
        print("    esac")

        if self.with_descriptions:
            print(f"\n    _{self.namespace}_add_descriptions")

        print("}")

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
        print(textwrap.dedent(f"""
            _{self.namespace}_add_descriptions(){{

                if (( ${{#COMPREPLY[@]}} <= 1 )) ; then
                    return
                fi

                local max_comp=0
                for c in "${{COMPREPLY[@]}}" ; do
                    if ((${{#c}} > max_comp)) ; then
                        max_comp=${{#c}}
                    fi
                done

                local i max_desc_len=$((COLUMNS - max_comp - 4))
                if ((max_desc_len < 10 )) ; then
                    return 1
                fi

                for((i=0;i<${{#COMPREPLY[@]}};i++));do
                    local comp=${{COMPREPLY[i]}}
                    local desc=${{_{self.namespace}_descriptions[$comp]}}

                    if [[ -z ${{desc}} ]] ; then
                        continue
                    fi
                    if ((${{#desc}} > max_desc_len)) ; then
                        desc=${{desc:0:$((max_desc_len-1))}}
                        desc+='…'
                    fi
                    printf -v COMPREPLY[i] "%-${{max_comp}}s (%s)" "${{comp}}" "${{desc}}"
                done
            }}
            """))


    def print_description_array(self):
        print(f"declare -gA _{self.namespace}_descriptions=(")
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
        print(")")

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
