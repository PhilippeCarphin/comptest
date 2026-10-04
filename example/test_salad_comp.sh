#!/usr/bin/env bash
root=$(cd -P $(dirname $0)/.. && pwd)
export XDG_DATA_DIRS=${root}/example/share
compare_arrays(){
    local -n _a=$1
    local -n _b=$2
    if (( ${#_a[@]} != ${#_b[@]} )) ; then
        echo "Different sizes" >&2
        return 1
    fi

    for((i=0;i<${#_a[@]};i++)); do
        if [[ ${_a[i]} != ${_b[i]} ]] ; then
            echo "Elements at index $i differ: ${1}[$i]:'${_a[i]}', ${2}[$i]:'${_b[i]}'" >&2
            return 1
        fi
    done
}
t(){
    local cmd=$1
    local expected=($2)
    results=($(${root}/bin/compget --load-bash-completion "$1"))
    if ! compare_arrays results expected ; then
        echo "Test failed for cmd = '${cmd}'" >2
        return 1
    else
        echo "Completion for '${cmd}' produced the correct candidates: '${results[*]}'"
    fi
}

if ! t 'salad -' '-fruit -vegetable' ; then
    exit 1
fi

if ! t 'salad -fruit ' 'apple apricot banana cherry' ; then
    exit 1
fi

if ! t 'salad -vegetable ' 'carrot celery onion potato' ; then
    exit 1
fi
