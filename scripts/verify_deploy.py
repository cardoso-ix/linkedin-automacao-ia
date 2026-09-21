import os
import time
import requests
import paramiko

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

print("[*] Aguardando 10 segundos para inicialização dos serviços...")
time.sleep(10)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=25)

print("\n--- 1. STATUS DOS CONTAINERS ---")
stdin, stdout, stderr = client.exec_command("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
print(stdout.read().decode('utf-8'))

print("\n--- 2. LOGS DO LINKEDIN-BRIDGE ---")
stdin, stdout, stderr = client.exec_command("docker logs --tail 35 linkedin-bridge")
print(stdout.read().decode('utf-8'))

print("\n--- 3. VERIFICANDO BANCO DO N8N (WORKFLOWS) ---")
cmd_check_db = """python3 - << 'EOF'
import sqlite3
conn = sqlite3.connect('/opt/linkedin-automation/n8n_data/database.sqlite')
cur = conn.cursor()
for row in cur.execute("SELECT id, name, active, settings FROM workflow_entity"):
    print(f"ID: {row[0]} | Active: {row[2]} | Name: {row[1]}")
    print(f"  Settings: {row[3]}")
EOF
"""
stdin, stdout, stderr = client.exec_command(cmd_check_db)
print(stdout.read().decode('utf-8'))

client.close()

print("\n--- 4. TESTANDO ENDPOINTS HTTP DO BRIDGE ---")
try:
    r_health = requests.get("http://108.174.145.77:8088/health", timeout=10)
    print(f"GET /health: {r_health.status_code} {r_health.text}")
except Exception as e:
    print(f"GET /health ERRO: {e}")

try:
    r_shot = requests.get("http://108.174.145.77:8088/screenshot", timeout=30)
    print(f"GET /screenshot: {r_shot.status_code}, tamanho bytes: {len(r_shot.content)}")
    if r_shot.status_code == 200:
        with open("live_screenshot_test.png", "wb") as f:
            f.write(r_shot.content)
        print("[+] Imagem salva localmente em live_screenshot_test.png!")
except Exception as e:
    print(f"GET /screenshot ERRO: {e}")

try:
    test_payload = {
        "workflow_name": "Teste Automatizado do Deploy",
        "node_name": "Validador Playwright & Alertas",
        "error_message": "Notificação de validação: Canal de alertas críticos e Telegram operando com sucesso.",
        "execution_id": "TEST-EXEC-01"
    }
    r_err = requests.post("http://108.174.145.77:8088/notify/error", json=test_payload, timeout=15)
    print(f"POST /notify/error: {r_err.status_code} {r_err.text}")
except Exception as e:
    print(f"POST /notify/error ERRO: {e}")
