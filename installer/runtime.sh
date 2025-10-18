#!/bin/bash
SPINNER_CMD="print_fill --char '.' --amount 999 --sleep 0.1 --rainbow"
PIP=$(shell command -v pip3 2>/dev/null || command -v pip || command -v py)

function run_with_spinner() {
	local PF ST

	if [ -t 1 ] && [ -w /dev/tty ]; then
		# open FD 3 to the terminal
		exec 3>/dev/tty
		# start spinner in background
		eval "$SPINNER_CMD" >&3 &
		PF=$!

		# trap Ctrl-C / termination and cleanup spinner
		trap 'cleanup_spinner' INT TERM EXIT
	fi

	# run main command
	"$@"
	ST=$?

	cleanup_spinner() {
		if [ -n "${PF-}" ] && kill -0 "$PF" 2>/dev/null; then
			kill "$PF" 2>/dev/null
			wait "$PF" 2>/dev/null || true
			printf "\r\033[K" >&3
			exec 3>&-
		fi
		trap - INT TERM EXIT
		return $ST
	}

	cleanup_spinner
	return $ST
}

function hint() {
	local code="$1"
	case "$code" in
	"NO_VENV")
		log --error "⚙️  <color=grey>.venv</> missing - setup required"
		copy_to_clipboard "make venv"
		log --info "✨ <color=olive>Fix</>: <color=green>make venv</>"
		log --info "${VERBOSE_CHAR} <color=grey>Command copied to your clipboard</>"
		;;
	"NO_PYCLEAN")
		log --error "❌ 'pyclean' not found in current environment."
		copy_to_clipboard "make pip"
		log --info "✨ Fix: <color=blue>make pip</> (inside your venv)."
		;;
	"GENERIC")
		log --error "⚠️ Unknown error occurred."
		copy_to_clipboard "make install"
		log --info "✨ Fix: <color=blue>make install</> or <color=grey>make reset</>."
		;;
	esac
}

copy_to_clipboard() {
	local data="$1" b64
	b64=$(printf %s "$data" | base64 | tr -d '\n')
	if [ -n "$TMUX" ]; then
		printf '\ePtmux;\e\e]52;c;%s\a\e\\' "$b64"
	else
		printf '\e]52;c;%s\a' "$b64"
	fi
	command -v pbcopy >/dev/null && { printf %s "$data" | pbcopy; }
	command -v wl-copy >/dev/null && { printf %s "$data" | wl-copy; }
	command -v xclip >/dev/null && { printf %s "$data" | xclip -selection clipboard; }
	command -v xsel >/dev/null && { printf %s "$data" | xsel --clipboard --input; }
}
