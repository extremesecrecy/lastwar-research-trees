#!/usr/bin/env python
"""Build script for plunder_guide.html - generates self-contained HTML with embedded images."""
import base64, os

IMG_DIR = os.path.join(os.path.dirname(__file__), 'pictures', 'Plunder')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'guides', 'plunder_guide.html')

# Load and base64-encode images
imgs = {}
for f in os.listdir(IMG_DIR):
    if f.endswith('.png'):
        path = os.path.join(IMG_DIR, f)
        with open(path, 'rb') as fh:
            data = base64.b64encode(fh.read()).decode()
            key = f.replace('.png', '').replace(' ', '_')
            imgs[key] = f'data:image/png;base64,{data}'

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plunder Guide - OWOW</title>
<style>
@import url("https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap");
  }
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #fff;
    color: #333;
    padding: 8px 16px;
    max-width: 900px;
    margin: 0 auto;
  }}
  h1, h2, h3, .section-label {{
    font-family: 'Fredoka', 'Segoe UI', sans-serif;
  }}

  /* Nav */
  .guide-nav {{
    display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: center;
    padding: 6px 16px; background: #f0f5f4; border-bottom: 2px solid #7fb3a8;
    font-size: 12px; margin: -8px -16px 16px -16px;
    width: 100vw; position: relative; left: 50%; transform: translateX(-50%);
  }}
  .guide-nav a {{ color: #5a6a6a; text-decoration: none; padding: 2px 6px; border-radius: 3px; white-space: nowrap; }}
  .guide-nav a:hover {{ color: #f4a261; background: #fff; }}
  .guide-nav a.current {{ color: #f4a261; font-weight: bold; background: #fff; border: 1px solid #f4a261; }}
  .guide-nav .nav-home {{ font-weight: bold; margin-right: 8px; padding-right: 12px; border-right: 1px solid #7fb3a8; }}
  @media (max-width: 480px) {{
    .guide-nav {{ padding: 4px 8px; gap: 3px 8px; font-size: 11px; }}
  }}

  /* Header */
  .header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 16px; padding-bottom: 8px; border-bottom: 3px solid #e53935;
  }}
  .header h1 {{ font-size: 28px; letter-spacing: 1px; text-transform: uppercase; color: #5a6a6a; }}
  .header .sub {{ font-size: 16px; color: #888; margin-top: 2px; }}
  .alliance {{
    background: #e8f4f1; border: 1px solid #7fb3a8; border-radius: 5px;
    padding: 4px 12px; text-align: right;
  }}
  .alliance .name {{ font-size: 19px; font-weight: 800; color: #5a6a6a; }}
  .alliance .info {{ font-size: 14px; color: #666; }}

  /* Warning banner */
  .warning-banner {{
    background: #fce4ec; border: 3px solid #e53935; border-radius: 8px;
    padding: 14px 18px; margin-bottom: 20px; text-align: center;
  }}
  .warning-banner .icon {{ font-size: 32px; margin-bottom: 4px; }}
  .warning-banner h2 {{ color: #c62828; font-size: 22px; margin-bottom: 4px; }}
  .warning-banner p {{ font-size: 15px; color: #333; line-height: 1.5; }}
  .warning-banner strong {{ color: #c62828; }}

  /* Info box */
  .info-box {{
    background: #e4f3f8; border: 2px solid #5bc0de; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 20px;
  }}
  .info-box h3 {{ color: #2a8fa8; font-size: 18px; margin-bottom: 6px; }}
  .info-box p, .info-box li {{ font-size: 14px; line-height: 1.6; }}
  .info-box ul {{ margin-left: 18px; }}

  /* Step sections */
  .step {{
    margin-bottom: 24px; padding: 16px; border-radius: 8px;
    border: 2px solid #ddd; background: #fafafa;
  }}
  .step-header {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
  }}
  .step-number {{
    background: #5a6a6a; color: #fff; width: 36px; height: 36px;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 18px; flex-shrink: 0;
    font-family: 'Fredoka', sans-serif;
  }}
  .step-number.red {{ background: #e53935; }}
  .step-number.orange {{ background: #f4a261; }}
  .step-number.cyan {{ background: #5bc0de; }}
  .step-number.teal {{ background: #7fb3a8; }}
  .step-number.green {{ background: #43a047; }}
  .step h2 {{ font-size: 20px; color: #5a6a6a; text-transform: uppercase; }}
  .step p, .step li {{ font-size: 14px; line-height: 1.6; }}
  .step ul, .step ol {{ margin: 8px 0 8px 18px; }}

  /* Screenshot container */
  .screenshot {{
    margin: 12px 0; text-align: center;
  }}
  .screenshot img {{
    max-width: 340px; width: 100%; border-radius: 8px;
    border: 2px solid #ddd; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }}
  .screenshot .caption {{
    font-size: 12px; color: #888; margin-top: 4px; font-style: italic;
  }}

  /* Highlight boxes */
  .tip-box {{
    background: #fef3e2; border: 2px solid #f4a261; border-radius: 6px;
    padding: 10px 14px; margin: 10px 0;
  }}
  .tip-box .label {{ font-weight: 800; color: #c47a30; font-size: 14px; }}
  .tip-box p {{ font-size: 14px; margin-top: 4px; }}

  .critical-box {{
    background: #fce4ec; border: 2px solid #e53935; border-radius: 6px;
    padding: 10px 14px; margin: 10px 0;
  }}
  .critical-box .label {{ font-weight: 800; color: #c62828; font-size: 14px; }}
  .critical-box p {{ font-size: 14px; margin-top: 4px; }}

  .success-box {{
    background: #e8f5e9; border: 2px solid #43a047; border-radius: 6px;
    padding: 10px 14px; margin: 10px 0;
  }}
  .success-box .label {{ font-weight: 800; color: #2e7d32; font-size: 14px; }}
  .success-box p {{ font-size: 14px; margin-top: 4px; }}

  /* Priority table */
  .priority-table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin: 10px 0; }}
  .priority-table th {{ background: #5a6a6a; color: #fff; padding: 6px 10px; text-align: left; font-size: 13px; text-transform: uppercase; }}
  .priority-table td {{ padding: 6px 10px; border-bottom: 1px solid #e8e8e8; }}
  .priority-table tr:nth-child(even) {{ background: #f5f8f7; }}
  .priority-table .ur {{ color: #c62828; font-weight: 700; }}
  .priority-table .ssr {{ color: #9c27b0; font-weight: 700; }}

  /* Rarity badges */
  .badge {{ display: inline-block; padding: 1px 8px; border-radius: 3px; font-size: 12px; font-weight: 700; color: #fff; }}
  .badge-ur {{ background: #c62828; }}
  .badge-ssr {{ background: #9c27b0; }}
  .badge-sr {{ background: #1565c0; }}
  .badge-r {{ background: #43a047; }}

  /* Footer */
  .footer {{
    text-align: center; padding: 16px 0; margin-top: 24px;
    border-top: 2px solid #7fb3a8; color: #888; font-size: 13px;
  }}
  .footer .motto {{ font-family: 'Fredoka', sans-serif; font-size: 16px; color: #5a6a6a; margin-bottom: 4px; }}

  /* Quick ref */
  .quick-ref {{
    background: #fdf8e8; border: 2px solid #f4d35e; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 20px;
  }}
  .quick-ref h3 {{ color: #d4a017; font-size: 18px; margin-bottom: 8px; }}
  .quick-ref li {{ font-size: 14px; line-height: 1.6; }}
  .quick-ref ul {{ margin-left: 18px; }}

  /* Responsive */
  @media (max-width: 600px) {{
    body {{ padding: 6px 10px; }}
    .header {{ flex-direction: column; text-align: center; gap: 8px; }}
    .header h1 {{ font-size: 22px; }}
    .alliance {{ text-align: center; }}
    .step h2 {{ font-size: 17px; }}
    .screenshot img {{ max-width: 280px; }}
    .warning-banner h2 {{ font-size: 18px; }}
  }}
</style>
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
  <a href="calendar.html">Calendar</a>
  <a href="hero_planner.html">Hero Planner</a>
  <a href="plunder_guide.html" class="current">Plunder</a>
  <a href="radar_guide.html">Radar</a>
  <a href="../research_trees_visual.html">Research Trees</a>
  <a href="server_dashboard.html">Server</a>
  <a href="vs_weekly_planner.html">VS Planner</a>
  <a href="waterfall_guide.html">Waterfall</a>
</nav>

<!-- HEADER -->
<div class="header">
  <div>
    <h1>Plunder Guide</h1>
    <div class="sub">Cross-Server Truck Raiding &mdash; Step by Step</div>
  </div>
  <div class="alliance">
    <img src="skynet_logo.png" alt="OWOW" style="height:50px;vertical-align:middle;margin-right:6px;">
    <div class="name">[OWOW] Old World Order</div>
    <div class="info">SKYNET Strategic Division</div>
  </div>
</div>

<!-- WARNING BANNER -->
<div class="warning-banner">
  <div class="icon">&#9888;&#65039;</div>
  <h2>NEVER Plunder Your Own Server!</h2>
  <p>Plundering alliance members or players on <strong>your own server</strong> creates enemies, breaks trust, and can lead to retaliation against you AND your alliance.<br>
  <strong>ALWAYS travel to another warzone</strong> before plundering. The filter checkbox exists for this reason &mdash; use it every single time!</p>
</div>

<!-- QUICK REFERENCE -->
<div class="quick-ref">
  <h3>Quick Reference</h3>
  <ul>
    <li><strong>Truck plunder limit:</strong> 4 truck plunders per day (resets at server reset)</li>
    <li><strong>Task plunder limit:</strong> 5 secret task plunders per day (SEPARATE from trucks!)</li>
    <li><strong>Each truck can be plundered:</strong> up to 2 times total by different players</li>
    <li><strong>Each task can be plundered:</strong> up to 3 times total, but only 1 time per player</li>
    <li><strong>Priority targets:</strong> <span class="badge badge-ur">UR</span> trucks and tasks &gt; <span class="badge badge-ssr">SSR</span> &gt; <span class="badge badge-sr">SR</span></li>
    <li><strong>Best time to plunder:</strong> Right after daily reset when fresh trucks are dispatched</li>
    <li><strong>Dispatching UR trucks</strong> scores VS points on Tuesday (Base Expansion) and Saturday (Enemy Buster)</li>
    <li><strong>Plunder target list:</strong> Can be refreshed for FREE &mdash; keep refreshing until you find UR targets</li>
  </ul>
</div>

<!-- WHAT IS PLUNDERING -->
<div class="info-box">
  <h3>What is Plundering?</h3>
  <p>When players dispatch trade trucks from their Truck Station, those trucks travel along a route visible to other players. You can <strong>plunder</strong> (raid) these trucks to steal bonus resources, speedups, hero shards, and other valuable items.</p>
  <p style="margin-top:6px;">You can also plunder <strong>secret tasks</strong> that appear as crate clusters on the world map.</p>
  <p style="margin-top:6px;">The golden rule: <strong>only plunder trucks and tasks on OTHER servers</strong>, never your own warzone.</p>
</div>

<!-- PRIORITY TABLE -->
<div class="info-box" style="border-color: #f4a261; background: #fef3e2;">
  <h3 style="color: #c47a30;">Plunder Target Priority</h3>
  <table class="priority-table">
    <thead>
      <tr><th>Rarity</th><th>Visual Indicator</th><th>Reward Quality</th><th>Priority</th></tr>
    </thead>
    <tbody>
      <tr><td class="ur">UR (Legendary)</td><td>Gold background glow</td><td>Best &mdash; hero shards, legendary items, speedups</td><td><strong>ALWAYS plunder these first!</strong></td></tr>
      <tr><td class="ssr">SSR (Epic)</td><td>Purple background glow</td><td>Good &mdash; quality resources, gear materials</td><td>Plunder if no UR available</td></tr>
      <tr><td style="color:#1565c0;font-weight:700;">SR (Rare)</td><td>Blue background glow</td><td>Decent &mdash; moderate resources</td><td>Only if nothing better</td></tr>
      <tr><td style="color:#43a047;font-weight:700;">R (Rare)</td><td>Green background</td><td>Low &mdash; basic resources</td><td>Skip if possible</td></tr>
      <tr><td style="color:#888;font-weight:700;">N (Normal)</td><td>Gray background</td><td>Minimal &mdash; barely worth it</td><td>Never plunder these</td></tr>
    </tbody>
  </table>
</div>

<!-- STEP 1: TRUCK STATION -->
<div class="step" style="border-color: #5bc0de;">
  <div class="step-header">
    <div class="step-number cyan">1</div>
    <h2>Open Your Truck Station</h2>
  </div>
  <p>Find the <strong>Truck Station</strong> building on your base. It looks like a train depot with railroad tracks and a clock tower. Tap it to open the truck interface.</p>
  <p style="margin-top:6px;">This is your hub for dispatching your own trucks AND plundering other players.</p>
  <div class="screenshot">
    <img src="{imgs['TruckStation']}" alt="Truck Station building on your base">
    <div class="caption">The Truck Station building on your base &mdash; tap to open</div>
  </div>
  <div class="tip-box">
    <div class="label">DISPATCH YOUR OWN TRUCKS FIRST!</div>
    <p>Before plundering, always dispatch your own trucks. F2P players get <strong>3 free truck dispatches</strong> per day (4th slot with Monthly Pass, 5th with Intercity Truck research). Use your 1 free refresh per slot (dice button), or spend Trade Contracts for additional refreshes, until you see a <span class="badge badge-ur">UR</span> (Legendary/gold background) truck, then send it. UR trucks earn the best rewards AND complete fastest.</p>
  </div>
</div>

<!-- STEP 2: GO TO OTHERS' TRUCKS -->
<div class="step" style="border-color: #f4a261;">
  <div class="step-header">
    <div class="step-number orange">2</div>
    <h2>Go to "Others' Trucks" Tab</h2>
  </div>
  <p>Once inside the Truck Station, look at the <strong>bottom of the screen</strong>. You will see two tabs:</p>
  <ul>
    <li><strong>"Others' Trucks"</strong> (left tab) &mdash; Shows trucks from other players that you can plunder</li>
    <li><strong>"Your Truck"</strong> (right tab) &mdash; Shows your own dispatched trucks and their status</li>
  </ul>
  <p style="margin-top:8px;">Tap <strong>"Others' Trucks"</strong> to browse available plunder targets. You will see a road with colorful trucks parked along it &mdash; each one belongs to a player.</p>
  <div class="screenshot">
    <img src="{imgs['Look_at_Trucks']}" alt="Others Trucks tab showing available trucks to plunder">
    <div class="caption">The "Others' Trucks" view &mdash; each truck on the road is a potential plunder target</div>
  </div>
  <p style="margin-top:8px;">At the top of this screen you can see <strong>"Your Plunder Count Today: X/4"</strong> &mdash; this tells you how many of your 4 daily truck plunders you have used. (Secret task plunders have a separate 5/day limit.)</p>
</div>

<!-- STEP 3: ENABLE THE FILTER -->
<div class="step" style="border-color: #e53935;">
  <div class="step-header">
    <div class="step-number red">3</div>
    <h2>Enable the Warzone Filter</h2>
  </div>
  <div class="critical-box">
    <div class="label">CRITICAL &mdash; THIS IS THE MOST IMPORTANT STEP!</div>
    <p>At the top of the trucks screen, find the checkbox labeled <strong>"Filter out trucks from your Warzone"</strong>. This <strong>MUST</strong> be checked (green checkmark visible). When enabled, it hides ALL trucks from your own server &mdash; you will ONLY see trucks from other servers that are safe to plunder.</p>
  </div>
  <div class="screenshot">
    <img src="{imgs['Make_Sure_Filter_is_Checked']}" alt="Filter checkbox must be checked">
    <div class="caption">The filter checkbox &mdash; green checkmark means it is ON. ALWAYS keep this checked!</div>
  </div>
  <p>With the filter enabled, <strong>every single truck you see</strong> belongs to a player on a different server. You are safe to plunder any of them without consequence to your own alliance or server relationships.</p>
  <div class="tip-box">
    <div class="label">WHY THIS MATTERS</div>
    <p>If you accidentally plunder someone on your own server, they will see your name in the notification. This creates enemies, invites retaliation against you personally, and can damage your alliance's reputation. <strong>Check the filter every single time you open this screen. No exceptions.</strong></p>
  </div>
</div>

<!-- STEP 4: VERIFY WARZONE -->
<div class="step" style="border-color: #7fb3a8;">
  <div class="step-header">
    <div class="step-number teal">4</div>
    <h2>Verify You Are on Another Server</h2>
  </div>
  <p>When you tap on a truck to view it on the map, you will be taken to the world map of that player's warzone. Always <strong>double-check the banner at the top of the screen</strong> which shows the current warzone number.</p>
  <div class="screenshot">
    <img src="{imgs['Check_Warzone']}" alt="Warzone banner showing server number">
    <div class="caption">The warzone banner confirms you are viewing Server #2015 &mdash; NOT your home server</div>
  </div>
  <p>If the banner shows <strong>any server number other than your own</strong>, you are safe to plunder.</p>
  <div class="success-box">
    <div class="label">DOUBLE CHECK</div>
    <p>The banner shows "Warzone #2015" &mdash; this is not our home server. Safe to plunder! The two buttons on the banner let you view warzone info (i) or return to your home server (arrow).</p>
  </div>
</div>

<!-- STEP 5: TAP A TRUCK -->
<div class="step" style="border-color: #5bc0de;">
  <div class="step-header">
    <div class="step-number cyan">5</div>
    <h2>Tap a Truck &amp; Inspect Details</h2>
  </div>
  <p>Tap on any truck along the road to open its <strong>detail popup</strong>. This is where you decide whether the truck is worth one of your precious 4 daily plunders. The popup shows:</p>
  <ul>
    <li><strong>Player name, server, and alliance tag</strong> &mdash; confirms they are from another server</li>
    <li><strong>Times plundered: X/2</strong> &mdash; each truck can be plundered a maximum of 2 times by different players. If it says <strong>2/2</strong>, it is fully plundered &mdash; skip it!</li>
    <li><strong>Next Station timer</strong> &mdash; how long until the truck reaches its next stop</li>
    <li><strong>Your Plunder Count Today: X/4</strong> &mdash; your remaining daily truck plunders</li>
    <li><strong>"Details" button</strong> &mdash; tap to see the exact rewards before committing</li>
  </ul>
  <div class="screenshot">
    <img src="{imgs['Plunder_the_truck']}" alt="Truck detail popup showing plunder info">
    <div class="caption">The truck detail popup &mdash; check "Times plundered" and tap "Details" to preview rewards</div>
  </div>
  <div class="tip-box">
    <div class="label">WHAT TO LOOK FOR</div>
    <p>Prioritize trucks with <strong>0/2 plunders</strong> (untouched = maximum rewards). Look for <span class="badge badge-ur">UR</span> trucks with gold glow &mdash; they have the best loot. Always tap "Details" to see exactly what you will receive before using a plunder charge.</p>
  </div>
</div>

<!-- STEP 6: PRESS PLUNDER -->
<div class="step" style="border-color: #43a047;">
  <div class="step-header">
    <div class="step-number green">6</div>
    <h2>Review Rewards &amp; Press Plunder!</h2>
  </div>
  <p>After tapping "Details" on a truck, the <strong>plunder confirmation screen</strong> appears. This is the final screen before you commit. It shows everything you need to make your decision:</p>
  <ul>
    <li><strong>Arrival countdown timer</strong> (top) &mdash; time remaining on the truck's route</li>
    <li><strong>Target player info</strong> &mdash; their server number, alliance tag, player name, level, and total power</li>
    <li><strong>Player avatar</strong> &mdash; their profile picture</li>
    <li><strong>Plunder reward icons</strong> (bottom) &mdash; the exact items you will receive: badges, chests, supplies, materials, etc. The number below each icon is the quantity.</li>
    <li><strong>Red "Plunder!" button</strong> &mdash; tap this to execute the plunder and claim your rewards</li>
  </ul>
  <div class="screenshot">
    <img src="{imgs['Press_Plunder']}" alt="Plunder confirmation with rewards and Plunder button">
    <div class="caption">Review rewards carefully, then hit the red "Plunder!" button to claim them</div>
  </div>
  <div class="success-box">
    <div class="label">PLUNDER COMPLETE!</div>
    <p>Rewards are instantly added to your inventory. You have used 1 of your 4 daily plunder charges. Go back to the truck list and repeat until all 4 are used!</p>
  </div>
</div>

<!-- STEP 7: PLUNDER TASKS -->
<div class="step" style="border-color: #f4d35e;">
  <div class="step-header">
    <div class="step-number" style="background:#d4a017;">7</div>
    <h2>Plunder Secret Tasks (Bonus Targets!)</h2>
  </div>
  <p>In addition to trucks, you can also plunder <strong>secret tasks</strong> that appear on the world map in other warzones. These show up as <strong>clusters of orange/gold crates</strong> sitting on the terrain, with the owner's name above them.</p>
  <div class="screenshot">
    <img src="{imgs['Plunder_a_Task']}" alt="Secret task plunder target on the map">
    <div class="caption">A secret task target on another server &mdash; plunder rewards shown below the player name</div>
  </div>
  <p style="margin-top:8px;">How to plunder secret tasks:</p>
  <ol>
    <li>Travel to <strong>another warzone</strong> (not your home server!)</li>
    <li><strong>Check the warzone banner at the top of the screen</strong> &mdash; confirm it shows a different server number than yours. This is just as critical for tasks as it is for trucks!</li>
    <li>Find crate clusters on the world map &mdash; look for the gold glow on <span class="badge badge-ur">UR</span> tasks</li>
    <li>Tap the crates to see the owner, their server, and the plunder rewards</li>
    <li>Tap plunder to claim the rewards</li>
  </ol>
  <div class="critical-box">
    <div class="label">CHECK THE WARZONE BEFORE PLUNDERING TASKS!</div>
    <p>The same rule applies to tasks as trucks: <strong>ALWAYS verify the warzone banner</strong> shows a server number different from yours before plundering any task. Tasks on your own server belong to your neighbors &mdash; plundering them creates enemies.</p>
  </div>
  <div class="critical-box">
    <div class="label">IMPORTANT</div>
    <p>Task plunders have their OWN separate daily limit: <strong>5 task plunders per day</strong>, completely independent from your 4 truck plunders. Each task can be plundered up to <strong>3 times total</strong> by different players, but you can only plunder the same task <strong>once</strong>.</p>
  </div>
  <div class="tip-box">
    <div class="label">PRIORITIZE UR TASKS</div>
    <p>Just like trucks, tasks come in different rarities. <span class="badge badge-ur">UR</span> (Legendary) tasks have the best rewards &mdash; look for the distinctive gold glow around the crates. If you spot a UR task, plunder it immediately before someone else does!</p>
  </div>
</div>

<!-- DAILY PLUNDER CHECKLIST -->
<div class="info-box" style="border-color:#7fb3a8; background:#e8f4f1;">
  <h3 style="color:#5a8a7e;">Daily Plunder Checklist</h3>
  <ol style="margin-left:18px;font-size:14px;line-height:1.8;">
    <li><strong>Dispatch your own trucks first</strong> &mdash; refresh until you get a <span class="badge badge-ur">UR</span> truck, then send it</li>
    <li>Open Truck Station &rarr; tap the <strong>"Others' Trucks"</strong> tab</li>
    <li>Check the <strong>"Filter out trucks from your Warzone"</strong> checkbox &mdash; make sure it is ON</li>
    <li>Browse the truck list &mdash; look for <span class="badge badge-ur">UR</span> trucks with <strong>0/2</strong> plunders</li>
    <li>Tap a truck &rarr; tap <strong>"Details"</strong> to preview rewards</li>
    <li>Verify the warzone banner shows a <strong>different server number</strong></li>
    <li>Press the red <strong>"Plunder!"</strong> button to claim rewards</li>
    <li>Repeat steps 4-7 until all <strong>4 daily truck plunders</strong> are used</li>
    <li>Then travel to another warzone &mdash; <strong>check the warzone banner!</strong> &mdash; and use your <strong>5 daily task plunders</strong> on <span class="badge badge-ur">UR</span> secret tasks (separate limit from trucks!)</li>
  </ol>
</div>

<!-- FOOTER -->
<div class="footer">
  <div class="motto">Kristen OWOW SKYNET. Ready for Judgment Day.</div>
  <div>[OWOW] Old World Order</div>
  <div>Last War: Survival &mdash; Plunder Guide v1.0</div>
</div>

</body>
</html>'''

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(OUT_PATH) / 1024
print(f'Written: {OUT_PATH} ({size_kb:.0f}KB)')
