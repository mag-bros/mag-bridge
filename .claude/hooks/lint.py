import subprocess


def main():
    # The directories you want to ruthlessly format
    targets = ["src", "tests", "mcp"]

    # 1. Ruff natively understands directories
    subprocess.run(["ruff", "check", "--fix", *targets], capture_output=True)
    subprocess.run(["ruff", "format", *targets], capture_output=True)

    # 2. Prettier requires glob patterns to match specific extensions recursively
    prettier_targets = [f"{dir}/**/*.{{js,ts,json,md}}" for dir in targets]
    subprocess.run(["npx", "prettier", "--write", *prettier_targets], capture_output=True)


if __name__ == "__main__":
    main()
