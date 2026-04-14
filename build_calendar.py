#!/usr/bin/env python3
"""
Build the Last War Event Calendar + ICS generator.
Reads cpt_hedge_timeline.json and generates:
  1. guides/calendar.html — Interactive calendar with daily tasks + server events
  2. guides/lastwar_calendar.ics — Static ICS for Server #2013

Output: guides/calendar.html, guides/lastwar_calendar.ics
"""
import json
import os
from datetime import datetime, timedelta


# Server #2013 creation date
SERVER_2013_CREATION = datetime(2025, 12, 14)
SEASON_LENGTHS = [120, 90, 90, 90, 90, 90]  # Season 0-5 in days

# Spanish translations for all UI strings in the generated HTML
TRANSLATIONS_ES = {
    # Day names
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Mi\u00e9rcoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "S\u00e1bado",
    "Sunday": "Domingo",
    # Short day names (calendar header)
    "Mon": "Lun",
    "Tue": "Mar",
    "Wed": "Mi\u00e9",
    "Thu": "Jue",
    "Fri": "Vie",
    "Sat": "S\u00e1b",
    "Sun": "Dom",
    # Month names
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre",
    # Short month names
    "Jan": "Ene",
    "Feb": "Feb",
    "Mar": "Mar",
    "Apr": "Abr",
    "Jun": "Jun",
    "Jul": "Jul",
    "Aug": "Ago",
    "Sep": "Sep",
    "Oct": "Oct",
    "Nov": "Nov",
    "Dec": "Dic",
    # Top bar
    "title": "Calendario de Eventos",
    "subtitle": "Conoce Tu D\u00eda. Gana Tu Guerra.",
    # Setup banner
    "setup_strong": "Configura TU servidor",
    "setup_text": "Cambia la fecha de creaci\u00f3n abajo para tu servidor. Todos los eventos, fechas y la descarga del calendario se ajustar\u00e1n autom\u00e1ticamente.",
    # Config bar labels
    "config_server_created": "Servidor Creado",
    "config_timezone": "Tu Zona Horaria",
    "config_reset_hour": "Hora de Reinicio",
    "config_server_day": "D\u00eda del Servidor",
    "config_season": "Temporada",
    # Calendar navigation
    "btn_today": "Hoy",
    # Calendar weekday headers
    "weekday_mon": "Lun",
    "weekday_tue": "Mar",
    "weekday_wed": "Mi\u00e9",
    "weekday_thu": "Jue",
    "weekday_fri": "Vie",
    "weekday_sat": "S\u00e1b",
    "weekday_sun": "Dom",
    # Sidebar
    "upcoming_events": "Pr\u00f3ximos Eventos",
    "legend_title": "Leyenda",
    "legend_hero": "Desbloqueo de H\u00e9roe",
    "legend_war": "Guerra / PvP",
    "legend_alliance": "Evento de Alianza",
    "legend_weapon": "Arma Exclusiva",
    "legend_season": "Inicio de Temporada",
    "legend_event": "Evento General",
    "download_title": "Descargar Calendario",
    "ics_desc": "Descarga un archivo .ics personalizado usando TU fecha de servidor, zona horaria y hora de reinicio configuradas arriba.",
    "ics_btn": "Descargar .ics para Tu Servidor",
    "subscribe_summary": "URL de Suscripci\u00f3n (solo Servidor #2013)",
    "subscribe_label": "URL de sincronizaci\u00f3n autom\u00e1tica para miembros de la alianza [OWOW]:",
    "subscribe_hint": "Pega en Google Calendar &rarr; Otros calendarios &rarr; Desde URL<br>Este archivo est\u00e1tico es solo para el Servidor #2013. Otros servidores: usa el bot\u00f3n de Descarga arriba.",
    # Day detail panel
    "detail_what_to_do": "Qu\u00e9 HACER",
    "detail_what_to_save": "Qu\u00e9 GUARDAR",
    "detail_special_events": "Eventos Especiales",
    # Radar tips
    "radar_collect": "RECOGER",
    "radar_collect_tip": "misiones de radar acumuladas despu\u00e9s del reinicio de las 6:05 PM!",
    "radar_stack": "ACUMULAR",
    "radar_stack_tip": "misiones de radar esta noche (~10 PM) &mdash; \u00a1completa pero NO recojas!",
    # Priority labels
    "priority_low": "baja",
    "priority_medium": "media",
    "priority_high": "alta",
    "priority_critical": "cr\u00edtica",
    "priority_prep": "preparaci\u00f3n",
    # VS Duel phase names
    "Radar Training": "Entrenamiento de Radar",
    "Base Expansion": "Expansi\u00f3n de Base",
    "Age of Science": "Era de la Ciencia",
    "Train Heroes": "Entrenar H\u00e9roes",
    "Total Mobilization": "Movilizaci\u00f3n Total",
    "Enemy Buster": "Destructor de Enemigos",
    "PREP DAY (no VS)": "D\u00cdA DE PREPARACI\u00d3N (sin VS)",
    "PREP": "PREP",
    # Arms Race phase names
    "Drone Boost": "Impulso de Dron",
    "City Building": "Construcci\u00f3n de Ciudad",
    "Tech Research": "Investigaci\u00f3n Tecnol\u00f3gica",
    "Hero Advancement": "Avance de H\u00e9roes",
    "Unit Progression": "Progresi\u00f3n de Unidades",
    "Recovery / Prep": "Recuperaci\u00f3n / Preparaci\u00f3n",
    # Upcoming events
    "no_events_30": "Sin eventos en los pr\u00f3ximos 30 d\u00edas",
    "badge_today": "HOY",
    "badge_tomorrow": "MA\u00d1ANA",
    # Detail meta
    "server_day": "D\u00eda del Servidor",
    "prep_day_label": "D\u00cdA DE PREPARACI\u00d3N",
    "prep_day_suffix": "\u00a1Guarda todo!",
    # Footer
    "footer": "[OWOW] Old World Order &mdash; Calendario de Eventos &mdash; Last War: Survival &mdash; Sistema de Comando Kristen",
    # whatToDo translations (keyed by English text)
    "todo_mon_1": "Recoger misiones de radar acumuladas (despu\u00e9s del reinicio de las 6:05 PM)",
    "todo_mon_2": "Gastar toda la energ\u00eda en ataques/reuniones/radar",
    "todo_mon_3": "Abrir cofres de CHIPS de datos de dron (chips de habilidad para Laboratorio de Chips)",
    "todo_mon_4": "Usar datos de combate de dron + entrenar partes de dron",
    "todo_mon_5": "Recoger recursos de minas (casillas de oro = m\u00e1s puntos, territorio de alianza +25%)",
    "todo_tue_1": "Abrir TODOS los regalos de construcci\u00f3n completada (cajas de regalo)",
    "todo_tue_2": "Usar TODOS los aceleradores de construcci\u00f3n para terminar mejoras",
    "todo_tue_3": "Despachar camiones comerciales UR (dorados) \u2014 \u00a1actualiza para Legendarios!",
    "todo_tue_4": "Iniciar tareas secretas Legendarias",
    "todo_tue_5": "Usar boletos de reclutamiento de sobrevivientes",
    "todo_wed_1": "Usar TODOS los aceleradores de investigaci\u00f3n para completar proyectos tecnol\u00f3gicos",
    "todo_wed_2": "Abrir cofres de COMPONENTES de dron (\u00a1SOLO cuentan hoy!)",
    "todo_wed_3": "Gastar Insignias de Valor en investigaci\u00f3n de Duelo de Alianza",
    "todo_wed_4": "Recoger misiones de radar acumuladas (despu\u00e9s de las 6:05 PM)",
    "todo_wed_5": "Iniciar nueva investigaci\u00f3n \u2192 acelerar \u2192 repetir para m\u00e1ximas completaciones",
    "todo_thu_1": "Invertir TODA la XP de h\u00e9roe en h\u00e9roes prioritarios",
    "todo_thu_2": "Usar TODOS los fragmentos de h\u00e9roe (subir estrellas)",
    "todo_thu_3": "Aplicar TODAS las medallas de habilidad",
    "todo_thu_4": "Usar fragmentos de arma de h\u00e9roe",
    "todo_thu_5": "Usar boletos de reclutamiento (Legendario/Nueva Era/Retorno de H\u00e9roe)",
    "todo_thu_6": "\u00a1La Campa\u00f1a Honorable se reinicia hoy!",
    "todo_fri_1": "CASCADA: Entrenar T5 \u2192 mejorar T6 \u2192 T7 \u2192 T8 (\u00a1cada nivel = m\u00e1s puntos!)",
    "todo_fri_2": "\u00a1Usar TODOS los aceleradores de entrenamiento (multiplicador 4x de puntos!)",
    "todo_fri_3": "Recoger misiones de radar acumuladas (despu\u00e9s de las 6:05 PM)",
    "todo_fri_4": "Usar aceleradores sobrantes de construcci\u00f3n/investigaci\u00f3n",
    "todo_fri_5": "Entrenar tantas tandas como sea posible \u2014 \u00a1cada tropa cuenta!",
    "todo_sat_1": "Comprar escudo de 24hrs (5,000 diamantes) DESPU\u00c9S de atacar",
    "todo_sat_2": "Explorar objetivos PRIMERO \u2014 encontrar bases con tropas defendiendo",
    "todo_sat_3": "\u00a1Atacar bases enemigas (coordinarse con la alianza para el momento!)",
    "todo_sat_4": "Usar aceleradores de curaci\u00f3n para revivir y atacar de nuevo",
    "todo_sat_5": "Quitar TU formaci\u00f3n defensiva para minimizar p\u00e9rdidas si te atacan",
    "todo_sat_6": "Atacar a las ~4:05am hora del servidor si es posible (oponentes durmiendo)",
    "todo_sun_1": "Enviar escuadrones de recolecci\u00f3n programados para regresar DESPU\u00c9S del reinicio del lunes a las 6 PM",
    "todo_sun_2": "Acumular misiones de radar ~10 PM (completar pero NO recoger)",
    "todo_sun_3": "Guardar TODOS los aceleradores, XP de h\u00e9roe, fragmentos, medallas \u2014 no tocar NADA",
    "todo_sun_4": "Revisar tiendas para partes de dron/chips de datos (VIP, Alianza, Campa\u00f1a, Honor)",
    "todo_sun_5": "Iniciar una mejora de construcci\u00f3n larga para terminar Lun/Mar (\u00a1regalo!)",
    # whatToSave translations
    "save_hero_thu": "XP/fragmentos/medallas de h\u00e9roe \u2192 JUEVES",
    "save_construction_tue": "Aceleradores de construcci\u00f3n \u2192 MARTES",
    "save_research_wed": "Aceleradores de investigaci\u00f3n \u2192 MI\u00c9RCOLES",
    "save_training_fri": "Aceleradores de entrenamiento \u2192 VIERNES",
    "save_drone_comp_wed": "Cofres de COMPONENTES de dron \u2192 MI\u00c9RCOLES",
    "save_hero_thu2": "XP/fragmentos/medallas de h\u00e9roe \u2192 JUEVES",
    "save_training_fri2": "Aceleradores de entrenamiento \u2192 VIERNES",
    "save_training_fri_big": "\u00a1Aceleradores de entrenamiento \u2192 VIERNES (ma\u00f1ana, el gran d\u00eda!)",
    "save_construction_next_tue": "Aceleradores de construcci\u00f3n \u2192 pr\u00f3ximo MARTES",
    "save_healing_sat": "Aceleradores de curaci\u00f3n \u2192 S\u00c1BADO",
    "save_everything_next": "\u00a1Empieza a guardar todo para el ciclo de la pr\u00f3xima semana!",
    "save_everything_sun": "TODO \u2014 El domingo es pura preparaci\u00f3n, no hay puntos disponibles",
}


def load_timeline(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_weekly_schedule():
    """Return the 7-day weekly schedule data."""
    return [
        {
            "dow": 1,
            "dayName": "Monday",
            "armsRace": "Drone Boost",
            "vsDuel": "Radar Training",
            "vp": 1,
            "priority": "low",
            "whatToDo": [
                "Collect stacked radar missions (after 6:05 PM reset)",
                "Spend all stamina on attacks/rallies/radar",
                "Open drone data CHIP chests (skill chips for Chip Lab)",
                "Use drone combat data + train drone parts",
                "Gather resources from mines (gold tiles = most points, alliance territory +25%)"
            ],
            "whatToSave": [
                "Hero XP/shards/medals \u2192 THURSDAY",
                "Construction speedups \u2192 TUESDAY",
                "Research speedups \u2192 WEDNESDAY",
                "Training speedups \u2192 FRIDAY",
                "Drone COMPONENT chests \u2192 WEDNESDAY"
            ],
            "stackRadar": False,
            "collectRadar": True
        },
        {
            "dow": 2,
            "dayName": "Tuesday",
            "armsRace": "City Building",
            "vsDuel": "Base Expansion",
            "vp": 1,
            "priority": "low",
            "whatToDo": [
                "Open ALL building completion presents (gift boxes)",
                "Use ALL construction speedups to finish upgrades",
                "Dispatch UR (gold) trade trucks \u2014 refresh for Legendary!",
                "Start Legendary secret tasks",
                "Use survivor recruitment tickets"
            ],
            "whatToSave": [
                "Research speedups \u2192 WEDNESDAY",
                "Hero XP/shards/medals \u2192 THURSDAY",
                "Training speedups \u2192 FRIDAY",
                "Drone COMPONENT chests \u2192 WEDNESDAY"
            ],
            "stackRadar": True,
            "collectRadar": False
        },
        {
            "dow": 3,
            "dayName": "Wednesday",
            "armsRace": "Tech Research",
            "vsDuel": "Age of Science",
            "vp": 1,
            "priority": "low",
            "whatToDo": [
                "Use ALL research speedups to complete tech projects",
                "Open drone COMPONENT chests (ONLY score today!)",
                "Spend Valor Badges on Alliance Duel research",
                "Collect stacked radar missions (after 6:05 PM)",
                "Start new research \u2192 speedup \u2192 repeat for max completions"
            ],
            "whatToSave": [
                "Hero XP/shards/medals \u2192 THURSDAY",
                "Training speedups \u2192 FRIDAY"
            ],
            "stackRadar": False,
            "collectRadar": True
        },
        {
            "dow": 4,
            "dayName": "Thursday",
            "armsRace": "Hero Advancement",
            "vsDuel": "Train Heroes",
            "vp": 2,
            "priority": "medium",
            "whatToDo": [
                "Dump ALL hero XP into priority heroes",
                "Use ALL hero shards (star up heroes)",
                "Apply ALL skill medals",
                "Use hero weapon shards",
                "Use recruitment tickets (Legendary/New Era/Hero Return)",
                "Honorable Campaign resets today!"
            ],
            "whatToSave": [
                "Training speedups \u2192 FRIDAY (tomorrow, the big day!)",
                "Construction speedups \u2192 next TUESDAY"
            ],
            "stackRadar": True,
            "collectRadar": False
        },
        {
            "dow": 5,
            "dayName": "Friday",
            "armsRace": "Unit Progression",
            "vsDuel": "Total Mobilization",
            "vp": 3,
            "priority": "high",
            "whatToDo": [
                "WATERFALL: Train T5 \u2192 upgrade T6 \u2192 T7 \u2192 T8 (each tier = more points!)",
                "Use ALL training speedups (4x point multiplier!)",
                "Collect stacked radar missions (after 6:05 PM)",
                "Use any leftover construction/research speedups",
                "Train as many batches as possible \u2014 every troop counts!"
            ],
            "whatToSave": [
                "Healing speedups \u2192 SATURDAY"
            ],
            "stackRadar": False,
            "collectRadar": True
        },
        {
            "dow": 6,
            "dayName": "Saturday",
            "armsRace": "Enemy Buster",
            "vsDuel": "Enemy Buster",
            "vp": 4,
            "priority": "critical",
            "whatToDo": [
                "Buy 24hr shield (5,000 diamonds) AFTER attacking",
                "Scout targets FIRST \u2014 find bases with troops defending",
                "Attack enemy bases (coordinate with alliance for timing!)",
                "Use healing speedups to revive and attack again",
                "Remove YOUR defense lineup to minimize losses if attacked",
                "Attack at ~4:05am server time if possible (opponents sleeping)"
            ],
            "whatToSave": [
                "Start saving everything for next week's cycle!"
            ],
            "stackRadar": False,
            "collectRadar": False
        },
        {
            "dow": 0,
            "dayName": "Sunday",
            "armsRace": "Recovery / Prep",
            "vsDuel": "PREP DAY (no VS)",
            "vp": 0,
            "priority": "prep",
            "whatToDo": [
                "Send gathering squads timed to return AFTER Monday 6 PM reset",
                "Stack radar missions ~10 PM (complete but DON'T collect)",
                "Save ALL speedups, hero XP, shards, medals \u2014 touch NOTHING",
                "Check stores for drone parts/data chips (VIP, Alliance, Campaign, Honor)",
                "Start a long building upgrade to finish Mon/Tue (present!)"
            ],
            "whatToSave": [
                "EVERYTHING \u2014 Sunday is pure prep, no points available"
            ],
            "stackRadar": True,
            "collectRadar": False
        }
    ]


def compute_absolute_day(season, day_in_season):
    """Convert (season, day) to absolute server day."""
    offset = 0
    for s in range(season):
        if s < len(SEASON_LENGTHS):
            offset += SEASON_LENGTHS[s]
        else:
            offset += 90
    return offset + day_in_season


def generate_ics(timeline, server_creation, reset_hour=18):
    """Generate a static .ics file for a specific server."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OWOW SKYNET//Last War Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Last War - Server Events",
        "X-WR-TIMEZONE:UTC",
    ]

    uid_counter = 0

    # Weekly recurring events
    schedule = get_weekly_schedule()
    # Start recurring from server creation week
    for sched in schedule:
        if sched["vp"] == 0:
            continue  # Skip Sunday prep
        dow_map = {0: "SU", 1: "MO", 2: "TU", 3: "WE", 4: "TH", 5: "FR", 6: "SA"}
        ical_dow = dow_map[sched["dow"]]

        # Find first occurrence of this weekday on or after server creation
        # sched["dow"] uses JS convention (Sun=0), Python weekday() uses Mon=0
        python_dow = (sched["dow"] - 1) % 7  # Convert JS dow to Python weekday
        days_ahead = (python_dow - server_creation.weekday()) % 7
        first_date = server_creation + timedelta(days=days_ahead)

        todo_text = "\\n".join(["DO: " + t for t in sched["whatToDo"]])
        save_text = "\\n".join(["SAVE: " + t for t in sched["whatToSave"]])
        desc = f"Arms Race: {sched['armsRace']}\\nVS Duel: {sched['vsDuel']}\\nVP: {sched['vp']}\\n\\n{todo_text}\\n\\n{save_text}"

        vp_stars = "\u2605" * sched["vp"]
        summary = f"{sched['vsDuel']} ({sched['vp']}VP {vp_stars})"

        dt_start = first_date.strftime("%Y%m%d") + f"T{reset_hour:02d}0000"
        uid_counter += 1

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:owow-weekly-{uid_counter}@lastwar",
            f"DTSTART:{dt_start}",
            f"DURATION:PT2H",
            f"RRULE:FREQ=WEEKLY;BYDAY={ical_dow}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "END:VEVENT",
        ])

    # One-time timeline events
    for evt in timeline:
        abs_day = compute_absolute_day(evt["season"], evt["day"])
        evt_date = server_creation + timedelta(days=abs_day - 1)
        dt_start = evt_date.strftime("%Y%m%d")
        uid_counter += 1

        season_label = f"S{evt['season']}: " if evt["season"] > 0 else ""
        summary = f"{season_label}{evt['name']}"
        desc = evt.get("details", "").replace("\n", "\\n")

        alert_days = 1 if evt["type"] == "hero" else 0

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:owow-event-{uid_counter}@lastwar",
            f"DTSTART;VALUE=DATE:{dt_start}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            f"CATEGORIES:{evt['type'].upper()}",
        ])
        if alert_days:
            lines.extend([
                "BEGIN:VALARM",
                "TRIGGER:-P1D",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Tomorrow: {summary}",
                "END:VALARM",
            ])
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def generate_html(timeline_json, schedule_json):
    """Generate the full self-contained calendar HTML page."""
    translations_json = json.dumps(TRANSLATIONS_ES, ensure_ascii=False, separators=(',', ':'))
    return f'''<!DOCTYPE html>
<html lang="en" id="htmlRoot">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Last War Event Calendar | OWOW SKYNET</title>
{generate_css()}
</head>
<body>

<nav class="guide-nav">
  <a href="../" class="nav-home">&#8592; Home</a>
  <a href="ai_advisor.html">AI Advisor</a>
  <a href="alliance_support_hub.html">Alliance Hub</a>
  <a href="building_planner.html">Building Planner</a>
  <a href="building_reference.html">Building Ref</a>
  <a href="capitol_positions.html">Capitol Positions</a>
  <a href="chip_lab_guide.html">Chip Lab</a>
  <a href="calendar.html" class="current">Calendar</a>
  <a href="hero_planner.html">Hero Planner</a>
  <a href="plunder_guide.html">Plunder</a>
  <a href="radar_guide.html">Radar</a>
  <a href="../research_trees_visual.html">Research Trees</a>
  <a href="server_dashboard.html">Server</a>
  <a href="vs_weekly_planner.html">VS Planner</a>
  <a href="waterfall_guide.html">Waterfall</a>
</nav>

<div class="top-bar">
  <div class="left">
    <h1 data-i18n="title">Event Calendar</h1>
    <div class="sub" data-i18n="subtitle">Know Your Day. Win Your War.</div>
  </div>
  <div class="alliance">
    <div class="lang-toggle">
      <button class="lang-btn active" id="btnEN" onclick="setLang('en')">EN</button>
      <button class="lang-btn" id="btnES" onclick="setLang('es')">ES</button>
    </div>
    <img src="skynet_logo.png" alt="OWOW SKYNET" class="skynet-logo">
    <div class="alliance-text">
      <div class="name">[OWOW]</div>
      <div class="tagline">SKYNET</div>
    </div>
  </div>
</div>

<div id="setupBanner" class="setup-banner" style="display:none">
  <div class="setup-icon">&#9881;</div>
  <div class="setup-text">
    <strong data-i18n="setup_strong">Set up YOUR server</strong> &mdash; <span data-i18n="setup_text">Change the creation date below to match your server. All events, dates, and the calendar download will adjust automatically.</span>
  </div>
  <button id="dismissSetup" class="setup-dismiss">&times;</button>
</div>

<div class="config-bar">
  <div class="config-group">
    <label for="serverDate" data-i18n="config_server_created">Your Server Created</label>
    <input type="date" id="serverDate" value="2025-12-14">
  </div>
  <div class="config-group">
    <label for="timezone" data-i18n="config_timezone">Your Timezone</label>
    <select id="timezone">
      <option value="-12">UTC-12</option>
      <option value="-11">UTC-11</option>
      <option value="-10">HST (UTC-10)</option>
      <option value="-9">AKST (UTC-9)</option>
      <option value="-8">PST (UTC-8)</option>
      <option value="-7">MST (UTC-7)</option>
      <option value="-6">CST (UTC-6)</option>
      <option value="-5">EST (UTC-5)</option>
      <option value="-4">AST (UTC-4)</option>
      <option value="-3">BRT (UTC-3)</option>
      <option value="-2">UTC-2</option>
      <option value="-1">UTC-1</option>
      <option value="0">UTC / GMT</option>
      <option value="1">CET (UTC+1)</option>
      <option value="2">EET (UTC+2)</option>
      <option value="3">MSK (UTC+3)</option>
      <option value="3.5">IRST (UTC+3:30)</option>
      <option value="4">GST (UTC+4)</option>
      <option value="5">PKT (UTC+5)</option>
      <option value="5.5">IST (UTC+5:30)</option>
      <option value="6">BST (UTC+6)</option>
      <option value="7">ICT (UTC+7)</option>
      <option value="8">CST/SGT (UTC+8)</option>
      <option value="9">JST/KST (UTC+9)</option>
      <option value="9.5">ACST (UTC+9:30)</option>
      <option value="10">AEST (UTC+10)</option>
      <option value="11">SBT (UTC+11)</option>
      <option value="12">NZST (UTC+12)</option>
      <option value="13">NZDT (UTC+13)</option>
    </select>
  </div>
  <div class="config-group">
    <label for="resetHour" data-i18n="config_reset_hour">Reset Hour</label>
    <select id="resetHour">
      <option value="0">12 AM</option>
      <option value="1">1 AM</option>
      <option value="2">2 AM</option>
      <option value="3">3 AM</option>
      <option value="4">4 AM</option>
      <option value="5">5 AM</option>
      <option value="6">6 AM</option>
      <option value="7">7 AM</option>
      <option value="8">8 AM</option>
      <option value="9">9 AM</option>
      <option value="10">10 AM</option>
      <option value="11">11 AM</option>
      <option value="12">12 PM</option>
      <option value="13">1 PM</option>
      <option value="14">2 PM</option>
      <option value="15">3 PM</option>
      <option value="16">4 PM</option>
      <option value="17">5 PM</option>
      <option value="18" selected>6 PM</option>
      <option value="19">7 PM</option>
      <option value="20">8 PM</option>
      <option value="21">9 PM</option>
      <option value="22">10 PM</option>
      <option value="23">11 PM</option>
    </select>
  </div>
  <div class="config-group">
    <label data-i18n="config_server_day">Server Day</label>
    <div id="serverDayDisplay" class="server-day-badge">Day --</div>
  </div>
  <div class="config-group">
    <label data-i18n="config_season">Season</label>
    <div id="seasonDisplay" class="season-badge">--</div>
  </div>
</div>

<div class="main-layout">
  <div class="calendar-container">
    <div class="cal-header">
      <button id="prevMonth" class="cal-nav">&larr;</button>
      <h2 id="monthTitle">March 2026</h2>
      <button id="nextMonth" class="cal-nav">&rarr;</button>
      <button id="todayBtn" class="today-btn" data-i18n="btn_today">Today</button>
    </div>
    <div class="cal-weekdays">
      <div data-i18n="weekday_mon">Mon</div><div data-i18n="weekday_tue">Tue</div><div data-i18n="weekday_wed">Wed</div><div data-i18n="weekday_thu">Thu</div><div data-i18n="weekday_fri">Fri</div><div data-i18n="weekday_sat">Sat</div><div data-i18n="weekday_sun">Sun</div>
    </div>
    <div id="calGrid" class="cal-grid"></div>
  </div>

  <div class="sidebar">
    <div class="sidebar-section">
      <h3 data-i18n="upcoming_events">Upcoming Events</h3>
      <div id="upcomingEvents" class="upcoming-list"></div>
    </div>
    <div class="sidebar-section">
      <h3 data-i18n="legend_title">Legend</h3>
      <div class="legend">
        <div class="legend-item"><span class="dot dot-hero"></span> <span data-i18n="legend_hero">Hero Unlock</span></div>
        <div class="legend-item"><span class="dot dot-war"></span> <span data-i18n="legend_war">War / PvP</span></div>
        <div class="legend-item"><span class="dot dot-alliance"></span> <span data-i18n="legend_alliance">Alliance Event</span></div>
        <div class="legend-item"><span class="dot dot-weapon"></span> <span data-i18n="legend_weapon">Exclusive Weapon</span></div>
        <div class="legend-item"><span class="dot dot-season"></span> <span data-i18n="legend_season">Season Start</span></div>
        <div class="legend-item"><span class="dot dot-event"></span> <span data-i18n="legend_event">General Event</span></div>
      </div>
    </div>
    <div class="sidebar-section ics-section">
      <h3 data-i18n="download_title">Download Calendar</h3>
      <p class="ics-desc" data-i18n="ics_desc">Downloads a personalized .ics file using YOUR server date, timezone, and reset hour settings above.</p>
      <button id="downloadIcs" class="ics-btn" data-i18n="ics_btn">Download .ics for Your Server</button>
      <details class="subscribe-details">
        <summary data-i18n="subscribe_summary">Subscribe URL (Server #2013 only)</summary>
        <div class="subscribe-box">
          <div class="subscribe-label" data-i18n="subscribe_label">Auto-sync URL for [OWOW] alliance members:</div>
          <input type="text" readonly class="subscribe-url"
            value="https://extremesecrecy.github.io/lastwar-research-trees/guides/lastwar_calendar.ics"
            onclick="this.select()">
          <div class="subscribe-hint" data-i18n="subscribe_hint">Paste into Google Calendar &rarr; Other calendars &rarr; From URL<br>This static file is for Server #2013 only. Other servers: use the Download button above.</div>
        </div>
      </details>
    </div>
  </div>
</div>

<div id="dayDetail" class="day-detail" style="display:none">
  <div class="detail-header">
    <h3 id="detailTitle">Monday, Mar 6</h3>
    <div id="detailMeta" class="detail-meta"></div>
    <button id="closeDetail" class="close-btn">&times;</button>
  </div>
  <div class="detail-body">
    <div class="detail-col">
      <h4 data-i18n="detail_what_to_do">What To Do</h4>
      <ul id="detailToDo" class="checklist"></ul>
    </div>
    <div class="detail-col">
      <h4 data-i18n="detail_what_to_save">What To Save</h4>
      <ul id="detailSave" class="savelist"></ul>
    </div>
  </div>
  <div id="detailEvents" class="detail-events"></div>
  <div id="detailRadar" class="detail-radar"></div>
</div>

<div class="footer" data-i18n="footer">
  [OWOW] Old World Order &mdash; Event Calendar &mdash; Last War: Survival &mdash; Kristen Command System
</div>

<script>
const TIMELINE_EVENTS = {timeline_json};
const WEEKLY_SCHEDULE = {schedule_json};
const SEASON_LENGTHS = [120, 90, 90, 90, 90, 90];

const T = {{ es: {translations_json} }};
const originals = {{}};
let currentLang = 'en';

function t(key, fallback) {{
  if (currentLang === 'es' && T.es[key]) return T.es[key];
  return fallback;
}}

function setLang(lang) {{
  currentLang = lang;
  document.querySelectorAll('[data-i18n]').forEach(function(el) {{
    var key = el.getAttribute('data-i18n');
    if (lang === 'es' && T.es[key]) {{
      el.innerHTML = T.es[key];
    }} else if (lang === 'en' && originals[key]) {{
      el.innerHTML = originals[key];
    }}
  }});
  document.getElementById('btnEN').classList.toggle('active', lang === 'en');
  document.getElementById('btnES').classList.toggle('active', lang === 'es');
  document.getElementById('htmlRoot').setAttribute('lang', lang);
  localStorage.setItem('owow-calendar-lang', lang);
  render();
  updateServerDay();
}}

let currentMonth, currentYear;
let serverCreation, resetHour;

function init() {{
  document.querySelectorAll('[data-i18n]').forEach(function(el) {{
    originals[el.getAttribute('data-i18n')] = el.innerHTML;
  }});
  const savedLang = localStorage.getItem('owow-calendar-lang');
  if (savedLang && savedLang !== 'en') {{
    currentLang = savedLang;
  }}
  const saved = localStorage.getItem('owow-calendar-config');
  if (saved) {{
    try {{
      const c = JSON.parse(saved);
      if (c.serverDate) document.getElementById('serverDate').value = c.serverDate;
      if (c.timezone) document.getElementById('timezone').value = c.timezone;
      if (c.resetHour) document.getElementById('resetHour').value = c.resetHour;
    }} catch(e) {{}}
  }} else {{
    // First visit — show setup banner and auto-detect timezone
    document.getElementById('setupBanner').style.display = 'flex';
    const offsetMin = new Date().getTimezoneOffset();
    const offsetHrs = -(offsetMin / 60); // JS offset is inverted (EST = +300 = UTC-5)
    const tzSelect = document.getElementById('timezone');
    let bestMatch = '0';
    let bestDiff = 999;
    for (const opt of tzSelect.options) {{
      const diff = Math.abs(parseFloat(opt.value) - offsetHrs);
      if (diff < bestDiff) {{ bestDiff = diff; bestMatch = opt.value; }}
    }}
    tzSelect.value = bestMatch;
  }}
  document.getElementById('dismissSetup').onclick = () => {{
    document.getElementById('setupBanner').style.display = 'none';
    saveConfig(); // Saves whatever they have, marks as configured
  }};
  loadConfig();
  const today = new Date();
  currentMonth = today.getMonth();
  currentYear = today.getFullYear();
  render();
  document.getElementById('prevMonth').onclick = () => {{ changeMonth(-1); }};
  document.getElementById('nextMonth').onclick = () => {{ changeMonth(1); }};
  document.getElementById('todayBtn').onclick = goToday;
  document.getElementById('closeDetail').onclick = () => {{
    document.getElementById('dayDetail').style.display = 'none';
  }};
  document.getElementById('downloadIcs').onclick = downloadIcs;
  document.getElementById('serverDate').onchange = () => {{ saveConfig(); loadConfig(); render(); }};
  document.getElementById('timezone').onchange = () => {{ saveConfig(); loadConfig(); render(); }};
  document.getElementById('resetHour').onchange = () => {{ saveConfig(); loadConfig(); render(); }};
  if (currentLang !== 'en') {{
    setLang(currentLang);
  }}
}}

function saveConfig() {{
  const c = {{
    serverDate: document.getElementById('serverDate').value,
    timezone: document.getElementById('timezone').value,
    resetHour: document.getElementById('resetHour').value
  }};
  localStorage.setItem('owow-calendar-config', JSON.stringify(c));
}}

function loadConfig() {{
  const dateStr = document.getElementById('serverDate').value;
  const parts = dateStr.split('-');
  serverCreation = new Date(+parts[0], +parts[1]-1, +parts[2]);
  resetHour = +document.getElementById('resetHour').value;
  updateServerDay();
}}

function updateServerDay() {{
  const today = new Date();
  today.setHours(0,0,0,0);
  const sc = new Date(serverCreation);
  sc.setHours(0,0,0,0);
  const diff = Math.floor((today - sc) / 86400000) + 1;
  document.getElementById('serverDayDisplay').textContent = (currentLang === 'es' ? 'D\u00eda' : 'Day') + ' ' + Math.max(1, diff);
  let cumulative = 0;
  let season = 0;
  for (let s = 0; s < SEASON_LENGTHS.length; s++) {{
    if (diff <= cumulative + SEASON_LENGTHS[s]) {{
      season = s;
      break;
    }}
    cumulative += SEASON_LENGTHS[s];
    season = s + 1;
  }}
  document.getElementById('seasonDisplay').textContent = 'S' + season;
}}

function getAbsDay(season, day) {{
  let offset = 0;
  for (let s = 0; s < season && s < SEASON_LENGTHS.length; s++) {{
    offset += SEASON_LENGTHS[s];
  }}
  return offset + day;
}}

function getDateForEvent(evt) {{
  const absDay = getAbsDay(evt.season, evt.day);
  const d = new Date(serverCreation);
  d.setDate(d.getDate() + absDay - 1);
  return d;
}}

function getEventsForDate(date) {{
  const result = [];
  const d = new Date(date);
  d.setHours(0,0,0,0);
  for (const evt of TIMELINE_EVENTS) {{
    const evtDate = getDateForEvent(evt);
    evtDate.setHours(0,0,0,0);
    if (evtDate.getTime() === d.getTime()) {{
      result.push(evt);
    }}
  }}
  return result;
}}

function getScheduleForDate(date) {{
  const dow = date.getDay();
  return WEEKLY_SCHEDULE.find(s => s.dow === dow);
}}

function changeMonth(delta) {{
  currentMonth += delta;
  if (currentMonth > 11) {{ currentMonth = 0; currentYear++; }}
  if (currentMonth < 0) {{ currentMonth = 11; currentYear--; }}
  render();
}}

function goToday() {{
  const today = new Date();
  currentMonth = today.getMonth();
  currentYear = today.getFullYear();
  render();
}}

function render() {{
  renderCalendar();
  renderUpcoming();
}}

function renderCalendar() {{
  const monthNamesEN = ['January','February','March','April','May','June',
    'July','August','September','October','November','December'];
  const monthName = t(monthNamesEN[currentMonth], monthNamesEN[currentMonth]);
  document.getElementById('monthTitle').textContent = monthName + ' ' + currentYear;

  const grid = document.getElementById('calGrid');
  grid.innerHTML = '';

  const firstDay = new Date(currentYear, currentMonth, 1);
  let startDow = firstDay.getDay();
  if (startDow === 0) startDow = 7;
  startDow--;

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const today = new Date();
  today.setHours(0,0,0,0);

  // Fill blanks before first day
  for (let i = 0; i < startDow; i++) {{
    const blank = document.createElement('div');
    blank.className = 'cal-cell blank';
    grid.appendChild(blank);
  }}

  for (let day = 1; day <= daysInMonth; day++) {{
    const date = new Date(currentYear, currentMonth, day);
    date.setHours(0,0,0,0);
    const cell = document.createElement('div');
    cell.className = 'cal-cell';

    const isToday = date.getTime() === today.getTime();
    if (isToday) cell.classList.add('today');

    const sched = getScheduleForDate(date);
    const events = getEventsForDate(date);

    // Priority class
    if (sched) {{
      cell.classList.add('priority-' + sched.priority);
    }}

    // Day number
    const num = document.createElement('div');
    num.className = 'cell-day';
    num.textContent = day;
    cell.appendChild(num);

    // VS phase label
    if (sched && sched.vp > 0) {{
      const phase = document.createElement('div');
      phase.className = 'cell-phase';
      phase.textContent = t(sched.vsDuel, sched.vsDuel);
      cell.appendChild(phase);

      const vp = document.createElement('div');
      vp.className = 'cell-vp vp-' + sched.vp;
      vp.textContent = sched.vp + 'VP';
      cell.appendChild(vp);
    }} else if (sched) {{
      const phase = document.createElement('div');
      phase.className = 'cell-phase prep';
      phase.textContent = t('PREP', 'PREP');
      cell.appendChild(phase);
    }}

    // Event dots
    if (events.length > 0) {{
      const dots = document.createElement('div');
      dots.className = 'cell-dots';
      const seen = new Set();
      for (const evt of events) {{
        if (seen.has(evt.type)) continue;
        seen.add(evt.type);
        const dot = document.createElement('span');
        dot.className = 'dot dot-' + evt.type.replace(/\\s+/g, '-');
        dot.title = evt.name;
        dots.appendChild(dot);
      }}
      cell.appendChild(dots);
    }}

    // Radar indicator
    if (sched && (sched.stackRadar || sched.collectRadar)) {{
      const radar = document.createElement('div');
      radar.className = 'cell-radar';
      radar.textContent = sched.collectRadar ? '\\ud83d\\udce1' : '\\ud83d\\udce6';
      radar.title = sched.collectRadar ? t('radar_collect', 'Collect') + ' radar' : t('radar_stack', 'Stack') + ' radar';
      cell.appendChild(radar);
    }}

    cell.onclick = () => showDayDetail(date);
    grid.appendChild(cell);
  }}
}}

function renderUpcoming() {{
  const container = document.getElementById('upcomingEvents');
  container.innerHTML = '';
  const today = new Date();
  today.setHours(0,0,0,0);
  const upcoming = [];
  for (const evt of TIMELINE_EVENTS) {{
    const evtDate = getDateForEvent(evt);
    evtDate.setHours(0,0,0,0);
    const diff = Math.floor((evtDate - today) / 86400000);
    if (diff >= 0 && diff <= 30) {{
      upcoming.push({{ ...evt, realDate: evtDate, daysAway: diff }});
    }}
  }}
  upcoming.sort((a, b) => a.daysAway - b.daysAway);
  if (upcoming.length === 0) {{
    container.innerHTML = '<div class="upcoming-empty">' + t('no_events_30', 'No events in the next 30 days') + '</div>';
    return;
  }}
  for (const evt of upcoming.slice(0, 12)) {{
    const item = document.createElement('div');
    item.className = 'upcoming-item type-' + evt.type.replace(/\\s+/g, '-');
    const locale = currentLang === 'es' ? 'es' : 'en-US';
    const dateStr = evt.realDate.toLocaleDateString(locale, {{ month: 'short', day: 'numeric' }});
    const badge = evt.daysAway === 0 ? '<span class="badge-today">' + t('badge_today', 'TODAY') + '</span>'
      : evt.daysAway === 1 ? '<span class="badge-tomorrow">' + t('badge_tomorrow', 'TOMORROW') + '</span>'
      : '<span class="badge-days">' + evt.daysAway + 'd</span>';
    item.innerHTML = '<div class="upcoming-top"><span class="dot dot-' + evt.type.replace(/\\s+/g, '-') + '"></span>'
      + '<span class="upcoming-name">' + evt.name + '</span>' + badge + '</div>'
      + '<div class="upcoming-date">' + dateStr + ' &middot; ' + evt.details + '</div>';
    container.appendChild(item);
  }}
}}

function showDayDetail(date) {{
  const panel = document.getElementById('dayDetail');
  const sched = getScheduleForDate(date);
  const events = getEventsForDate(date);
  const dayNamesEN = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const monthNamesEN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const dayName = t(dayNamesEN[date.getDay()], dayNamesEN[date.getDay()]);
  const monthName = t(monthNamesEN[date.getMonth()], monthNamesEN[date.getMonth()]);

  document.getElementById('detailTitle').textContent =
    dayName + ', ' + monthName + ' ' + date.getDate();

  const sc = new Date(serverCreation);
  sc.setHours(0,0,0,0);
  const d2 = new Date(date);
  d2.setHours(0,0,0,0);
  const serverDay = Math.floor((d2 - sc) / 86400000) + 1;

  let meta = t('server_day', 'Server Day') + ' ' + serverDay;
  if (sched && sched.vp > 0) {{
    meta += ' &middot; <strong>' + t(sched.armsRace, sched.armsRace) + '</strong> + <strong>' + t(sched.vsDuel, sched.vsDuel) + '</strong>';
    meta += ' &middot; <span class="vp-inline vp-' + sched.vp + '">' + sched.vp + ' VP</span>';
  }} else if (sched) {{
    meta += ' &middot; <strong>' + t('prep_day_label', 'PREP DAY') + '</strong> &mdash; ' + t('prep_day_suffix', 'Save everything!');
  }}
  document.getElementById('detailMeta').innerHTML = meta;

  const todoList = document.getElementById('detailToDo');
  todoList.innerHTML = '';
  if (sched) {{
    const todoKeys = getTodoKeys(sched.dow);
    sched.whatToDo.forEach(function(item, i) {{
      const li = document.createElement('li');
      li.textContent = (todoKeys[i] && currentLang === 'es' && T.es[todoKeys[i]]) ? T.es[todoKeys[i]] : item;
      todoList.appendChild(li);
    }});
  }}

  const saveList = document.getElementById('detailSave');
  saveList.innerHTML = '';
  if (sched) {{
    const saveKeys = getSaveKeys(sched.dow);
    sched.whatToSave.forEach(function(item, i) {{
      const li = document.createElement('li');
      li.textContent = (saveKeys[i] && currentLang === 'es' && T.es[saveKeys[i]]) ? T.es[saveKeys[i]] : item;
      saveList.appendChild(li);
    }});
  }}

  const evtDiv = document.getElementById('detailEvents');
  evtDiv.innerHTML = '';
  if (events.length > 0) {{
    const h4 = document.createElement('h4');
    h4.textContent = t('detail_special_events', 'Special Events');
    evtDiv.appendChild(h4);
    for (const evt of events) {{
      const card = document.createElement('div');
      card.className = 'event-card type-' + evt.type.replace(/\\s+/g, '-');
      card.innerHTML = '<span class="dot dot-' + evt.type.replace(/\\s+/g, '-') + '"></span>'
        + '<strong>' + evt.name + '</strong><br><span class="event-detail">' + evt.details + '</span>';
      evtDiv.appendChild(card);
    }}
  }}

  const radarDiv = document.getElementById('detailRadar');
  radarDiv.innerHTML = '';
  if (sched && sched.collectRadar) {{
    radarDiv.innerHTML = '<div class="radar-tip collect">\\ud83d\\udce1 <strong>' + t('radar_collect', 'COLLECT') + '</strong> ' + t('radar_collect_tip', 'stacked radar missions after 6:05 PM reset!') + '</div>';
  }} else if (sched && sched.stackRadar) {{
    radarDiv.innerHTML = '<div class="radar-tip stack">\\ud83d\\udce6 <strong>' + t('radar_stack', 'STACK') + '</strong> ' + t('radar_stack_tip', 'radar missions tonight (~10 PM) \\u2014 complete but DON\\\'T collect!') + '</div>';
  }}

  panel.style.display = 'block';
  panel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}

function getTodoKeys(dow) {{
  const map = {{
    1: ['todo_mon_1','todo_mon_2','todo_mon_3','todo_mon_4','todo_mon_5'],
    2: ['todo_tue_1','todo_tue_2','todo_tue_3','todo_tue_4','todo_tue_5'],
    3: ['todo_wed_1','todo_wed_2','todo_wed_3','todo_wed_4','todo_wed_5'],
    4: ['todo_thu_1','todo_thu_2','todo_thu_3','todo_thu_4','todo_thu_5','todo_thu_6'],
    5: ['todo_fri_1','todo_fri_2','todo_fri_3','todo_fri_4','todo_fri_5'],
    6: ['todo_sat_1','todo_sat_2','todo_sat_3','todo_sat_4','todo_sat_5','todo_sat_6'],
    0: ['todo_sun_1','todo_sun_2','todo_sun_3','todo_sun_4','todo_sun_5']
  }};
  return map[dow] || [];
}}

function getSaveKeys(dow) {{
  const map = {{
    1: ['save_hero_thu','save_construction_tue','save_research_wed','save_training_fri','save_drone_comp_wed'],
    2: ['save_research_wed','save_hero_thu2','save_training_fri2','save_drone_comp_wed'],
    3: ['save_hero_thu','save_training_fri'],
    4: ['save_training_fri_big','save_construction_next_tue'],
    5: ['save_healing_sat'],
    6: ['save_everything_next'],
    0: ['save_everything_sun']
  }};
  return map[dow] || [];
}}

function downloadIcs() {{
  const resetH = +document.getElementById('resetHour').value;
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//OWOW SKYNET//Last War Calendar//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Last War - Server Events',
    'X-WR-TIMEZONE:UTC',
  ];
  let uid = 0;
  const dowMap = ['SU','MO','TU','WE','TH','FR','SA'];

  for (const sched of WEEKLY_SCHEDULE) {{
    if (sched.vp === 0) continue;
    uid++;
    let daysAhead = sched.dow - serverCreation.getDay();
    if (daysAhead < 0) daysAhead += 7;
    const first = new Date(serverCreation);
    first.setDate(first.getDate() + daysAhead);
    const dtStart = formatIcsDate(first) + 'T' + pad2(resetH) + '0000';
    const todoText = sched.whatToDo.map(t => 'DO: ' + t).join('\\n');
    const saveText = sched.whatToSave.map(t => 'SAVE: ' + t).join('\\n');
    const desc = 'Arms Race: ' + sched.armsRace + '\\nVS Duel: ' + sched.vsDuel + '\\nVP: ' + sched.vp + '\\n\\n' + todoText + '\\n\\n' + saveText;
    const stars = '\u2605'.repeat(sched.vp);
    lines.push('BEGIN:VEVENT');
    lines.push('UID:owow-w-' + uid + '@lastwar');
    lines.push('DTSTART:' + dtStart);
    lines.push('DURATION:PT2H');
    lines.push('RRULE:FREQ=WEEKLY;BYDAY=' + dowMap[sched.dow]);
    lines.push('SUMMARY:' + sched.vsDuel + ' (' + sched.vp + 'VP ' + stars + ')');
    lines.push('DESCRIPTION:' + foldIcs(desc));
    lines.push('END:VEVENT');
  }}

  for (const evt of TIMELINE_EVENTS) {{
    uid++;
    const evtDate = getDateForEvent(evt);
    const dtStart = formatIcsDate(evtDate);
    const sLabel = evt.season > 0 ? 'S' + evt.season + ': ' : '';
    lines.push('BEGIN:VEVENT');
    lines.push('UID:owow-e-' + uid + '@lastwar');
    lines.push('DTSTART;VALUE=DATE:' + dtStart);
    lines.push('SUMMARY:' + sLabel + evt.name);
    lines.push('DESCRIPTION:' + foldIcs(evt.details || ''));
    lines.push('CATEGORIES:' + evt.type.toUpperCase());
    if (evt.type === 'hero') {{
      lines.push('BEGIN:VALARM');
      lines.push('TRIGGER:-P1D');
      lines.push('ACTION:DISPLAY');
      lines.push('DESCRIPTION:Tomorrow: ' + evt.name);
      lines.push('END:VALARM');
    }}
    lines.push('END:VEVENT');
  }}

  lines.push('END:VCALENDAR');
  const blob = new Blob([lines.join('\\r\\n')], {{ type: 'text/calendar' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'lastwar_calendar.ics';
  a.click();
  URL.revokeObjectURL(url);
}}

function formatIcsDate(d) {{
  return d.getFullYear() + pad2(d.getMonth()+1) + pad2(d.getDate());
}}
function pad2(n) {{ return n < 10 ? '0'+n : ''+n; }}
function foldIcs(s) {{ return s.replace(/\\n/g, '\\\\n'); }}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>'''


def generate_css():
    return r'''<style>
@import url("https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap");
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --orange: #f4a261;
    --cyan: #5bc0de;
    --yellow: #f4d35e;
    --teal: #7fb3a8;
    --dark: #5a6a6a;
    --text: #333;
    --watermelon: #fc5c65;
    --green: #43a047;
    --red: #e53935;
    --gray: #ccc;
    --light-bg: #fafafa;
    --hero: #9b59b6;
    --war: #e53935;
    --alliance: #5bc0de;
    --weapon: #f4d35e;
    --season-clr: #f4a261;
    --event-clr: #7fb3a8;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #fff;
    color: var(--text);
    padding: 8px;
    min-height: 100vh;
  }

  h1, h2, h3, .section-label, .alliance .name {
    font-family: 'Fredoka', 'Segoe UI', sans-serif;
  }

  /* Nav */
  .guide-nav {
    display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: center;
    padding: 6px 16px; background: #f0f5f4; border-bottom: 2px solid var(--teal);
    font-size: 12px; margin: -8px -8px 12px -8px;
  }
  .guide-nav a { color: var(--dark); text-decoration: none; padding: 2px 6px; border-radius: 3px; white-space: nowrap; }
  .guide-nav a:hover { color: var(--orange); background: #fff; }
  .guide-nav a.current { color: var(--orange); font-weight: bold; background: #fff; border: 1px solid var(--orange); }
  .guide-nav .nav-home { font-weight: bold; margin-right: 8px; padding-right: 12px; border-right: 1px solid var(--teal); }

  /* Top bar */
  .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
  .top-bar h1 { font-size: 22px; letter-spacing: 1px; text-transform: uppercase; color: var(--dark); }
  .top-bar .sub { font-size: 12px; color: #888; }
  .alliance { display: flex; align-items: center; gap: 8px; background: #e8f4f1; border: 1px solid var(--teal); border-radius: 5px; padding: 4px 10px; }
  .skynet-logo { height: 40px; width: auto; }
  .alliance-text { text-align: right; }
  .alliance .name { font-size: 14px; color: var(--dark); }
  .alliance .tagline { font-size: 10px; color: var(--teal); letter-spacing: 2px; text-transform: uppercase; }

  /* Config bar */
  .config-bar {
    display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;
    padding: 10px 14px; background: var(--light-bg); border: 1px solid var(--gray);
    border-radius: 6px; margin-bottom: 14px;
  }
  .config-group { display: flex; flex-direction: column; gap: 2px; }
  .config-group label { font-size: 10px; text-transform: uppercase; color: var(--dark); font-weight: 600; letter-spacing: 0.5px; }
  .config-group input[type="date"], .config-group select {
    padding: 4px 8px; border: 1px solid var(--gray); border-radius: 4px;
    font-size: 13px; font-family: inherit; background: #fff;
  }
  .server-day-badge {
    font-size: 14px; font-weight: 700; color: var(--orange); background: #fff;
    border: 2px solid var(--orange); border-radius: 4px; padding: 2px 10px; text-align: center;
  }
  .season-badge {
    font-size: 14px; font-weight: 700; color: var(--cyan); background: #fff;
    border: 2px solid var(--cyan); border-radius: 4px; padding: 2px 10px; text-align: center;
  }

  /* Main layout */
  .main-layout { display: flex; gap: 16px; align-items: flex-start; }

  /* Calendar */
  .calendar-container { flex: 1; min-width: 0; }
  .cal-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
  .cal-header h2 { flex: 1; text-align: center; font-size: 20px; color: var(--dark); }
  .cal-nav {
    background: none; border: 2px solid var(--orange); color: var(--orange);
    width: 32px; height: 32px; border-radius: 50%; cursor: pointer;
    font-size: 16px; font-weight: bold; display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
  }
  .cal-nav:hover { background: var(--orange); color: #fff; }
  .today-btn {
    background: var(--teal); color: #fff; border: none; padding: 5px 14px;
    border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;
    transition: background 0.15s;
  }
  .today-btn:hover { background: var(--dark); }

  .cal-weekdays {
    display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;
    margin-bottom: 2px;
  }
  .cal-weekdays div {
    text-align: center; font-size: 11px; font-weight: 700; color: var(--dark);
    padding: 4px; text-transform: uppercase; letter-spacing: 1px;
  }

  .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; width: 100%; overflow: hidden; }

  .cal-cell {
    min-height: 90px; padding: 4px 5px; background: #fff; border: 1px solid #e8e8e8;
    border-radius: 4px; cursor: pointer; position: relative; transition: all 0.12s;
    display: flex; flex-direction: column;
  }
  .cal-cell:hover { border-color: var(--orange); box-shadow: 0 2px 8px rgba(244,162,97,0.18); z-index: 2; }
  .cal-cell.blank { background: transparent; border: none; cursor: default; min-height: 0; }
  .cal-cell.today { border: 2px solid var(--orange); background: #fff8f2; box-shadow: 0 0 0 2px rgba(244,162,97,0.15); }

  .cell-day { font-size: 14px; font-weight: 700; color: var(--dark); margin-bottom: 2px; }
  .cell-phase { font-size: 9px; color: #666; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .cell-phase.prep { color: var(--teal); font-weight: 600; }

  .cell-vp {
    display: inline-block; font-size: 9px; font-weight: 800; padding: 1px 5px;
    border-radius: 3px; margin-top: 1px; width: fit-content;
  }
  .cell-vp.vp-1 { background: #e8f5e9; color: #388e3c; }
  .cell-vp.vp-2 { background: #fff3e0; color: #e65100; }
  .cell-vp.vp-3 { background: #fce4ec; color: #c62828; }
  .cell-vp.vp-4 { background: #f44336; color: #fff; }

  .cell-dots { display: flex; gap: 3px; margin-top: auto; flex-wrap: wrap; padding-top: 2px; }
  .dot {
    width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0;
  }
  .dot-hero { background: var(--hero); }
  .dot-war { background: var(--war); }
  .dot-alliance-event, .dot-alliance { background: var(--alliance); }
  .dot-exclusive-weapon { background: var(--weapon); border: 1px solid #d4a017; }
  .dot-season-start { background: var(--season-clr); }
  .dot-season { background: var(--season-clr); opacity: 0.7; }
  .dot-event { background: var(--event-clr); }

  .cell-radar {
    position: absolute; top: 3px; right: 4px; font-size: 12px; opacity: 0.7;
  }

  /* Priority borders */
  .cal-cell.priority-high { border-left: 3px solid var(--watermelon); }
  .cal-cell.priority-critical { border-left: 3px solid var(--red); background: #fff5f5; }
  .cal-cell.priority-medium { border-left: 3px solid var(--orange); }
  .cal-cell.priority-prep { border-left: 3px solid var(--teal); }

  /* Sidebar */
  .sidebar { width: 280px; flex-shrink: 0; }
  .sidebar-section {
    background: var(--light-bg); border: 1px solid #e8e8e8; border-radius: 6px;
    padding: 12px; margin-bottom: 12px;
  }
  .sidebar-section h3 { font-size: 14px; color: var(--dark); margin-bottom: 8px; border-bottom: 2px solid var(--yellow); padding-bottom: 4px; }

  .legend { display: flex; flex-direction: column; gap: 6px; }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }

  .upcoming-list { display: flex; flex-direction: column; gap: 6px; }
  .upcoming-item { padding: 6px 8px; background: #fff; border-radius: 4px; border-left: 3px solid var(--gray); }
  .upcoming-item.type-hero { border-left-color: var(--hero); }
  .upcoming-item.type-war { border-left-color: var(--war); }
  .upcoming-item.type-alliance-event { border-left-color: var(--alliance); }
  .upcoming-item.type-exclusive-weapon { border-left-color: var(--weapon); }
  .upcoming-item.type-season-start { border-left-color: var(--season-clr); }
  .upcoming-item.type-event { border-left-color: var(--event-clr); }
  .upcoming-item.type-season { border-left-color: var(--season-clr); }
  .upcoming-top { display: flex; align-items: center; gap: 6px; }
  .upcoming-name { font-size: 12px; font-weight: 600; flex: 1; }
  .upcoming-date { font-size: 10px; color: #888; margin-top: 2px; }
  .badge-today { font-size: 9px; font-weight: 800; color: #fff; background: var(--watermelon); padding: 1px 6px; border-radius: 3px; }
  .badge-tomorrow { font-size: 9px; font-weight: 800; color: #fff; background: var(--orange); padding: 1px 6px; border-radius: 3px; }
  .badge-days { font-size: 9px; font-weight: 700; color: var(--dark); background: #eee; padding: 1px 6px; border-radius: 3px; }
  .upcoming-empty { font-size: 12px; color: #aaa; text-align: center; padding: 16px 0; }

  /* ICS section */
  .ics-section { }
  /* Setup banner */
  .setup-banner {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; margin-bottom: 8px;
    background: linear-gradient(135deg, #fff8e1, #fff3cd); border: 2px solid var(--orange);
    border-radius: 6px; font-size: 12px; color: var(--text);
  }
  .setup-icon { font-size: 20px; }
  .setup-text { flex: 1; line-height: 1.4; }
  .setup-text strong { color: var(--dark); }
  .setup-dismiss {
    background: none; border: none; font-size: 18px; color: #999;
    cursor: pointer; padding: 0 4px; line-height: 1;
  }
  .setup-dismiss:hover { color: var(--dark); }

  .ics-desc { font-size: 11px; color: #666; margin-bottom: 8px; line-height: 1.4; }
  .ics-btn {
    width: 100%; padding: 8px; background: var(--watermelon); color: #fff;
    border: none; border-radius: 4px; font-size: 13px; font-weight: 700;
    cursor: pointer; transition: background 0.15s; margin-bottom: 10px;
  }
  .ics-btn:hover { background: #e04550; }
  .subscribe-details { margin-top: 6px; }
  .subscribe-details summary {
    font-size: 10px; color: var(--teal); cursor: pointer; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .subscribe-details summary:hover { color: var(--dark); }
  .subscribe-box { background: #fff; border: 1px solid #e8e8e8; border-radius: 4px; padding: 8px; margin-top: 6px; }
  .subscribe-label { font-size: 10px; font-weight: 600; color: var(--dark); margin-bottom: 4px; text-transform: uppercase; }
  .subscribe-url {
    width: 100%; font-size: 10px; padding: 4px 6px; border: 1px solid var(--gray);
    border-radius: 3px; color: var(--text); cursor: pointer; background: var(--light-bg);
  }
  .subscribe-hint { font-size: 9px; color: #aaa; margin-top: 4px; }

  /* Day detail panel */
  .day-detail {
    margin-top: 14px; background: #fff; border: 2px solid var(--orange);
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 4px 20px rgba(244,162,97,0.12);
  }
  .detail-header {
    background: linear-gradient(135deg, var(--orange), #e8956a);
    color: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px;
  }
  .detail-header h3 { font-size: 18px; flex: 1; }
  .detail-meta { font-size: 12px; opacity: 0.95; }
  .detail-meta strong { color: #fff; }
  .close-btn {
    background: rgba(255,255,255,0.2); border: none; color: #fff;
    width: 28px; height: 28px; border-radius: 50%; cursor: pointer;
    font-size: 16px; display: flex; align-items: center; justify-content: center;
    transition: background 0.15s;
  }
  .close-btn:hover { background: rgba(255,255,255,0.35); }

  .detail-body { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 16px; }
  .detail-col h4 { font-size: 13px; font-weight: 700; color: var(--dark); margin-bottom: 8px;
    text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--yellow); padding-bottom: 4px; }
  .checklist { list-style: none; }
  .checklist li { position: relative; padding: 4px 0 4px 20px; font-size: 12px; line-height: 1.5; }
  .checklist li::before { content: '\2713'; position: absolute; left: 0; color: var(--green); font-weight: 700; }
  .savelist { list-style: none; }
  .savelist li { position: relative; padding: 4px 0 4px 20px; font-size: 12px; line-height: 1.5; }
  .savelist li::before { content: '\01F4BE'; position: absolute; left: 0; font-size: 11px; }

  .detail-events { padding: 0 16px 12px; }
  .detail-events h4 { font-size: 13px; font-weight: 700; color: var(--dark); margin-bottom: 8px;
    text-transform: uppercase; letter-spacing: 0.5px; }
  .event-card {
    display: flex; align-items: flex-start; gap: 8px; padding: 8px 10px;
    background: var(--light-bg); border-radius: 4px; margin-bottom: 6px;
    border-left: 3px solid var(--gray);
  }
  .event-card.type-hero { border-left-color: var(--hero); }
  .event-card.type-war { border-left-color: var(--war); }
  .event-card.type-alliance-event { border-left-color: var(--alliance); }
  .event-card.type-exclusive-weapon { border-left-color: var(--weapon); }
  .event-card.type-season-start { border-left-color: var(--season-clr); }
  .event-card.type-event { border-left-color: var(--event-clr); }
  .event-card.type-season { border-left-color: var(--season-clr); }
  .event-card strong { font-size: 12px; }
  .event-detail { font-size: 11px; color: #888; }

  .detail-radar { padding: 0 16px 16px; }
  .radar-tip {
    padding: 8px 12px; border-radius: 4px; font-size: 12px;
  }
  .radar-tip.collect { background: #e8f5e9; border-left: 3px solid var(--green); }
  .radar-tip.stack { background: #fff3e0; border-left: 3px solid var(--orange); }

  .vp-inline { font-weight: 800; padding: 1px 6px; border-radius: 3px; }
  .vp-inline.vp-1 { background: rgba(255,255,255,0.25); }
  .vp-inline.vp-2 { background: rgba(255,255,255,0.3); }
  .vp-inline.vp-3 { background: rgba(255,255,255,0.35); }
  .vp-inline.vp-4 { background: rgba(255,255,255,0.4); }

  /* Language Toggle */
  .lang-toggle {
    display: inline-flex; align-items: center; gap: 4px;
    background: #f0f5f4; border: 2px solid #7fb3a8; border-radius: 20px;
    padding: 2px 4px; cursor: pointer; font-family: 'Segoe UI', sans-serif;
    font-size: 12px; font-weight: 700; user-select: none;
    margin-right: 8px;
  }
  .lang-btn {
    padding: 2px 10px; border-radius: 16px; border: none; cursor: pointer;
    font-size: 12px; font-weight: 700; background: transparent; color: #888;
    transition: all 0.2s;
  }
  .lang-btn.active { background: #5a6a6a; color: #fff; }
  .lang-btn:hover:not(.active) { color: #5a6a6a; }

  /* Footer */
  .footer { text-align: center; font-size: 12px; color: #999; padding: 12px 8px 4px; margin-top: 16px; border-top: 1px solid #e0e0e0; }

  /* Responsive */
  @media (max-width: 900px) {
    .main-layout { flex-direction: column; }
    .sidebar { width: 100%; }
    .cal-cell { min-height: 70px; }
    .cell-phase { font-size: 8px; }
  }
  @media (max-width: 600px) {
    body { padding: 4px; overflow-x: hidden; }
    .guide-nav { margin: -4px -4px 8px -4px; padding: 4px 8px; gap: 3px 8px; font-size: 11px; }
    .top-bar h1 { font-size: 18px; }
    .config-bar { gap: 6px 10px; padding: 8px 10px; }
    .config-group label { font-size: 9px; }
    .config-group select, .config-group input[type="date"] { font-size: 12px; padding: 3px 4px; }
    .cal-header h2 { font-size: 16px; }
    .cal-weekdays div { font-size: 9px; letter-spacing: 0; }
    .cal-grid { gap: 1px; }
    .cal-cell { min-height: 48px; padding: 2px 2px; }
    .cal-cell.blank { min-height: 0; }
    .cell-day { font-size: 11px; }
    .cell-phase { font-size: 7px; max-width: 100%; }
    .cell-vp { font-size: 7px; padding: 0 3px; }
    .cell-dots { gap: 2px; }
    .dot { width: 6px; height: 6px; }
    .cell-radar { font-size: 9px; top: 1px; right: 1px; }
    .detail-body { grid-template-columns: 1fr; gap: 10px; padding: 12px; }
    .detail-header { flex-wrap: wrap; padding: 10px 12px; gap: 6px; }
    .detail-header h3 { font-size: 16px; width: 100%; }
    .detail-meta { font-size: 11px; flex: 1; }
    .close-btn { position: absolute; top: 8px; right: 8px; }
    .detail-header { position: relative; }
    .checklist li, .savelist li { font-size: 12px; }
    .detail-events { padding: 0 12px 10px; }
    .detail-radar { padding: 0 12px 12px; }
    .sidebar-section { padding: 10px; }
    .subscribe-url { font-size: 9px; }
  }
  @media (max-width: 380px) {
    .cal-cell { min-height: 42px; }
    .cell-phase { display: none; }
    .cell-radar { display: none; }
    .cell-vp { font-size: 7px; }
    .cal-weekdays div { font-size: 8px; }
  }
</style>'''


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timeline_path = os.path.join(script_dir, 'cpt_hedge_timeline.json')
    output_dir = os.path.join(script_dir, 'guides')
    os.makedirs(output_dir, exist_ok=True)

    timeline = load_timeline(timeline_path)
    schedule = get_weekly_schedule()

    timeline_json = json.dumps(timeline, separators=(',', ':'))
    schedule_json = json.dumps(schedule, separators=(',', ':'))

    # Generate HTML
    html = generate_html(timeline_json, schedule_json)
    html_path = os.path.join(output_dir, 'calendar.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {html_path}")

    # Generate static ICS for Server #2013
    ics_content = generate_ics(timeline, SERVER_2013_CREATION, reset_hour=18)
    ics_path = os.path.join(output_dir, 'lastwar_calendar.ics')
    with open(ics_path, 'w', encoding='utf-8', newline='') as f:
        f.write(ics_content)
    print(f"Generated: {ics_path}")
    print(f"Timeline events: {len(timeline)}")
    print(f"Weekly schedule: {len(schedule)} days")


if __name__ == "__main__":
    main()
