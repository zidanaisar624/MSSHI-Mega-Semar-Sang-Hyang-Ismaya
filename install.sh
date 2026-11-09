#!/bin/sh
set -eu

repository=https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git
source_dir=
no_setup=0
no_path=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --source-dir) source_dir=${2:?--source-dir requires a path}; shift ;;
        --no-setup) no_setup=1 ;;
        --no-path) no_path=1 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
    esac
    shift
done

python=
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
        python=$candidate
        break
    fi
done
if [ -z "$python" ]; then
    printf 'MSSHI requires Python 3.10 or newer.\n' >&2
    exit 1
fi

if [ -z "$source_dir" ]; then
    command -v git >/dev/null
    scratch=$(mktemp -d "${TMPDIR:-/tmp}/msshi-bootstrap.XXXXXXXX")
    trap 'rm -rf -- "$scratch"' EXIT
    source_dir=$scratch/repo
    GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_LFS_SKIP_SMUDGE=1 \
        git -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= \
        clone --template= --depth 1 --no-tags --branch main -- "$repository" "$source_dir"
fi

cli=$source_dir/scripts/msshi_cli.py
if [ ! -f "$cli" ]; then
    printf 'This source does not contain the Stage 2 CLI yet.\n' >&2
    exit 1
fi
set -- bootstrap
if [ "$no_path" -eq 1 ]; then set -- "$@" --no-path; fi
"$python" -B -X utf8 "$cli" "$@"
if [ "$no_setup" -eq 0 ]; then
    if [ -t 0 ]; then
        "$python" -B -X utf8 "$cli" setup
    elif ( : </dev/tty ) 2>/dev/null; then
        "$python" -B -X utf8 "$cli" setup </dev/tty
    else
        printf 'Run msshi setup from an interactive terminal.\n'
    fi
fi
