import sys
import paramiko
import os

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)
    return client

def run_command(cmd, verbose=True):
    client = get_ssh_client()
    try:
        if verbose:
            print(f">>> [VPS EXEC]: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        out_lines = []
        for line in iter(stdout.readline, ""):
            out_lines.append(line)
            if verbose:
                try:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                except Exception:
                    sys.stdout.write(line.encode('ascii', errors='replace').decode('ascii'))
                    sys.stdout.flush()
        exit_code = stdout.channel.recv_exit_status()
        client.close()
        return exit_code, "".join(out_lines)
    except Exception as e:
        client.close()
        raise e

def upload_file(local_path, remote_path):
    client = get_ssh_client()
    sftp = client.open_sftp()
    print(f"[*] Upload: {local_path} -> {remote_path}...")
    sftp.put(local_path, remote_path)
    sftp.close()
    client.close()
    print("[+] Upload finalizado com sucesso!")

def download_file(remote_path, local_path):
    client = get_ssh_client()
    sftp = client.open_sftp()
    print(f"[*] Download: {remote_path} -> {local_path}...")
    sftp.get(remote_path, local_path)
    sftp.close()
    client.close()
    print("[+] Download finalizado com sucesso!")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    if len(sys.argv) > 2 and sys.argv[1] == "--upload":
        upload_file(sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2 and sys.argv[1] == "--download":
        download_file(sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        code, out = run_command(cmd)
        sys.exit(code)
    else:
        code, out = run_command("uname -a && docker --version && free -h")
        sys.exit(code)
