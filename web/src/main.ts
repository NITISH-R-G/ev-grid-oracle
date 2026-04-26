import "./style.css";
import { startCommandCenter } from "./phaser/startCommandCenter";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="dot"></div>
        <div>
          <div class="title glitch" data-text="EV Grid Oracle — Command Center">EV Grid Oracle — Command Center</div>
          <div class="subtitle">A/B live: heuristic baseline vs GRPO-trained Oracle (Dream → Act)</div>
        </div>
      </div>

      <div class="controls">
        <div class="controlCluster primary">
          <button id="btnNew" class="btn primary">New</button>
          <button id="btnStep" class="btn">Step</button>
          <button id="btnRun" class="btn">Run 60</button>
          <button id="btnDemo" class="btn glow">Guided Demo</button>
          <button id="btnJudge" class="btn">Judge Mode</button>
        </div>

        <label class="label">
          Scenario
          <select id="scenario" class="input">
            <option value="baseline">baseline</option>
            <option value="heatwave_peak">heatwave_peak</option>
            <option value="festival_surge">festival_surge</option>
            <option value="transformer_derate">transformer_derate</option>
            <option value="station_outage">station_outage</option>
            <option value="tariff_shock">tariff_shock</option>
            <option value="MonsoonStorm">MonsoonStorm</option>
            <option value="CricketFinal">CricketFinal</option>
            <option value="AirportRush">AirportRush</option>
            <option value="SilkBoardJam">SilkBoardJam</option>
            <option value="WhitefieldNight">WhitefieldNight</option>
          </select>
        </label>

        <label class="label">
          Fleet
          <select id="fleetMode" class="input">
            <option value="mixed" selected>mixed</option>
            <option value="taxi">taxi</option>
            <option value="corporate">corporate</option>
            <option value="delivery">delivery</option>
            <option value="private">private</option>
            <option value="emergency">emergency</option>
          </select>
        </label>

        <details class="advanced">
          <summary class="btn ghost">Advanced</summary>
          <div class="advancedGrid">
            <label class="label">
              Seed
              <input id="seed" class="input narrow" type="number" min="0" max="1000000" value="123" />
            </label>

            <label class="label">
              Follow EV
              <input id="follow" type="checkbox" />
            </label>

            <label class="label wide">
              Oracle LoRA repo
              <input id="lora" class="input" placeholder="NITISHRG15102007/ev-oracle-lora" />
            </label>
          </div>
        </details>
      </div>
    </header>

    <div class="heroStrip" id="heroStrip">
      <div class="heroLeft">
        <div class="heroEyebrow">Oracle Advantage</div>
        <div class="heroHeadline">
          <span id="heroMain" class="heroMain">—</span>
          <span id="heroMainUnit" class="heroUnit">avg wait</span>
        </div>
        <div id="heroSub" class="heroSub">Click Step twice. Watch the “WIN” badge lock in. Then Run 60 for the cinematic proof.</div>
      </div>
      <div class="heroRight">
        <div class="heroMini">
          <div class="miniLabel">Peak</div>
          <div id="heroPeak" class="miniVal">—</div>
        </div>
        <div class="heroMini">
          <div class="miniLabel">Stress</div>
          <div id="heroStress" class="miniVal">—</div>
        </div>
        <div class="heroMini">
          <div class="miniLabel">Renew</div>
          <div id="heroRen" class="miniVal">—</div>
        </div>
        <div class="heroMini">
          <div class="miniLabel">Dream</div>
          <div id="heroDream" class="miniVal">—</div>
        </div>
        <div id="heroVerdict" class="heroVerdict">READY</div>
      </div>
    </div>

    <div class="replayBar">
      <div class="replayTitle">City Ops Replay</div>
      <div class="replayRow">
        <input id="tick" class="range" type="range" min="0" max="0" value="0" disabled />
        <div class="replayMeta">
          <div>tick: <span id="tickLabel">0</span></div>
          <button id="btnPlay" class="btn small" type="button" disabled>Play</button>
        </div>
      </div>
      <div class="replayHint">Tip: scrub the timeline to replay the recorded action sequence deterministically.</div>
    </div>

    <main class="main">
      <section id="baselinePanel" class="game baselineGame">
        <div class="gameHeader hudHeader">
          <div class="tag baseline hudTag"><span class="hudIcon danger">⚡</span> BASELINE</div>
          <div id="baselineBadge" class="pill hudPill">heuristic</div>
        </div>
        <div id="gameBaseline" style="width:100%; height:100%;"></div>
      </section>

      <section id="oraclePanel" class="game oracleGame">
        <div class="gameHeader hudHeader">
          <div class="tag oracle hudTag"><span class="hudIcon good">★</span> ORACLE</div>
          <div id="oracleBadge" class="pill warn hudPill">loading…</div>
        </div>
        <div id="gameOracle" style="width:100%; height:100%;"></div>
      </section>

      <aside class="rail">
        <div class="card hudCard">
          <div class="cardTitle hudTitle"><span class="hudIcon info">▣</span> KPI Delta (Oracle − Baseline)</div>
          <div class="kpis hudKpis">
            <div class="kpiRow hudKpiRow">
              <div class="kpiLeft"><span class="kpiIcon">⏱</span><div>Avg wait</div></div>
              <div class="kpiRight">
                <div class="kpiBar"><div id="kpiWaitBar" class="kpiBarFill"></div></div>
                <div id="kpiWait" class="kpiVal">—</div>
              </div>
            </div>
            <div class="kpiRow hudKpiRow">
              <div class="kpiLeft"><span class="kpiIcon">⚠</span><div>Peak violations</div></div>
              <div class="kpiRight">
                <div class="kpiBar"><div id="kpiPeakBar" class="kpiBarFill"></div></div>
                <div id="kpiPeak" class="kpiVal">—</div>
              </div>
            </div>
            <div class="kpiRow hudKpiRow">
              <div class="kpiLeft"><span class="kpiIcon">⚡</span><div>Grid stress</div></div>
              <div class="kpiRight">
                <div class="kpiBar"><div id="kpiStressBar" class="kpiBarFill"></div></div>
                <div id="kpiStress" class="kpiVal">—</div>
              </div>
            </div>
            <div class="kpiRow hudKpiRow">
              <div class="kpiLeft"><span class="kpiIcon">☀</span><div>Renewable</div></div>
              <div class="kpiRight">
                <div class="kpiBar"><div id="kpiRenBar" class="kpiBarFill"></div></div>
                <div id="kpiRen" class="kpiVal">—</div>
              </div>
            </div>
            <div class="kpiRow hudKpiRow">
              <div class="kpiLeft"><span class="kpiIcon">✦</span><div>Dream acc</div></div>
              <div class="kpiRight">
                <div class="kpiBar"><div id="kpiDreamBar" class="kpiBarFill"></div></div>
                <div id="kpiDream" class="kpiVal">—</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card hudCard">
          <div class="cardTitle hudTitle"><span class="hudIcon oracle">☾</span> Dream vs Reality (T+5)</div>
          <pre id="dream" class="mono">(waiting)</pre>
        </div>

        <div class="card hudCard">
          <div class="cardTitle hudTitle"><span class="hudIcon good">◆</span> Oracle Action + Reward</div>
          <pre id="oracle" class="mono">(waiting)</pre>
        </div>

        <details class="card hudCard collapsible">
          <summary class="cardTitle hudTitle">Explain / Debug (Event Stream)</summary>
          <pre id="events" class="mono">(none)</pre>
        </details>

        <details class="card hudCard collapsible">
          <summary class="cardTitle hudTitle">Judge Mode Transcript (Multi-Agent)</summary>
          <pre id="nego" class="mono">(click Judge Mode)</pre>
        </details>
      </aside>
    </main>
  </div>
`;

{
  const lora = document.querySelector<HTMLInputElement>("#lora")!;
  lora.value = "NITISHRG15102007/ev-oracle-lora";
  lora.title =
    "Hugging Face repo id for LoRA (exact spelling). Common typo: NITISHGR… — correct is NITISHRG… (HR).";
}

startCommandCenter({
  baselineMountId: "gameBaseline",
  oracleMountId: "gameOracle",
  btnNew: document.querySelector<HTMLButtonElement>("#btnNew")!,
  btnStep: document.querySelector<HTMLButtonElement>("#btnStep")!,
  btnRun: document.querySelector<HTMLButtonElement>("#btnRun")!,
  btnDemo: document.querySelector<HTMLButtonElement>("#btnDemo")!,
  scenarioEl: document.querySelector<HTMLSelectElement>("#scenario")!,
  fleetEl: document.querySelector<HTMLSelectElement>("#fleetMode")!,
  seedEl: document.querySelector<HTMLInputElement>("#seed")!,
  tickEl: document.querySelector<HTMLInputElement>("#tick")!,
  tickLabelEl: document.querySelector<HTMLSpanElement>("#tickLabel")!,
  btnPlay: document.querySelector<HTMLButtonElement>("#btnPlay")!,
  followEl: document.querySelector<HTMLInputElement>("#follow")!,
  loraEl: document.querySelector<HTMLInputElement>("#lora")!,
  baselineBadge: document.querySelector<HTMLDivElement>("#baselineBadge")!,
  oracleBadge: document.querySelector<HTMLDivElement>("#oracleBadge")!,
  kpiWait: document.querySelector<HTMLDivElement>("#kpiWait")!,
  kpiPeak: document.querySelector<HTMLDivElement>("#kpiPeak")!,
  kpiStress: document.querySelector<HTMLDivElement>("#kpiStress")!,
  kpiRen: document.querySelector<HTMLDivElement>("#kpiRen")!,
  kpiDream: document.querySelector<HTMLDivElement>("#kpiDream")!,
  dreamEl: document.querySelector<HTMLPreElement>("#dream")!,
  oracleEl: document.querySelector<HTMLPreElement>("#oracle")!,
  eventsEl: document.querySelector<HTMLPreElement>("#events")!,
  negoEl: document.querySelector<HTMLPreElement>("#nego")!,
  btnJudge: document.querySelector<HTMLButtonElement>("#btnJudge")!,
});
