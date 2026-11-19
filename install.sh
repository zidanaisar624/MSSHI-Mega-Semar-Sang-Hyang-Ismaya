#!/bin/sh
set -eu

repository=https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git
source_dir=
no_setup=0
no_path=0
download_pdf=0
no_pdf=0
pdf_version=
pdf_dest=
mode=
platform=
academic_project=
academic_level=
academic_topic=
academic_deadline=
academic_campus_guideline=
preferred_name=
default_bot=
yes_mode=0
kat_mode=
stage_auto_trim=0
install_steel=0
connect_services=
browser=
browser_profile_label=
browser_account_label=
connect_apps=
connect_bots=
connect_targets=
with_rea=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --source-dir) source_dir=${2:?--source-dir requires a path}; shift ;;
        --no-setup) no_setup=1 ;;
        --no-path) no_path=1 ;;
        --download-pdf) download_pdf=1 ;;
        --no-pdf) no_pdf=1 ;;
        --pdf-version) pdf_version=${2:?--pdf-version requires a version}; shift ;;
        --pdf-dest) pdf_dest=${2:?--pdf-dest requires a path}; shift ;;
        --academic-project) academic_project=${2:?--academic-project requires a path}; shift ;;
        --academic-level) academic_level=${2-}; shift ;;
        --academic-topic) academic_topic=${2-}; shift ;;
        --academic-deadline) academic_deadline=${2-}; shift ;;
        --academic-campus-guideline) academic_campus_guideline=${2-}; shift ;;
        --preferred-name) preferred_name=${2-}; shift ;;
        --mode) mode=${2:?--mode requires a value}; shift ;;
        --platform) platform=${2:?--platform requires a value}; shift ;;
        --default-bot) default_bot=${2:?--default-bot requires a value}; shift ;;
        --yes|-y) yes_mode=1 ;;
        --kat-mode) kat_mode=${2:?--kat-mode requires a value}; shift ;;
        --stage-auto-trim) stage_auto_trim=1 ;;
        --install-steel) install_steel=1 ;; # Deprecated compatibility no-op.
        --connect-services) connect_services=${2:?--connect-services requires a value}; shift ;;
        --browser) browser=${2:?--browser requires chrome/edge/firefox/none}; shift ;;
        --browser-profile-label) browser_profile_label=${2-}; shift ;;
        --browser-account-label) browser_account_label=${2-}; shift ;;
        --connect-apps) connect_apps=${2:?--connect-apps requires a value}; shift ;;
        --connect-bots) connect_bots=${2:?--connect-bots requires a value}; shift ;;
        --connect-targets) connect_targets=${2:?--connect-targets requires a value}; shift ;;
        --with-rea) with_rea=1 ;;
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
if [ "$no_pdf" -eq 1 ]; then set -- "$@" --no-pdf; fi
if [ -n "$pdf_version" ]; then set -- "$@" --pdf-version "$pdf_version"; fi
if [ -n "$pdf_dest" ]; then set -- "$@" --pdf-dest "$pdf_dest"; fi
"$python" -B -X utf8 "$cli" "$@"
if [ "$no_setup" -eq 0 ]; then
    set -- setup
    if [ -n "$mode" ]; then set -- "$@" --mode "$mode"; fi
    if [ -n "$academic_project" ]; then set -- "$@" --academic-project "$academic_project"; fi
    if [ -n "$academic_level" ]; then set -- "$@" --academic-level "$academic_level"; fi
    if [ -n "$academic_topic" ]; then set -- "$@" --academic-topic "$academic_topic"; fi
    if [ -n "$academic_deadline" ]; then set -- "$@" --academic-deadline "$academic_deadline"; fi
    if [ -n "$academic_campus_guideline" ]; then set -- "$@" --academic-campus-guideline "$academic_campus_guideline"; fi
    if [ -n "$preferred_name" ]; then set -- "$@" --preferred-name "$preferred_name"; fi
    if [ -n "$platform" ]; then set -- "$@" --platform "$platform"; fi
    if [ -n "$default_bot" ]; then set -- "$@" --default-bot "$default_bot"; fi
    if [ "$yes_mode" -eq 1 ]; then set -- "$@" --yes; fi
    if [ -n "$kat_mode" ]; then set -- "$@" --kat-mode "$kat_mode"; fi
    if [ "$stage_auto_trim" -eq 1 ]; then set -- "$@" --stage-auto-trim; fi
    if [ "$install_steel" -eq 1 ]; then set -- "$@" --install-steel; fi
    if [ -n "$connect_services" ]; then set -- "$@" --connect-services "$connect_services"; fi
    if [ -n "$browser" ]; then set -- "$@" --browser "$browser"; fi
    if [ -n "$browser_profile_label" ]; then set -- "$@" --browser-profile-label "$browser_profile_label"; fi
    if [ -n "$browser_account_label" ]; then set -- "$@" --browser-account-label "$browser_account_label"; fi
    if [ -n "$connect_apps" ]; then set -- "$@" --connect-apps "$connect_apps"; fi
    if [ -n "$connect_bots" ]; then set -- "$@" --connect-bots "$connect_bots"; fi
    if [ -n "$connect_targets" ]; then set -- "$@" --connect-targets "$connect_targets"; fi
    if [ "$with_rea" -eq 1 ]; then set -- "$@" --with-rea; fi
    if [ "$download_pdf" -eq 1 ]; then set -- "$@" --download-pdf; fi
    if [ "$no_pdf" -eq 1 ]; then set -- "$@" --no-pdf; fi
    if [ -n "$pdf_version" ]; then set -- "$@" --pdf-version "$pdf_version"; fi
    if [ -n "$pdf_dest" ]; then set -- "$@" --pdf-dest "$pdf_dest"; fi
    if [ "$yes_mode" -eq 1 ] || [ -t 0 ]; then
        "$python" -B -X utf8 "$cli" "$@"
    elif ( : </dev/tty ) 2>/dev/null; then
        "$python" -B -X utf8 "$cli" "$@" </dev/tty
    else
        printf 'Run msshi setup from an interactive terminal.\n'
    fi
fi
