import subprocess


def main():
    # The directories you want to ruthlessly format
    ruff_targets = ["src", "tests", ".claude/scripts"]
    prettier_targets_dirs = ["src", "tests", "security"]

    # 1. Ruff natively understands directories
    subprocess.run(["ruff", "check", "--fix", *ruff_targets], capture_output=True)
    subprocess.run(["ruff", "format", *ruff_targets], capture_output=True)

    # 2. Prettier requires glob patterns to match specific extensions recursively
    prettier_targets = [f"{d}/**/*.{{js,ts,json,md}}" for d in prettier_targets_dirs]
    subprocess.run(["npx", "prettier", "--write", *prettier_targets], capture_output=True)


if __name__ == "__main__":
    main()
