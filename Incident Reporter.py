from datetime import datetime, timedelta, timezone
from collections import defaultdict

# -------------------------
# Tarih aralıkları
# -------------------------
def get_previous_month_range(tz_offset_hours=3):
    tz = timezone(timedelta(hours=tz_offset_hours))
    now = datetime.now(tz)
    first_this_month = datetime(now.year, now.month, 1, tzinfo=tz)
    last_prev_month = first_this_month - timedelta(milliseconds=1)
    first_prev_month = datetime(last_prev_month.year, last_prev_month.month, 1, tzinfo=tz)

    turkish_months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
        5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
        9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }

    prev_month_number = last_prev_month.month
    prev_month_name = turkish_months[prev_month_number]

    return int(first_prev_month.timestamp() * 1000), int(last_prev_month.timestamp() * 1000), prev_month_name

def get_first_day_of_year(tz_offset_hours=3):
    tz = timezone(timedelta(hours=tz_offset_hours))
    now = datetime.now(tz)
    first_day = datetime(now.year, 1, 1, tzinfo=tz)
    return int(first_day.timestamp() * 1000)

first_day_ms = get_first_day_of_year()
start_prev, end_prev, prev_month_name = get_previous_month_range()

# -------------------------
# Ortak yardımcılar
# -------------------------
def normalize_type(type_field):
    if not type_field:
        return ["Other"]
    if isinstance(type_field, list):
        return type_field
    return [type_field]

def build_stats_from_incidents(incidents):
    stats = defaultdict(lambda: {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "Total": 0})
    for inc in incidents:
        severity = getattr(inc, "severity_code", None) or "Low"
        types = normalize_type(getattr(inc, "incident_type_ids", None))
        for t in types:
            # güvenlik: eğer severity beklenmeyen bir değer ise 'Low' olarak say
            if severity not in ("Low", "Medium", "High", "Critical"):
                severity = "Low"
            stats[t][severity] += 1
            stats[t]["Total"] += 1
    return stats

def stats_to_table_html(stats):
    # İç tablo başlığı
    table = """
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
      <tr style="background:#f0f0f0;">
        <th style="border:1px solid #ccc; padding:6px;">Tür</th>
        <th style="border:1px solid #ccc; padding:6px;">Low</th>
        <th style="border:1px solid #ccc; padding:6px;">Medium</th>
        <th style="border:1px solid #ccc; padding:6px;">High</th>
        <th style="border:1px solid #ccc; padding:6px;">Critical</th>
        <th style="border:1px solid #ccc; padding:6px;">Total</th>
      </tr>
    """
    total_low = total_med = total_high = total_crit = total_all = 0
    # Satırları sırayla ekle
    for t, v in stats.items():
        table += f"""
      <tr>
        <td style="border:1px solid #ccc; padding:6px;">{t}</td>
        <td style="border:1px solid #ccc; padding:6px;">{v['Low']}</td>
        <td style="border:1px solid #ccc; padding:6px;">{v['Medium']}</td>
        <td style="border:1px solid #ccc; padding:6px;">{v['High']}</td>
        <td style="border:1px solid #ccc; padding:6px;">{v['Critical']}</td>
        <td style="border:1px solid #ccc; padding:6px;">{v['Total']}</td>
      </tr>
        """
        total_low += v["Low"]
        total_med += v["Medium"]
        total_high += v["High"]
        total_crit += v["Critical"]
        total_all += v["Total"]

    # Toplam satırı
    table += f"""
      <tr style="font-weight:bold; background:#f9f9f9;">
        <td style="border:1px solid #ccc; padding:6px;">TOPLAM</td>
        <td style="border:1px solid #ccc; padding:6px;">{total_low}</td>
        <td style="border:1px solid #ccc; padding:6px;">{total_med}</td>
        <td style="border:1px solid #ccc; padding:6px;">{total_high}</td>
        <td style="border:1px solid #ccc; padding:6px;">{total_crit}</td>
        <td style="border:1px solid #ccc; padding:6px;">{total_all}</td>
      </tr>
    </table>
    """
    return table, {"Low": total_low, "Medium": total_med, "High": total_high, "Critical": total_crit, "Total": total_all}

# -------------------------
# Rapor fonksiyonları (istatistik üretir)
# -------------------------
def run_query_and_build_stats(query):
    incidents = helper.findIncidents(query)
    stats = build_stats_from_incidents(incidents)
    table_html, totals = stats_to_table_html(stats)
    return stats, table_html, totals, incidents

def yillik_rapor():
    year_query = (
        query_builder
            .isGreaterThanOrEquals(fields.incident.create_date, first_day_ms)
            .isLessThanOrEquals(fields.incident.create_date, end_prev)
            .equals(fields.incident.olay_kaydi_mi, "Evet")
            .build()
    )
    stats, table_html, totals, _ = run_query_and_build_stats(year_query)
    # log'a da yazdırmak istersen
    for t, v in stats.items():
        try:
            log.info(f"{t:40} Low={v['Low']} Medium={v['Medium']} High={v['High']} Critical={v['Critical']} Total={v['Total']}")
        except Exception:
            pass
    return table_html, stats, totals

def aylik_rapor():
    month_query = (
        query_builder
            .isGreaterThanOrEquals(fields.incident.create_date, start_prev)
            .isLessThanOrEquals(fields.incident.create_date, end_prev)
            .equals(fields.incident.olay_kaydi_mi, "Evet")
            .build()
    )
    stats, table_html, totals, _ = run_query_and_build_stats(month_query)
    for t, v in stats.items():
        try:
            log.info(f"{t:40} Low={v['Low']} Medium={v['Medium']} High={v['High']} Critical={v['Critical']} Total={v['Total']}")
        except Exception:
            pass
    return table_html, stats, totals

def aylik_rapor_inc_id():
    q = (
        query_builder
            .isGreaterThanOrEquals(fields.incident.create_date, start_prev)
            .isLessThanOrEquals(fields.incident.create_date, end_prev)
            .equals(fields.incident.olay_kaydi_mi, "Evet")
            .build()
    )
    incidents = helper.findIncidents(q)

    table_html = """
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
      <thead>
        <tr style="background:#f0f0f0;">
          <th style="border:1px solid #ccc; padding:6px;">ID</th>
          <th style="border:1px solid #ccc; padding:6px;">İsim</th>
          <th style="border:1px solid #ccc; padding:6px;">Severity</th>
          <th style="border:1px solid #ccc; padding:6px;">Link</th>
        </tr>
      </thead>
      <tbody>
    """
    for inc in incidents:
        table_html += f"""
        <tr>
          <td style="border:1px solid #ccc; padding:6px;">{inc.id}</td>
          <td style="border:1px solid #ccc; padding:6px;">{inc.name}</td>
          <td style="border:1px solid #ccc; padding:6px;">{inc.severity_code}</td>
          <td style="border:1px solid #ccc; padding:6px;">
            <a href="https://soar.onur.com.tr/#incidents/{inc.id}">Olayı Aç</a>
          </td>
        </tr>
        """

    table_html += """
      </tbody>
    </table>
    """
    return table_html

# -------------------------
# Rapor üretimi ve final HTML
# -------------------------
yillik_table_html, yillik_stats, yillik_totals = yillik_rapor()
aylik_table_html, aylik_stats, aylik_totals = aylik_rapor()
inc_list_table_html = aylik_rapor_inc_id()

# inner_table_rows istenirse aylık istatistiklerden üretilir
inner_table_rows = ""
for t, v in aylik_stats.items():
    inner_table_rows += f"""
    <tr>
      <td style="border:1px solid #008348; padding:8px;">{t}</td>
      <td style="border:1px solid #008348; padding:8px;">{v['Low']}</td>
      <td style="border:1px solid #008348; padding:8px;">{v['Medium']}</td>
      <td style="border:1px solid #008348; padding:8px;">{v['High']}</td>
      <td style="border:1px solid #008348; padding:8px;">{v['Critical']}</td>
      <td style="border:1px solid #008348; padding:8px;">{v['Total']}</td>
    </tr>
    """

# Final outer-wrapped HTML mail body
b2 = f"""
<table align="center" style="width:900px; margin:20px auto; padding:0; 
       border:3px solid #008348; border-radius:8px; background:#ffffff; font-family:Arial, sans-serif;">
  <tr>
    <td style="padding:20px;">

      <h2 style="color:#008348; margin:0 0 10px 0; text-align:center;">{prev_month_name} Rapor Özeti</h2>

      <!-- Yıllık -->
      <h3 style="margin:18px 0 6px 0; color:#006633;">Yıllık Rapor</h3>
      <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
        {yillik_table_html}
      </div>

      <!-- Aylık -->
      <h3 style="margin:18px 0 6px 0; color:#006633;">Aylık Rapor</h3>
      <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
        {aylik_table_html}
      </div>

      <!-- Olay Listesi -->
      <h3 style="margin:18px 0 6px 0; color:#006633;">Olay Kaydı Listesi</h3>
      <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
        {inc_list_table_html}
      </div>

      <!-- Özet İç Tablosu (aylık statlerden) -->
      <h3 style="margin:18px 0 6px 0; color:#006633;">Aylık Tür Dağılımı</h3>
      <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
        <table style="width:100%; border-collapse:collapse;">
          <tr>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">Tür</th>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">Low</th>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">Medium</th>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">High</th>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">Critical</th>
            <th style="border:1px solid #008348; padding:8px; background:#f0f0f0;">Total</th>
          </tr>
          {inner_table_rows}
        </table>
      </div>

    </td>
  </tr>
</table>
"""

# Atama 
inputs.mail_body_html = b2
inputs.mail_from = "soar_rapor@onur.com.tr"
inputs.mail_to = "muhammetonur.aslan@onur.com.tr"
inputs.mail_subject = f"SOAR Olay Kayıtları {prev_month_name}"
inputs.mail_incident_id=incident.id

