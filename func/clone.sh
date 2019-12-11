# vim: filetype=sh

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

function clone() {
    cd $(~/bin/clone $1)
}
