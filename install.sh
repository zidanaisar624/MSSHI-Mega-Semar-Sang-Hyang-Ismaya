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
light_mode=0
low_ram=0
resource_profile=
install_dir=
hermes_home_opt=
target_dir=
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
        --light) light_mode=1 ;;
        --low-ram) low_ram=1 ;;
        --resource-profile) resource_profile=${2:?--resource-profile requires auto/light/normal}; shift ;;
        --install-dir) install_dir=${2:?--install-dir requires a path}; shift ;;
        --hermes-home) hermes_home_opt=${2:?--hermes-home requires a path}; shift ;;
        --target-dir) target_dir=${2:?--target-dir requires a path}; shift ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
    esac
    shift
done

if [ "$yes_mode" -eq 0 ] && [ "$no_setup" -eq 0 ] && [ -t 0 ]; then
    if [ "$light_mode" -eq 0 ] && [ "$low_ram" -eq 0 ] && [ -z "$resource_profile" ]; then
        printf '\n=== Pilihan Mode Instalasi MSSHI ===\n'
        printf '  1. Standar / Lengkap (Full Build)\n'
        printf '  2. Mode Hemat RAM 4 GB (Light Build <= 50 MB + Low-RAM Mode)\n'
        printf 'Pilih mode instalasi [1/2, Enter=1]: '
        read -r ed_pick || ed_pick=1
        if [ "$ed_pick" = "2" ]; then
            light_mode=1
            low_ram=1
        fi
    fi
    if [ -z "$install_dir" ]; then
        default_install=${MSSHI_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/msshi}
        printf 'Folder instalasi MSSHI (bebas ke direktori mana saja) [%s]: ' "$default_install"
        read -r picked_dir || picked_dir=
        if [ -n "$picked_dir" ]; then
            install_dir=$picked_dir
        fi
    fi
    if [ -z "$hermes_home_opt" ] && [ -z "${HERMES_HOME:-}" ]; then
        printf 'Folder data Hermes / HERMES_HOME (Enter=otomatis adaptif, atau ketik path bebas): '
        read -r picked_hermes || picked_hermes=
        if [ -n "$picked_hermes" ]; then
            hermes_home_opt=$picked_hermes
        fi
    fi
fi

if [ -n "$install_dir" ]; then
    MSSHI_HOME=$install_dir
    export MSSHI_HOME
fi
if [ -n "$hermes_home_opt" ]; then
    HERMES_HOME=$hermes_home_opt
    export HERMES_HOME
fi

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
    if [ "$light_mode" -eq 1 ]; then
        if ! (
            GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_LFS_SKIP_SMUDGE=1 \
                git -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= \
                clone --template= --depth 1 --filter=blob:none --no-tags --no-checkout --sparse --branch main -- "$repository" "$source_dir" &&
            git -C "$source_dir" sparse-checkout set --no-cone \
                /scripts/ /configs/ /skills/ /hermes_plugins/ /templates/ /business-sage/ \
                /docs/manuals/pdf_catalog.json /optional/manifest.json /VERSION.json /CHANGELOG.md \
                /LICENSE /CREDITS.md /THIRD_PARTY_NOTICES.md /SKILL.md /INSTALL_FOR_AGENTS.md \
                /package.json /install.ps1 /install.sh /MULAI_DI_SINI_PEMULA.bat \
                /MULAI_SKRIPSI_DRAG_AND_DROP.bat /UPDATE_OTOMATIS_KE_V3.bat &&
            git -C "$source_dir" checkout --quiet HEAD
        ); then
            rm -rf -- "$source_dir"
            GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_LFS_SKIP_SMUDGE=1 \
                git -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= \
                clone --template= --depth 1 --no-tags --branch main -- "$repository" "$source_dir"
        fi
    else
        GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_LFS_SKIP_SMUDGE=1 \
            git -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= \
            clone --template= --depth 1 --no-tags --branch main -- "$repository" "$source_dir"
    fi
fi

cli=$source_dir/scripts/msshi_cli.py
if [ ! -f "$cli" ]; then
    printf 'This source does not contain the Stage 2 CLI yet.\n' >&2
    exit 1
fi
set -- bootstrap
if [ "$no_path" -eq 1 ]; then set -- "$@" --no-path; fi
if [ "$light_mode" -eq 1 ]; then set -- "$@" --light; fi
if [ "$no_pdf" -eq 1 ] || { [ "$light_mode" -eq 1 ] && [ "$download_pdf" -eq 0 ]; }; then set -- "$@" --no-pdf; fi
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
    if [ -n "$target_dir" ]; then set -- "$@" --target-dir "$target_dir"; fi
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
    if [ "$low_ram" -eq 1 ]; then set -- "$@" --low-ram; fi
    if [ -n "$resource_profile" ]; then set -- "$@" --resource-profile "$resource_profile"; fi
    if [ "$download_pdf" -eq 1 ]; then set -- "$@" --download-pdf; fi
    if [ "$no_pdf" -eq 1 ] || { [ "$light_mode" -eq 1 ] && [ "$download_pdf" -eq 0 ]; }; then set -- "$@" --no-pdf; fi
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
