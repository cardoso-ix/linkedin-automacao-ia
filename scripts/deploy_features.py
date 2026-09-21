import os
import json
import sqlite3
import paramiko

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

print("[1/5] Conectando via SSH à VPS HostGator...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=25)
sftp = client.open_sftp()

print("[2/5] Fazendo upload dos arquivos atualizados...")
# Worker files
sftp.put("worker/app.py", "/opt/linkedin-automation/worker/app.py")
print("  -> worker/app.py OK")
sftp.put("worker/telegram_bot.py", "/opt/linkedin-automation/worker/telegram_bot.py")
print("  -> worker/telegram_bot.py OK")
sftp.put("worker/ai_leaders.json", "/opt/linkedin-automation/worker/ai_leaders.json")
print("  -> worker/ai_leaders.json OK")

# Workflows directory on VPS
stdin, stdout, stderr = client.exec_command("mkdir -p /opt/linkedin-automation/workflows")
stdout.channel.recv_exit_status()

sftp.put("workflows/n8n_error_handler.json", "/opt/linkedin-automation/workflows/n8n_error_handler.json")
print("  -> workflows/n8n_error_handler.json OK")
sftp.put("workflows/linkedin_comment_monitor.json", "/opt/linkedin-automation/workflows/linkedin_comment_monitor.json")
print("  -> workflows/linkedin_comment_monitor.json OK")
sftp.put("workflows/linkedin_profile_views_monitor.json", "/opt/linkedin-automation/workflows/linkedin_profile_views_monitor.json")
print("  -> workflows/linkedin_profile_views_monitor.json OK")
sftp.put("workflows/linkedin_radar_monitor.json", "/opt/linkedin-automation/workflows/linkedin_radar_monitor.json")
print("  -> workflows/linkedin_radar_monitor.json OK")

sftp.close()

print("[3/5] Importando e sincronizando workflows no banco de dados do n8n...")
setup_n8n_script = """python3 - << 'EOF'
import sqlite3, json, time, os

# Carrega credenciais do .env
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

db_path = '/opt/linkedin-automation/n8n_data/database.sqlite'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
now = time.strftime('%Y-%m-%d %H:%M:%S')

# 1. Carrega o workflow de erro
with open('/opt/linkedin-automation/workflows/n8n_error_handler.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

wf_id = wf.get('id', 'ErrTr1gg3r999999')
wf_name = wf.get('name', 'Hermes - Notificador de Erros Telegram')
nodes_json = json.dumps(wf.get('nodes', []))
connections_json = json.dumps(wf.get('connections', {}))
settings_json = json.dumps(wf.get('settings', {"executionOrder": "v1"}))

cur.execute("SELECT id FROM workflow_entity WHERE id = ?", (wf_id,))
row = cur.fetchone()
if row:
    cur.execute('''
        UPDATE workflow_entity
        SET name = ?, nodes = ?, connections = ?, settings = ?, active = 1, updatedAt = ?
        WHERE id = ?
    ''', (wf_name, nodes_json, connections_json, settings_json, now, wf_id))
    print(f"[+] Workflow de erro {wf_id} atualizado no n8n.")
else:
    cur.execute('''
        INSERT INTO workflow_entity (id, name, active, nodes, connections, createdAt, updatedAt, settings)
        VALUES (?, ?, 1, ?, ?, ?, ?, ?)
    ''', (wf_id, wf_name, nodes_json, connections_json, now, now, settings_json))
    print(f"[+] Workflow de erro {wf_id} inserido no n8n.")

# 2. Carrega o workflow do Radar de IA
if os.path.exists('/opt/linkedin-automation/workflows/linkedin_radar_monitor.json'):
    with open('/opt/linkedin-automation/workflows/linkedin_radar_monitor.json', 'r', encoding='utf-8') as f:
        wf_radar_raw = f.read()

    if opencode_key:
        wf_radar_raw = wf_radar_raw.replace('SUA_OPENCODE_API_KEY', opencode_key)
    if tg_token:
        wf_radar_raw = wf_radar_raw.replace('SEU_TELEGRAM_TOKEN', tg_token)
    if tg_chat:
        wf_radar_raw = wf_radar_raw.replace('SEU_CHAT_ID', tg_chat)

    wf_radar = json.loads(wf_radar_raw)
    radar_id = wf_radar.get('id', 'Rad4rL1d3r3sIA99')
    radar_name = wf_radar.get('name', 'LinkedIn Radar de Líderes em IA (Sniper Engagement)')
    r_nodes = json.dumps(wf_radar.get('nodes', []))
    r_conns = json.dumps(wf_radar.get('connections', {}))
    r_settings = json.dumps(wf_radar.get('settings', {"executionOrder": "v1", "errorWorkflow": wf_id}))

    cur.execute("SELECT id FROM workflow_entity WHERE id = ?", (radar_id,))
    if cur.fetchone():
        cur.execute('''
            UPDATE workflow_entity
            SET name = ?, nodes = ?, connections = ?, settings = ?, active = 1, updatedAt = ?
            WHERE id = ?
        ''', (radar_name, r_nodes, r_conns, r_settings, now, radar_id))
        print(f"[+] Workflow Radar {radar_id} atualizado no n8n.")
    else:
        cur.execute('''
            INSERT INTO workflow_entity (id, name, active, nodes, connections, createdAt, updatedAt, settings)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?)
        ''', (radar_id, radar_name, r_nodes, r_conns, now, now, r_settings))
        print(f"[+] Workflow Radar {radar_id} inserido no n8n.")

# 3. Atualiza settings dos workflows produtivos para vincular errorWorkflow
for prod_id in ['W1XyZ2aB3cD4eF5g', 'V1ewZ2aB3cD4eF9h', 'Rad4rL1d3r3sIA99']:
    cur.execute("SELECT settings FROM workflow_entity WHERE id = ?", (prod_id,))
    res = cur.fetchone()
    if res:
        st = json.loads(res[0]) if res[0] else {}
        st['errorWorkflow'] = wf_id
        st['executionOrder'] = 'v1'
        cur.execute("UPDATE workflow_entity SET settings = ? WHERE id = ?", (json.dumps(st), prod_id))
        print(f"[+] Vinculado errorWorkflow={wf_id} no workflow {prod_id}.")

conn.commit()

print("\n--- Workflows no n8n: ---")
for r in cur.execute("SELECT id, name, active FROM workflow_entity"):
    print(f"[{'ATIVO' if r[2] else 'INATIVO'}] {r[0]} - {r[1]}")

conn.close()
EOF
"""

stdin, stdout, stderr = client.exec_command(setup_n8n_script)
print(stdout.read().decode('utf-8'))

print("[4/5] Reiniciando linkedin-bridge e n8n-server no Docker...")
cmd_restart = "cd /opt/linkedin-automation && docker compose restart linkedin-bridge && docker compose restart n8n"
stdin, stdout, stderr = client.exec_command(cmd_restart)
print(stdout.read().decode('utf-8'))

print("[5/5] Testando endpoints do Radar e integridade dos containers...")
cmd_check = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' && echo '--- Teste /radar/leaders ---' && curl -s http://localhost:8088/radar/leaders"
stdin, stdout, stderr = client.exec_command(cmd_check)
print(stdout.read().decode('utf-8'))

client.close()
print("[+] Deploy finalizado com sucesso!")

