#!/usr/bin/env bash # hint for editors

_chef_arg_options=(-F)
_chef_flag_options=(-h --help --debug -d)
_chef_options=("${_chef_arg_options[@]}" "${_chef_flag_options[@]}")
_chef_subcommands=(cook prep)
declare -gA _chef_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [--debug]="Turn on debug logging"
    [-d]="Turn on debug logging"
    [-F]="Config file"
    [cook]="subcommand: Cook food"
    [prep]="subcommand: Prep food"
)

_chef_cook_arg_options=(--vessel -v --temp -t --bowl -b)
_chef_cook_flag_options=(-h --help)
_chef_cook_options=("${_chef_cook_arg_options[@]}" "${_chef_cook_flag_options[@]}")
declare -gA _chef_cook_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [--vessel]="The vessel to cook in"
    [-v]="The vessel to cook in"
    [--temp]="Temperature to cook at"
    [-t]="Temperature to cook at"
    [--bowl]="The bowl to empty into the cooking vessel"
    [-b]="The bowl to empty into the cooking vessel"
)

_chef_prep_arg_options=(--bowl -b --vegetable -v)
_chef_prep_flag_options=(-h --help)
_chef_prep_options=("${_chef_prep_arg_options[@]}" "${_chef_prep_flag_options[@]}")
declare -gA _chef_prep_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [--bowl]="The bowl to put prepped vegetables into"
    [-b]="The bowl to put prepped vegetables into"
    [--vegetable]="The vegetable to prep"
    [-v]="The vegetable to prep"
)

_chef(){
    local cur prev words cword completed_option posarg_number=0
    _init_completion || return

    local subcommand subcommand_index=${subcommand_index:-0}
    for((i=subcommand_index+1;i<${#words[@]};i++)) ; do
        case ${words[i]} in
            -F) i=$((i+2)) ;;
            cook|prep) subcommand=${words[i]}; subcommand_index=$i ; break ;;
        esac
    done

    if [[ -z ${subcommand} ]] ; then
        _chef_get_completed_option
        case $completed_option in
            -F)  : TODO ;;
            *) COMPREPLY=($(compgen -W "${_chef_subcommands[*]} ${_chef_options[*]}" -- "${cur}")) ;;
        esac

        _chef_add_descriptions_by_ref _chef_descriptions
    else
        _chef_${subcommand}
        _chef_add_descriptions_by_ref _chef_${subcommand}_descriptions
    fi
}

_chef_cook(){
    local completed_option posarg_number=0

    case $prev in
        -v|--vessel) COMPREPLY+=($(compgen -W "pan pot" -- "${cur}")) ;;
        -t|--temp) COMPREPLY+=($(compgen -W "high medium low" -- "${cur}")) ;;
        -b|--bowl) COMPREPLY+=($(compgen -W "large small" -- "${cur}")) ;;
        *) COMPREPLY=($(compgen -W "${_chef_cook_subcommands[*]} ${_chef_cook_options[*]}" -- "${cur}")) ;;
    esac
}

_chef_prep(){
    local completed_option posarg_number=0

    _chef_prep_get_completed_option
    case $completed_option in
        -b|--bowl) COMPREPLY+=($(compgen -W "large small" -- "${cur}")) ;;
        -v|--vegetable) COMPREPLY+=($(compgen -W "onion carrot potato" -- "${cur}")) ;;
        *) COMPREPLY=($(compgen -W "${_chef_prep_subcommands[*]} ${_chef_prep_options[*]}" -- "${cur}")) ;;
    esac
}

_chef_add_descriptions_by_ref(){

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
_chef_get_completed_option(){
    for((i=subcommand_index+1;i<cword;i++)) ; do
        local nargs=0 type=''
        local word=${words[i]}
        case ${word} in
            -h|--help|--debug|-d) : nargs=0 ;;
            -F) nargs=2 ;;
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
_chef_prep_get_completed_option(){
    for((i=subcommand_index+1;i<cword;i++)) ; do
        local nargs=0 type=''
        local word=${words[i]}
        case ${word} in
            -h|--help) : nargs=0 ;;
            --vegetable|-v) nargs=1 ;;
            --bowl|-b) nargs=${cword} ; type='*' ;;
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
complete -F _chef chef
