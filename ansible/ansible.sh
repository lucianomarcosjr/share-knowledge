#!/bin/bash

# === ENTRADA ===
HOST="$1"          # IP do host remoto
PASS="$2"          # Senha SSH
USER="root"

# === VALIDAÇÃO ===
if [ -z "$HOST" ] || [ -z "$PASS" ]; then
  echo "Uso: $0 <IP_DO_SERVIDOR> <SENHA_SSH>"
  exit 1
fi

# === FUNÇÃO PARA TESTAR CONEXÃO COM ANSIBLE ===
test_connection() {
  local port=$1
  TMP_INVENTORY=$(mktemp)
  echo "[new-host]" > "$TMP_INVENTORY"
  echo "$HOST ansible_user=$USER ansible_ssh_pass=$PASS ansible_port=$port" >> "$TMP_INVENTORY"

  ansible -i "$TMP_INVENTORY" new-host -m ping &>/dev/null
  local result=$?
  rm -f "$TMP_INVENTORY"
  return $result
}

# === TENTAR CONEXÃO NA PORTA 22 ===
if test_connection 22; then
  PORT=22
else
  echo "[!] Falhou na porta 22, tentando na porta 2221..."
  if test_connection 2221; then
    PORT=2221
  else
    echo "[X] Falha ao conectar nas portas 22 e 2221."
    exit 2
  fi
fi

# === CRIAR INVENTÁRIO DEFINITIVO E EXECUTAR ===
FINAL_INVENTORY=$(mktemp)
echo "[new-host]" > "$FINAL_INVENTORY"
echo "$HOST ansible_user=$USER ansible_ssh_pass=$PASS ansible_port=$PORT" >> "$FINAL_INVENTORY"

ansible-playbook /etc/ansible/playbooks/default.yml -i "$FINAL_INVENTORY" --limit new-host

rm -f "$FINAL_INVENTORY"
