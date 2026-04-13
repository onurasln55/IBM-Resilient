#!/bin/bash

USER="res-snmp"
AUTH_PASS="AuthPass123"
PRIV_PASS="AuthPass123"

echo "[1] SNMP paketleri kuruluyor..."
yum --noplugins install -y net-snmp net-snmp-utils

echo "[2] Servis durduruluyor..."
systemctl stop snmpd

echo "[3] Eski config temizleniyor..."
rm -f /var/lib/net-snmp/snmpd.conf
rm -f /usr/share/snmp/snmpd.local.conf

echo "[4] SNMPv3 user oluşturuluyor..."
cat <<EOF > /var/lib/net-snmp/snmpd.conf
createUser $USER MD5 $AUTH_PASS DES $PRIV_PASS
EOF

echo "[5] Disk monitoring config yazılıyor..."
cat <<EOF > /usr/share/snmp/snmpd.local.conf
rouser $USER
disk /
disk /var/log
disk /usr/share/co3
EOF

echo "[6] Servis başlatılıyor..."
systemctl enable snmpd
systemctl start snmpd

sleep 2

echo "[7] User doğrulanıyor..."
cat /var/lib/net-snmp/snmpd.conf | grep usmUser

echo "[8] Local test yapılıyor..."
snmpget -v3 -u $USER -l authPriv \
-a MD5 -x DES \
-A $AUTH_PASS -X $PRIV_PASS \
localhost hrSystemUptime.0

echo "[✔] Kurulum tamamlandı"
