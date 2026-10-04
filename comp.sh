
    _compget_arg_options=(--init-files -f --bash-command -d --log-file --xtrace-log --color)
    _compget_flag_options=(--debug --load-bash-completion -l -x --verbose-ps4 --interact --generate-completion)
    _compget(){
        local cur prev words cword
        _init_completion || return
        case $prev in

            --init-files|-f) _compget_init_files_values ;;
            --bash-command) _compget_bash_command_values ;;
            -d) _compget_d_values ;;
            --log-file) _compget_log_file_values ;;
            --xtrace-log) _compget_xtrace_log_values ;;
            --color) COMPREPLY=($(compgen -W 'red green blue' -- "${cur}")) ; return ;;
            *) COMPREPLY=($(compgen -W '${_compget_arg_options[*]} ${_compget_flag_options[*]}' -- "${cur}"))
        esac
    }
_compget_init_files_values(){
    : TODO
}

_compget_bash_command_values(){
    : TODO
}

_compget_d_values(){
    : TODO
}

_compget_log_file_values(){
    : TODO
}

_compget_xtrace_log_values(){
    : TODO
}

complete -F _compget compget
