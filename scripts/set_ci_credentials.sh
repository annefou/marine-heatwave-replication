#!/usr/bin/env bash
# Publish the local Copernicus Marine credentials to this repo's GitHub secrets,
# so ci.yml's pipeline smoke run can authenticate.
#
#   bash scripts/set_ci_credentials.sh              # set the secrets
#   bash scripts/set_ci_credentials.sh --dry-run    # check everything, set nothing
#
# The credential values are never printed, never written to a temporary file,
# and never placed on a command line (where `ps` would expose them). They are
# piped straight from the credentials file into `gh secret set`, which reads
# from stdin. The script reports field names and character counts only, so you
# can confirm it found the right things without seeing them.
#
# WHY TWO SECRETS RATHER THAN ONE ENCODED BLOB
# GitHub masks the exact string it is given wherever that string appears in a
# log. Store the username and password as themselves and GitHub masks the values
# that matter. Store a base64 copy of the credentials file instead and GitHub
# masks the blob, while the decoded username and password -- values it has never
# seen -- are not masked at all, so one `set -x` or library debug line prints
# them in the clear in a public repo's build log. Encoding is not encryption.
# See DOMAIN.md § Copernicus credentials in CI.

set -euo pipefail
set +x  # never trace: this script handles secret values

CRED_FILE="${COPERNICUSMARINE_CREDENTIALS_FILE:-$HOME/.copernicusmarine/.copernicusmarine-credentials}"
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

die() { echo "error: $*" >&2; exit 1; }

# --- preconditions ----------------------------------------------------------

[ -r "$CRED_FILE" ] || die "no readable credentials file at $CRED_FILE
  Run 'copernicusmarine login' first, or set COPERNICUSMARINE_CREDENTIALS_FILE."

command -v gh >/dev/null || die "the GitHub CLI 'gh' is not installed."

gh auth status >/dev/null 2>&1 || die "gh is not authenticated. Run 'gh auth login'."

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)" \
  || die "not inside a GitHub repository that gh can resolve."

# --- read the credentials ---------------------------------------------------

# copernicusmarine stores the file base64-encoded, but has used plain INI in
# other versions. Accept either rather than assuming, and never echo the result.
decoded_credentials() {
  local raw decoded
  raw="$(cat "$CRED_FILE")"
  if decoded="$(printf '%s' "$raw" | base64 -d 2>/dev/null)" \
     && [[ "$decoded" == *username=* ]]; then
    printf '%s\n' "$decoded"
  elif [[ "$raw" == *username=* ]]; then
    printf '%s\n' "$raw"
  else
    return 1
  fi
}

decoded_credentials >/dev/null 2>&1 \
  || die "could not find username=/password= in $CRED_FILE (base64 or plain).
  The file format may have changed; inspect it yourself rather than trusting this script."

# Extract one field. Output goes straight to a pipe — never to a variable that a
# later trace or error message could expose.
field() {
  decoded_credentials | sed -n "s/^$1=//p" | head -1 | tr -d '\r\n'
}

# --- verify both fields are present, by length only -------------------------

user_len="$(field username | wc -c | tr -d ' ')"
pass_len="$(field password | wc -c | tr -d ' ')"

[ "$user_len" -gt 0 ] || die "username is empty in $CRED_FILE"
[ "$pass_len" -gt 0 ] || die "password is empty in $CRED_FILE"

echo "credentials file : $CRED_FILE"
echo "  username       : $user_len chars"
echo "  password       : $pass_len chars"
echo "target repo      : $REPO"
echo

if [ "$DRY_RUN" = true ]; then
  echo "--dry-run: would set COPERNICUSMARINE_SERVICE_USERNAME and"
  echo "           COPERNICUSMARINE_SERVICE_PASSWORD on $REPO"
  exit 0
fi

# --- set the secrets --------------------------------------------------------

# `gh secret set NAME` reads the value from stdin when --body is omitted, so the
# secret never appears as a process argument.
field username | gh secret set COPERNICUSMARINE_SERVICE_USERNAME --repo "$REPO"
field password | gh secret set COPERNICUSMARINE_SERVICE_PASSWORD --repo "$REPO"

echo
echo "Set both secrets on $REPO."
echo "Verify with: gh secret list --repo $REPO"
echo "CI's smoke run will authenticate on the next push or PR; until then it"
echo "skips with a warning rather than passing green unverified."
