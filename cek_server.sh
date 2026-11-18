#!/bin/bash
#script bash

echo "================================"
echo " LAPORAN KESEHATAN SERVER PABRIK"
echo "================================"
echo "waktu pengecekan: $(date)"
echo ""

# cek who yg login

echo "[1] User yang sedang aktif: $(whoami)"

#cek memori/ram yang tersisa
echo "[2] Sisa memori (RAM)"
free -h | grep "Mem:"

#cek apakah koneksi database lancar

echo "[3] cek koneksi database..."
if [ -n "$DB_HOST" ]; then
   echo "  database host terdeteksi: $DB_HOST (aman)"
else
   echo " peringatan: variabel DB_HOST tidak di temukan"

fi

echo ""
echo "==========================================="
echo " PENGECEKAN SELESAI"
echo "==========================================="

