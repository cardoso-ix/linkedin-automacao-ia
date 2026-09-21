import os
import json
import sqlite3
import paramiko

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=25)

remote_script = r"""
import sqlite3, json, sys, subprocess

db_path = '/opt/linkedin-automation/n8n_data/database.sqlite'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Limpa registro anterior se houver
cur.execute("DELETE FROM workflow_entity WHERE id = 'ErrTr1gg3r999999'")
conn.commit()

# 2. Pega usuario e projeto padrao
cur.execute("SELECT id FROM user LIMIT 1")
user_row = cur.fetchone()
user_id = user_row[0] if user_row else None

cur.execute("SELECT id FROM project LIMIT 1")
proj_row = cur.fetchone()
proj_id = proj_row[0] if proj_row else None

print(f"[*] Usuario n8n: {user_id} | Projeto n8n: {proj_id}")
conn.close()

# 3. Executa importacao oficial do n8n
cmd = [
    "docker", "exec", "n8n-server",
    "n8n", "import:workflow",
    "--input=/tmp/n8n_error_handler.json"
]
if proj_id:
    cmd.append(f"--projectId={proj_id}")
elif user_id:
    cmd.append(f"--userId={user_id}")

print("Executando:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)

# 4. Ativa o workflow importado e vincula errorWorkflow
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE workflow_entity SET active = 1 WHERE id = 'ErrTr1gg3r999999'")
print("[+] Workflow ErrTr1gg3r999999 ativado.")
for prod_id in ['W1XyZ2aB3cD4eF5g', 'V1ewZ2aB3cD4eF9h']:
    cur.execute("SELECT settings FROM workflow_entity WHERE id = ?", (prod_id,))
    res = cur.fetchone()
    if res:
        st = json.loads(res[0]) if res[0] else {}
        st['errorWorkflow'] = 'ErrTr1gg3r999999'
        st['executionOrder'] = 'v1'
        cur.execute("UPDATE workflow_entity SET settings = ? WHERE id = ?", (json.dumps(st), prod_id))
        print(f"[+] Vinculado errorWorkflow=ErrTr1gg3r999999 em {prod_id}")

conn.commit()

print("\n--- Workflows ativos no n8n: ---")
for r in cur.execute("SELECT id, name, active, settings FROM workflow_entity"):
    print(f"ID: {r[0]} | Active: {r[2]} | Name: {r[1]}")
    print(f"  Settings: {r[3]}")

conn.close()
"""

# Copia workflow para dentro do container
client.exec_command("docker cp /opt/linkedin-automation/workflows/n8n_error_handler.json n8n-server:/tmp/n8n_error_handler.json")

sftp = client.open_sftp()
with sftp.file("/tmp/sync_n8n_clean.py", "w") as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = client.exec_command("python3 /tmp/sync_n8n_clean.py")
print("OUTPUT:\n", stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("ERROR:\n", err)

# Restart n8n to refresh triggers
print("[*] Reiniciando n8n-server...")
stdin, stdout, stderr = client.exec_command("docker restart n8n-server")
stdout.channel.recv_exit_status()
print("[+] n8n-server reiniciado com sucesso.")

client.close()
