#!/usr/bin/env bash
_cmd(){
    COMPREPLY=($(compgen -W "red green blue" -- "${COMP_WORDS[COMP_CWORD]}"))
    if [[ -n "${TO_PRINT}" ]] ; then
        printf "${TO_PRINT}"
    fi
}

export -f _cmd

do-it(){
    local title="${1}" ; shift
    printf "\033[1;37m[${title}] Running \033[36m$*"
    if [[ -n "${TO_PRINT}" ]] ; then
        printf "\033[1;37m with error message: %q" "${TO_PRINT}"
    fi
    printf "\033[0m\n"
    "$@"
}

do-it "Match 1 normal" compget --init-commands "complete -F _cmd cmd" -- 'cmd '

# Match 2 normal:
do-it "Match 2 normal" compget --init-commands "complete -F _cmd cmd" -- 'cmd b'

# Match 3 Normal:
export TO_PRINT=$'ERROR\n'
do-it "Match 3 normal" compget --init-commands "complete -F _cmd cmd" -- 'cmd b'

# Bad error messages: No candidates, no \n's in error message
export TO_PRINT=$'ERROR'
do-it "Match 2 abnormal" compget --init-commands "complete -F _cmd cmd" -- 'cmd yel'

# Bad error message: Starts with \n and we have multiple candidates
export TO_PRINT=$'\nERROR'
do-it "Match 1 abnormal" compget --init-commands "complete -F _cmd cmd" -- 'cmd '

# Bad error message: Starts with \n and multiple candidates
# Note: the \n after the error produces
# | $ cmd 
# | ERROR
# |
# | blue
# | green
# | red
# | $ cmd
# which gets sorted by compget after doing 'strip()' so we get an empty line
# in our candidates.
export TO_PRINT=$'\nERROR\n'
do-it "Match 1 abnormal" compget --init-commands "complete -F _cmd cmd" -- 'cmd '

#
# get_comp match numbers:
# In all cases we
# - Type cmd consume the echoed CMD with expect_exact
#   our 'self.bash.before' will start with whatever is output after that
# - We press TAB
# - Some output may or may not happen
# - We type YAYBOOYAYBOO
#
# 0. Example session:
#
#                          v Match starting point (^)
#    1 | @PS1@ cmd --color 
#    2 | red
#    3 | green
#    4 | blue
#    5 | @PS1@ cmd --color YAYBOOYAYBOO
#                                      ^ Match end ($)
#
#    We type 'cmd --color '.  We consume it and now matching and before start
#    from [].
#
#    We press TAB which is not echoed but causes multiple completions to be
#    printed and causes BASH to re-print our PS1 and our command.
#
#    After completions are produced, we type YAYBOOYAYBOO.
#
#    What we look for is line #5.  That's our match and what is before is
#    our completions so our completions are self.bash.before.strip().splitlines().
#
# 1. Example session:
#
#                           v Match starting point
#    1 | @PS1@ cmd --colour YAYBOOYAYBOO
#                                       ^ Match end ($)
#
#    We type our command, press TAB (and nothing happens) and type YAYBOOYAYBOO
#    so we match YAYBOOYAYBOO from the starting point.
#
# 2. Example session (cmd = 'cmd --color bl')
#
#                            v Match starting point (^)
#    1 | @PS1@ cmd --color blue YAYBOOYAYBOO
#                                           ^ Match end ($)
#
#    We type our command and consume it to set our starting point, we press TAB
#    and since there is only one candidate, the only thing that gets added is
#    the rest of that candidate and a space gets added (unless `compopt -o
#    nospace`), we then type our YAYBOOYAYBOO.
#
#    What we match is 'starting point, a match group of non-backslash-r
#    characters followed by YAYBOOYAYBOO
#
#    In this case, self.bash.before is empty because our match is everything
#    that was added.
#
# 3. Outpute from  the execution of our completion function will typically cause
#    output on the first line some characters to appear on the first line.
#    Let's say that the compltion function gets possible colors from a file like
#    ~/.config/cmd/colors.txt, that this file doesn't exist but the writer of
#    the completion function forgot to account for that:
#
#                          v Match starting point (^)
#    1 | @PS1@ cmd --color cat: ~/.config/cmd/colors.txt: No such file or directory
#    2 | YAYBOOYAYBOO
#
#    So if we have a non-backslash-r character at the start of the region *and*
#    our YAYBOOYAYBOO is not on the first line, then we have error messages.
#
#    If YAYBOOYAYBOO had been on the first line, then we would have matched
#    case 2.
#
#    Case 3 relies on two things:
#    ============================
#    - Output does not begin with \n
#    - Output has at least one \n.
#
#    For a completion that produces no candidates but does `printf "ERROR"`
#
#    1 | @PS1 cmd --color yelERRORYAYBOOYAYBOO
#
#    this will match case 2 as if the completion of 'yel' was 'yelERROR'
#
#    For a completion that produces one candidate but does `printf "\nERROR\n"`
#
#    1 | @PS1 cmd --color bl
#    2 | ERROR
#    3 | ueYAYBOOYAYBOO
#
#    then we will not match any case and will hang.
#
#    And if a completion produces multiple candidates but does `printf "\nERROR\n"`
#                          v Match starting point (^)
#    1 | @PS1@ cmd --color 
#    2 | ERROR
#    3 | red
#    4 | green
#    5 | blue
#    6 | @PS1@ cmd --color YAYBOOYAYBOO
#                                      ^ Match end ($)
#    We can't tell where "ERROR" came from, is it a completion or output from
#    the completion function.  Same for `printf "\nERROR"
#
#                          v Match starting point (^)
#    1 | @PS1@ cmd --color 
#    2 | ERROR
#    3 | red
#    3 | green
#    4 | blue
#    5 | @PS1@ cmd --color YAYBOOYAYBOO
#                                      ^ Match end ($)
#
#    It produces the same result because BASH prints multiple completion candidates
#    below the cursor.

