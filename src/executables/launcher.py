# launcher.py
import os
import socket
import subprocess
import sys
import time
import webbrowser


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port: int = s.getsockname()[1]  # type: ignore[assignment]
    s.close()
    return port


def main() -> int:
    port = _free_port()

    # Handle both development and PyInstaller packaged environments
    if getattr(sys, "frozen", False):
        # Running in a PyInstaller bundle
        base_path: str = getattr(sys, "_MEIPASS", "")  # type: ignore[attr-defined]
        app_path = os.path.join(base_path, "executables", "youtube_app.py")
        # Add base_path to PYTHONPATH so imports work
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        if pythonpath:
            env["PYTHONPATH"] = f"{base_path}:{pythonpath}"
        else:
            env["PYTHONPATH"] = base_path
    else:
        # Running in development
        app_path = os.path.join(os.path.dirname(__file__), "youtube_app.py")
        env = os.environ.copy()
        # Add src directory to PYTHONPATH
        src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pythonpath = env.get("PYTHONPATH", "")
        if pythonpath:
            env["PYTHONPATH"] = f"{src_path}:{pythonpath}"
        else:
            env["PYTHONPATH"] = src_path

    # Start Streamlit
    # We intentionally don't use 'with' here because we need to keep the process
    # running and manage its lifecycle manually (wait for it, handle interrupts)
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.address=127.0.0.1",
            f"--server.port={port}",
            "--server.headless=true",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        env=env,
    )

    # Give it a moment then open browser
    time.sleep(1.0)
    webbrowser.open(f"http://127.0.0.1:{port}")

    # Keep the launcher alive while Streamlit runs
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
