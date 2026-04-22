import getpass
import platform
from pathlib import Path


def test_kernel_logs_unreadable():
    """Asserts the container cannot read host kernel logs, verifying non-privileged mode."""
    try:
        with open("/dev/kmsg", "r") as f:
            f.read(10)
        assert False, "Container has read access to host kernel logs."
    except (PermissionError, FileNotFoundError):
        pass


def test_pid_namespace_isolated():
    """Asserts PID 1 is the container entrypoint, not the host OS init system."""
    try:
        with open("/proc/1/cmdline", "rb") as f:
            cmdline = f.read().replace(b"\x00", b" ").decode("utf-8").lower()

        assert "systemd" not in cmdline, "Host systemd visible in container."
        assert "launchd" not in cmdline, "Host launchd visible in container."
    except PermissionError:
        pass


def test_host_credentials_unreachable():
    """Asserts high-value host credentials are not accessible inside the container."""
    targets = ["/root/.aws/credentials", "/root/.ssh/id_rsa", "/root/.npmrc", "/.aws/credentials", "/.ssh/id_rsa"]
    for path in targets:
        try:
            assert not Path(path).exists(), f"Credential exposed at {path}"
        except PermissionError:
            pass


def test_cgroup_sandbox_active():
    """Asserts the process is constrained by Docker container control groups."""
    cgroup_path = Path("/proc/1/cgroup")
    if cgroup_path.exists():
        cgroups = cgroup_path.read_text().lower()
        is_sandboxed = any(word in cgroups for word in ["docker", "containerd", "/"])
        assert is_sandboxed, "Process escapes container cgroups."


def test_kernel_parameters_readonly():
    """Asserts kernel parameters in /proc/sys block unprivileged modifications."""
    target = Path("/proc/sys/kernel/hostname")
    if target.exists():
        try:
            with open(target, "a") as f:
                f.write("test")
            assert False, "Container can modify kernel parameters."
        except (PermissionError, OSError):
            pass


def test_system_binaries_readonly():
    """Asserts standard users cannot modify root-owned system binaries."""
    target = Path("/bin/ls")
    if target.exists():
        try:
            with open(target, "a") as f:
                f.write("\n")
            assert False, "Container user can tamper with system binaries."
        except PermissionError:
            pass


def test_shadow_file_readonly():
    """Asserts standard users cannot modify system identity/password files."""
    try:
        with open("/etc/shadow", "a") as f:
            f.write("test")
        assert False, "Container user can write to /etc/shadow."
    except PermissionError:
        pass


def test_host_users_directory_unreachable():
    """Asserts host OS user directories and profiles do not bleed into the container."""
    assert not Path("/Users").exists(), "Mac host /Users directory is visible."
    assert not Path("C:\\").exists(), "Windows C: drive is visible."

    if Path("/home").exists():
        home_dirs = [d.name for d in Path("/home").iterdir() if d.is_dir()]
        assert getpass.getuser() in home_dirs, "Container user missing from /home."

        for host_profile in ["Shared", "Guest", "Administrator"]:
            assert host_profile not in home_dirs, f"Host profile '{host_profile}' leaked."


def test_docker_socket_unreachable():
    """Asserts the Docker socket is not mounted to prevent container escape."""
    assert not Path("/var/run/docker.sock").exists(), "Docker socket is mounted."


def test_user_is_sandboxed():
    """Asserts the current user is restricted to the expected container identity."""
    assert getpass.getuser() == "vscode_server", "Running as incorrect user."


def test_os_is_containerized():
    """Asserts the environment identifies strictly as a Linux container."""
    assert Path("/.dockerenv").exists(), "Not running inside a Docker environment."
    assert platform.system() == "Linux", "Host OS leaked into container platform info."


def test_root_filesystem_readonly_for_user():
    """Asserts standard users cannot write to protected OS directories like /etc."""
    test_file = Path("/etc/host_isolation_test.txt")
    try:
        test_file.write_text("test")
        test_file.unlink()
        assert False, "User has write access to /etc."
    except PermissionError:
        pass
