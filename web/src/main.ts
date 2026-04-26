import "./style.css";
import { startCommandCenter } from "./phaser/startCommandCenter";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="dot"></div>
        <div>
          <div class="title">EV Grid Oracle — Command Center</div>
          <div class="subtitle">Split-screen Baseline vs Oracle (Dream → Act)</div>
        </div>
      </div>

      <div class="controls">
        <button id="btnNew" class="btn">New</button>
        <button id="btnStep" class="btn">Step</button>
        <button id="btnRun" class="btn">Run 60 (cinematic)</button>
        <button id="btnJudge" class="btn">Judge Mode (MA)</button>

        <label class="label">
          Scenario
          <select id="scenario" class="input">
            <option value="baseline">baseline</option>
            <option value="heatwave_peak">heatwave_peak</option>
            <option value="festival_surge">festival_surge</option>
            <option value="transformer_derate">transformer_derate</option>
            <option value="station_outage">station_outage</option>
            <option value="tariff_shock">tariff_shock</option>
          </select>
        </label>

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
    </header>

    <div class="replayBar">
      <div class="replayTitle">City Ops Replay</div>
      <div class="replayRow">
        <input id="tick" class="range" type="range" min="0" max="0" value="0" disabled />
        <div class="replayMeta">
          <div>tick: <span id="tickLabel">0</span></div>
          <button id="btnPlay" class="btn small" type="button" disabled>Play</button>
        </div>
      </div>
      <div class="replayHint">
        Tip: after a few steps, scrub the timeline — it replays the recorded action sequence deterministically.
      </div>
    </div>

    <main class="main">
      <section class="game baselineGame">
        <div class="gameHeader">
          <div class="tag baseline">BASELINE</div>
          <div id="baselineBadge" class="pill">heuristic</div>
        </div>
        <div id="gameBaseline" style="width:100%; height:100%;"></div>
      </section>

      <section class="game oracleGame">
        <div class="gameHeader">
          <div class="tag oracle">ORACLE</div>
          <div id="oracleBadge" class="pill warn">loading…</div>
        </div>
        <div id="gameOracle" style="width:100%; height:100%;"></div>
      </section>

      <aside class="rail">
        <div class="card">
          <div class="cardTitle">KPI Delta (Oracle − Baseline)</div>
          <div class="kpis">
            <div class="kpiRow"><div>Avg wait (min)</div><div id="kpiWait" class="kpiVal">—</div></div>
            <div class="kpiRow"><div>Peak violations</div><div id="kpiPeak" class="kpiVal">—</div></div>
            <div class="kpiRow"><div>Grid stress events</div><div id="kpiStress" class="kpiVal">—</div></div>
            <div class="kpiRow"><div>Renewable mean</div><div id="kpiRen" class="kpiVal">—</div></div>
            <div class="kpiRow"><div>Dream accuracy</div><div id="kpiDream" class="kpiVal">—</div></div>
          </div>
        </div>

        <div class="card">
          <div class="cardTitle">Dream vs Reality (T+5)</div>
          <pre id="dream" class="mono">(waiting)</pre>
        </div>

        <div class="card">
          <div class="cardTitle">Oracle Action + Reward</div>
          <pre id="oracle" class="mono">(waiting)</pre>
        </div>

        <div class="card">
          <div class="cardTitle">Event Stream</div>
          <pre id="events" class="mono">(none)</pre>
        </div>

        <div class="card">
          <div class="cardTitle">Negotiation (Multi-Agent)</div>
          <pre id="nego" class="mono">(click Judge Mode)</pre>
        </div>
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
  scenarioEl: document.querySelector<HTMLSelectElement>("#scenario")!,
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
