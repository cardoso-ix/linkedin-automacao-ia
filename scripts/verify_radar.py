import os
import sys
import json
import paramiko

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)

remote_code = """
import sqlite3, json, time, os, subprocess

env_vars = {}
if os.path.exists('/opt/linkedin-automation/.env'):
    with open('/opt/linkedin-automation/.env', 'r', encoding='utf-8') as ef:
        for el in ef:
            el = el.strip()
            if el and not el.startswith('#') and '=' in el:
                k, v = el.split('=', 1)
                env_vars[k.strip()] = v.strip()

opencode_key = env_vars.get('OPENCODE_API_KEY', '')
tg_token = env_vars.get('TELEGRAM_BOT_TOKEN', '')
tg_chat = env_vars.get('TELEGRAM_CHAT_ID', '')

radar_file = '/opt/linkedin-automation/workflows/linkedin_radar_monitor.json'
if os.path.exists(radar_file):
    with open(radar_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if opencode_key:
        content = content.replace('SUA_OPENCODE_API_KEY', opencode_key)
    if tg_token:
        content = content.replace('SEU_TELEGRAM_TOKEN', tg_token)
    if tg_chat:
        content = content.replace('SEU_CHAT_ID', tg_chat)

    with open('/tmp/radar_ready.json', 'w', encoding='utf-8') as f:
        f.write(content)

    # Copia para dentro do n8n-server container
    subprocess.run(['docker', 'cp', '/tmp/radar_ready.json', 'n8n-server:/tmp/radar_ready.json'], check=True)

    # Identifica projectId
    db_path = '/opt/linkedin-automation/n8n_data/database.sqlite'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM project LIMIT 1")
    proj_row = cur.fetchone()
    proj_id = proj_row[0] if proj_row else None
    conn.close()

    cmd = ['docker', 'exec', 'n8n-server', 'n8n', 'import:workflow', '--input=/tmp/radar_ready.json']
    if proj_id:
        cmd.append(f'--projectId={proj_id}')

    print("Executando import n8n:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)

    # Ativa no SQLite e vincula errorWorkflow
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE workflow_entity SET active = 1 WHERE id = 'Rad4rL1d3r3sIA99'")
    print("[+] Workflow Rad4rL1d3r3sIA99 ativado com sucesso.")

    cur.execute("SELECT settings FROM workflow_entity WHERE id = 'Rad4rL1d3r3sIA99'")
    row = cur.fetchone()
    if row:
        st = json.loads(row[0]) if row[0] else {}
        st['errorWorkflow'] = 'ErrTr1gg3r999999'
        st['executionOrder'] = 'v1'
        cur.execute("UPDATE workflow_entity SET settings = ? WHERE id = 'Rad4rL1d3r3sIA99'", (json.dumps(st),))
        print("[+] Vinculado errorWorkflow=ErrTr1gg3r999999 em Rad4rL1d3r3sIA99")

    conn.commit()

    print("\\n--- Workflows ativos no n8n: ---")
    for r in cur.execute("SELECT id, active, name FROM workflow_entity"):
        st = "ATIVO" if r[1] else "INATIVO"
        print(f"[{st}] {r[0]} - {r[2]}")

    conn.close()
"""


sftp = client.open_sftp()
with sftp.file("/tmp/sync_radar_workflow.py", "w") as f:
    f.write(remote_code)
sftp.close()

stdin, stdout, stderr = client.exec_command("python3 /tmp/sync_radar_workflow.py")
print("=== N8N WORKFLOW SYNC ===")
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("ERR:", err)

# Check bridge logs
stdin, stdout, stderr = client.exec_command("docker logs --tail 25 linkedin-bridge")
print("=== DOCKER LINKEDIN-BRIDGE LOGS ===")
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
