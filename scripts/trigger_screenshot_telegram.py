import os
import paramiko

HOST = os.getenv("VPS_HOST", "108.174.145.77")
PORT = int(os.getenv("VPS_PORT", "22022"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=25)

remote_code = """
import asyncio
from app import pw_manager
from telegram_bot import handle_screenshot

async def main():
    await pw_manager.get_page()
    await handle_screenshot(pw_manager)
    print("Screenshot enviado com sucesso para o Telegram!")

asyncio.run(main())
"""

sftp = client.open_sftp()
with sftp.file("/tmp/test_shot_tg.py", "w") as f:
    f.write(remote_code)
sftp.close()

client.exec_command("docker cp /tmp/test_shot_tg.py linkedin-bridge:/tmp/test_shot_tg.py")
stdin, stdout, stderr = client.exec_command("docker exec linkedin-bridge python /tmp/test_shot_tg.py")
print("STDOUT:", stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("STDERR:", err)

client.close()
