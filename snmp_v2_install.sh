#!/bin/bash

COMMUNITY="test"
CLIENT_IP=""   # boş bırakırsan herkes erişir, IP yazarsan kısıtlar

echo "[1] Paket kontrol..."
yum install -y net-snmp net-snmp-utils >/dev/null 2>&1

echo "[2] Servis durduruluyor..."
systemctl stop snmpd

echo "[3] Config yazılıyor..."
cat <<EOF > /etc/snmp/snmpd.conf
agentAddress udp:161
rocommunity $COMMUNITY $CLIENT_IP
EOF

echo "[4] Servis başlatılıyor..."
systemctl enable snmpd >/dev/null 2>&1
systemctl start snmpd

echo "[5] Firewall açılıyor..."
firewall-cmd --permanent --add-port=161/udp >/dev/null 2>&1
firewall-cmd --reload >/dev/null 2>&1

sleep 2

echo "[6] Local test..."
snmpwalk -v2c -c $COMMUNITY localhost 1.3.6.1.2.1.1.1

echo ""
echo "[✔] SNMPv2 kurulumu tamam"
echo "[TEST] Remote test komutu:"
echo "snmpwalk -v2c -c $COMMUNITY <SUNUCU_IP> 1.3.6.1.2.1.1.1"
