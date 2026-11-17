#!/usr/bin/env bash # hint for editors

_git_arg_options=(-F)
_git_flag_options=(-h --help --debug -d)
_git_options=("${_git_arg_options[@]}" "${_git_flag_options[@]}")
_git_subcommands=(remote worktree)
declare -gA _git_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [--debug]="Turn on debug logging"
    [-d]="Turn on debug logging"
    [-F]="Config file"
    [remote]="subcommand: Do remote stuff"
    [worktree]="subcommand: worktree stuff"
)

_git_remote_arg_options=()
_git_remote_flag_options=(-h --help)
_git_remote_options=("${_git_remote_arg_options[@]}" "${_git_remote_flag_options[@]}")
_git_remote_subcommands=(add remove)
declare -gA _git_remote_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [add]="subcommand: add a remote"
    [remove]="subcommand: Remove a remote"
)

_git_remote_add_arg_options=(--name)
_git_remote_add_flag_options=(-h --help)
_git_remote_add_options=("${_git_remote_add_arg_options[@]}" "${_git_remote_add_flag_options[@]}")
declare -gA _git_remote_add_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
)

_git_remote_remove_arg_options=(--name --force)
_git_remote_remove_flag_options=(-h --help)
_git_remote_remove_options=("${_git_remote_remove_arg_options[@]}" "${_git_remote_remove_flag_options[@]}")
declare -gA _git_remote_remove_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [--name]="Remove an existing remote"
    [--force]="Remove even if something"
)

_git_worktree_arg_options=()
_git_worktree_flag_options=(-h --help)
_git_worktree_options=("${_git_worktree_arg_options[@]}" "${_git_worktree_flag_options[@]}")
_git_worktree_subcommands=(add delete)
declare -gA _git_worktree_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
    [add]="subcommand: Add a worktree"
    [delete]="subcommand: Add a worktree"
)

_git_worktree_add_arg_options=(--name)
_git_worktree_add_flag_options=(-h --help)
_git_worktree_add_options=("${_git_worktree_add_arg_options[@]}" "${_git_worktree_add_flag_options[@]}")
declare -gA _git_worktree_add_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
)

_git_worktree_delete_arg_options=(--name)
_git_worktree_delete_flag_options=(-h --help)
_git_worktree_delete_options=("${_git_worktree_delete_arg_options[@]}" "${_git_worktree_delete_flag_options[@]}")
declare -gA _git_worktree_delete_descriptions=(
    [-h]="show this help message and exit"
    [--help]="show this help message and exit"
)

_git(){
    local cur prev words cword
    _init_completion || return

    local subcommand subcommand_index=${subcommand_index:-0}
    for((i=subcommand_index+1;i<${#words[@]};i++)) ; do
        case ${words[i]} in
            --debug|-d) ;;
            -F) ((i++)) ;;
            remote|worktree) subcommand=${words[i]}; subcommand_index=$i ; break ;;
        esac
    done

    if [[ -z ${subcommand} ]] ; then
        case $prev in
            -F) _git_F_values ;;
            *) COMPREPLY=($(compgen -W "${_git_subcommands[*]} ${_git_options[*]}" -- "${cur}")) ;;
        esac

        _git_add_descriptions_by_ref _git_descriptions
    else
        _git_${subcommand}
        _git_add_descriptions_by_ref _git_${subcommand}_descriptions
    fi
}

_git_remote(){
    local cur prev words cword
    _init_completion || return

    local subcommand subcommand_index=${subcommand_index:-0}
    for((i=subcommand_index+1;i<${#words[@]};i++)) ; do
        case ${words[i]} in
            add|remove) subcommand=${words[i]}; subcommand_index=$i ; break ;;
        esac
    done

    if [[ -z ${subcommand} ]] ; then
        case $prev in
            *) COMPREPLY=($(compgen -W "${_git_remote_subcommands[*]} ${_git_remote_options[*]}" -- "${cur}")) ;;
        esac
    else
        _git_remote_${subcommand}
        _git_add_descriptions_by_ref _git_remote_${subcommand}_descriptions
    fi
}

_git_remote_add(){
    local cur prev words cword
    _init_completion || return

    case $prev in
        --name) _git_remote_add_name_values ;;
        *) COMPREPLY=($(compgen -W "${_git_remote_add_options[*]}" -- "${cur}")) ;;
    esac
}

_git_remote_remove(){
    local cur prev words cword
    _init_completion || return

    local opt=$(_git_remote_remove_get_completed_option)
    case $opt in
        --name) _git_remote_remove_name_values ;;
        --force) _git_remote_remove_force_values ;;
        *) COMPREPLY=($(compgen -W "${_git_remote_remove_options[*]}" -- "${cur}")) ;;
    esac
}

_git_worktree(){
    local cur prev words cword
    _init_completion || return

    local subcommand subcommand_index=${subcommand_index:-0}
    for((i=subcommand_index+1;i<${#words[@]};i++)) ; do
        case ${words[i]} in
            add|delete) subcommand=${words[i]}; subcommand_index=$i ; break ;;
        esac
    done

    if [[ -z ${subcommand} ]] ; then
        case $prev in
            *) COMPREPLY=($(compgen -W "${_git_worktree_subcommands[*]} ${_git_worktree_options[*]}" -- "${cur}")) ;;
        esac
    else
        _git_worktree_${subcommand}
        _git_add_descriptions_by_ref _git_worktree_${subcommand}_descriptions
    fi
}

_git_worktree_add(){
    local cur prev words cword
    _init_completion || return

    case $prev in
        --name) _git_worktree_add_name_values ;;
        *) COMPREPLY=($(compgen -W "${_git_worktree_add_options[*]}" -- "${cur}")) ;;
    esac
}

_git_worktree_delete(){
    local cur prev words cword
    _init_completion || return

    case $prev in
        --name) _git_worktree_delete_name_values ;;
        *) COMPREPLY=($(compgen -W "${_git_worktree_delete_options[*]}" -- "${cur}")) ;;
    esac
}

_git_add_descriptions_by_ref(){

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
_git_F_values(){
    COMPREPLY=($(compgen -W 'main-F x' -- "${cur}"))
}

_git_remote_add_name_values(){
    COMPREPLY=($(compgen -W 'remote-add--name origin upstream' -- "${cur}"))
}

_git_remote_remove_name_values(){
    COMPREPLY=($(compgen -W 'remote-remove--name x' -- "${cur}"))
}

_git_remote_remove_force_values(){
    COMPREPLY=($(compgen -W 'remote-remove--force x' -- "${cur}"))
}

_git_worktree_add_name_values(){
    COMPREPLY=($(compgen -W 'worktree-add--name x' -- "${cur}"))
}

_git_worktree_delete_name_values(){
    COMPREPLY=($(compgen -W 'worktree-delete--name x' -- "${cur}"))
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
_git_remote_remove_get_completed_option(){
    case ${prev} in
        --force) echo "${prev}" ; return ;;
    esac
    for((i=0;i<${#words[@]}-${subcommand_index};i++)) ; do
        local word=${words[cword-i]}
        case ${word} in
            --name) if ((i<=3)) ; then echo "${word}" ; return ; fi ;;
            -*) break ;;
        esac
    done
}
complete -F _git git g
