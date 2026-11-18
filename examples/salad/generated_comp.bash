#!/usr/bin/env bash # hint for editors

_salad_arg_options=(--dressing -d --seasoning -s --vegetable -v --fruit -f)
_salad_flag_options=(-h --help)
_salad_options=("${_salad_arg_options[@]}" "${_salad_flag_options[@]}")

_salad(){
    local cur prev words cword completed_option posarg_number=0
    _init_completion || return

    _salad_get_completed_option
    case $completed_option in
        -d|--dressing) COMPREPLY+=($(compgen -W "italian ranch" -- "${cur}")) ;;
        -s|--seasoning) COMPREPLY+=($(compgen -W "salt pepper" -- "${cur}")) ;;
        -v|--vegetable) COMPREPLY+=($(compgen -W "celery carrot broccoli potato" -- "${cur}")) ;;
        -f|--fruit) COMPREPLY+=($(compgen -W "apple apricot banana cherry" -- "${cur}")) ;;
        *) COMPREPLY=($(compgen -W "${_salad_subcommands[*]} ${_salad_options[*]}" -- "${cur}")) ;;
    esac
}


# First check if ${prev} is an option that takes exactly one argument, then
# starting from the end, read backwards.  If word[cword-i] is an option that
# can take $i or more args, then that is the option we are completing.  However
# as soon as we encounter an argument that starts with '-' that is not one
# of these options, everything stops.  This is how argparse works also.
#
# It is technically possible to have aguments.
# - Choice arguments with choices that start with '-',
# - Using the --opt=-value
# but these possibilities are not handled.
_salad_get_completed_option(){
    for((i=subcommand_index+1;i<cword;i++)) ; do
        local nargs=0 type=''
        local word=${words[i]}
        case ${word} in
            -h|--help) : nargs=0 ;;
            --dressing|-d) nargs=1 ;;
            --seasoning|-s|--vegetable|-v) nargs=${cword} ; type='*' ;;
            --fruit|-f) nargs=3 ;;
            *) ((posarg_number++)) ;;
        esac
        for((x=1;x<=nargs;x++)) ; do
            if ((i+x >= cword)) ; then
                completed_option=${word}
                return
            elif [[ ${type} == '*' ]] && [[ ${words[i+x]} == -* ]] ; then
                break
            fi
        done
        i=$((i+x-1))
    done
}
complete -F _salad salad
