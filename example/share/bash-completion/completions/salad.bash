_salad(){
    local cur prev words cword
    _init_completion || return

    case ${prev} in
        -fruit)
            COMPREPLY=($(compgen -W "apple apricot banana cherry" -- "${cur}"))
            ;;
        -vegetable)
            COMPREPLY=($(compgen -W "onion potato carrot celery" -- "${cur}"))
            ;;
        *)
            COMPREPLY=($(compgen -W "-vegetable -fruit" -- "${cur}"))
            ;;
    esac
}

complete -F _salad salad
