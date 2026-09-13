# actions.py
import json
import logging
from typing import Dict, Any
from decision import DecisionResult, DecisionStatus
from models import ProductionAnalysis

logger = logging.getLogger(__name__)

class ActionDispatcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def dispatch(self, decision: DecisionResult, analisis: ProductionAnalysis):
        if decision.status == DecisionStatus.CRITICAL:
            self._send_email_alert(decision, analisis)
            self._trigger_webhook(decision, analisis)
            self._write_to_db(decision, analisis)
        elif decision.status == DecisionStatus.WARNING:
            self._send_email_alert(decision, analisis)
            self._write_to_db(decision, analisis)
        else:
            self._write_to_db(decision, analisis)

    def _send_email_alert(self, decision, analisis):
        if not self.config.get('smtp_enabled', False):
            logger.info("SMTP tidak diaktifkan, lewati email")
            return
        try:
            # Di sini  bisa pakai smtplib untuk kirim email
            logger.info(f"Mengirim email alert: {decision.status.value}")
            # ... kode pengiriman email (di tahap ini cukup log dulu)
        except Exception as e:
            logger.error(f"Gagal kirim email: {e}")

    def _trigger_webhook(self, decision, analisis):
        url = self.config.get('webhook_url')
        if not url:
            logger.info("Tidak ada webhook URL, lewati")
            return
        try:
            # Di sini  bisa pakai requests.post untuk trigger webhook
            logger.info(f"Memicu webhook: {url}")
            # ... kode request (di tahap ini cukup log dulu)
        except Exception as e:
            logger.error(f"Webhook gagal: {e}")

    def _write_to_db(self, decision, analisis):
      from db import get_connection, insert_decision_log
      conn = None
      try:
        conn = get_connection()
        kpi = self.config.get("kpi", {})
        sukses = insert_decision_log(conn, decision, analisis, kpi)
        if sukses:
            logger.info("Keputusan berhasil disimpan ke decision_log")
        else:
            logger.error("Gagal menyimpan keputusan ke decision_log")
      except Exception as e:
        logger.error(f"Error saat write to DB: {e}")
      finally:
        if conn:
            conn.close()