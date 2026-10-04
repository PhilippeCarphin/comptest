#
# This file tests
# - generation of completion from an argparse.ArgumentParser
# - tests the generated completion
#
echo "Generating completion"
bin/compget --generate-completion x > comp.sh
echo "Testing completion"
results="$(bin/compget --load-bash-completion --init-files comp.sh -- 'compget ')"
expected="--bash-command
--color
--debug
--generate-completion
--init-files
--interact
--load-bash-completion
--log-file
--verbose-ps4
--xtrace-log
-d
-f
-l
-x"

if [[ "${results}" != "${expected}" ]] ; then
    echo "FAILED:"
    echo "EXPECTED:"
    echo "${expected}" | sed 's/^/    /'
    echo "GOT:"
    echo "${result}" | sed 's/^/    /'
else
    echo "PASSED"
fi
