# WhatsApp — caminho mais fácil (VPS)

Sem System User agora. Usa o token do wizard (~24h). Depois troca pelo permanente.

## Ideia

1. Copiar `WHATSAPP_CLOUD_*` do PC → Hermes da VPS  
2. Abrir porta `8090` + 1 linha no Caddy  
3. Colar webhook no Meta  
4. Testar `oi` e `/postar-texto`  
5. (Depois) System User permanente

## Você faz em 3 blocos

### 1) Meta — webhook (2 min)

Quando a VPS estiver com health ok:

- Callback: `https://srv1897392.hstgr.cloud/whatsapp/webhook`
- Verify token: o mesmo do wizard no PC (`WHATSAPP_CLOUD_VERIFY_TOKEN`)
- Subscribe: `messages`

### 2) VPS — um script (SSH ou console Hostinger)

Cole o script em [`scripts/whatsapp-vps-easy.sh`](../scripts/whatsapp-vps-easy.sh) **depois** de exportar as vars (não commitar secrets).

### 3) Desligar Hermes do Windows

Para não haver dois bots: pare o gateway no PC.

## IDs fixos

- Phone Number ID: `1164738343399026`
- App ID: `2842287619460178`
- WABA: `1318156490102575`
