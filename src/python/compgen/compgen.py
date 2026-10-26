import argparse
import textwrap
import sys

def completion_from_parser(parser: argparse.ArgumentParser, namespace: str, commands: list[str]):
    if isinstance(commands, str):
        raise TypeError("Argument commands must be a sequence, not 'str'")
    CompletionGenerator(parser=parser, namespace=namespace, commands=commands).generate()

class CompletionGenerator():
    def __init__(self, parser, namespace, commands):
        self.parser = parser
        self.namespace = namespace
        self.arg_actions = []
        self.flag_actions = []
        self.posarg_actions = []
        self.get_action()
        self.commands = commands

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
        self.print_arrays()
        self.print_main_function()
        self.print_generic_options()
        self.print_value_function_stubs()
        print(f"complete -F _{self.namespace} {' '.join(self.commands)}")

    def print_arrays(self):
        print(textwrap.dedent( f"""
            _{self.namespace}_arg_options=({' '.join((' '.join(o.option_strings) for o in self.arg_actions))})
            _{self.namespace}_flag_options=({' '.join((' '.join(o.option_strings) for o in self.flag_actions))})
        """))

    def print_main_function(self):
        print(textwrap.dedent(f"""
            _{self.namespace}(){{
            local cur prev words cword
            _init_completion || return
        """))

        print("    case $prev in")
        for opt in self.arg_actions:
            case = '|'.join(opt.option_strings)
            print(f"        {case}) _{self.namespace}_{opt.dest}_values ;;")

        print(f"        *) _{self.namespace}_options ;;")
        print("    esac")
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
