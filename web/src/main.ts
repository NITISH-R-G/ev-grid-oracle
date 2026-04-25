import "./style.css";
import { startGame } from "./phaser/startGame";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="dot"></div>
        <div>
          <div class="title">EV Grid Oracle</div>
          <div class="subtitle">Pixel City — live simulation</div>
        </div>
      </div>

      <div class="controls">
        <button id="btnNew" class="btn">New</button>
        <button id="btnStep" class="btn">Step</button>
        <button id="btnRun" class="btn">Run 60</button>

        <label class="label">
          Mode
          <select id="mode" class="select">
            <option value="baseline">Baseline</option>
            <option value="oracle">Oracle</option>
          </select>
        </label>

        <label class="label">
          Follow EV
          <input id="follow" type="checkbox" />
        </label>

        <label class="label wide">
          LoRA repo
          <input id="lora" class="input" placeholder="NITISHRG15102007/ev-oracle-lora" />
        </label>
      </div>
    </header>

    <main class="main">
      <div id="game" class="game"></div>
      <aside class="side">
        <div class="card">
          <div class="cardTitle">Status</div>
          <pre id="status" class="mono">Starting…</pre>
        </div>
        <div class="card">
          <div class="cardTitle">Last event</div>
          <pre id="event" class="mono">(none)</pre>
        </div>
      </aside>
    </main>
  </div>
`;

startGame({
  mountId: "game",
  statusEl: document.querySelector<HTMLPreElement>("#status")!,
  eventEl: document.querySelector<HTMLPreElement>("#event")!,
  btnNew: document.querySelector<HTMLButtonElement>("#btnNew")!,
  btnStep: document.querySelector<HTMLButtonElement>("#btnStep")!,
  btnRun: document.querySelector<HTMLButtonElement>("#btnRun")!,
  modeEl: document.querySelector<HTMLSelectElement>("#mode")!,
  followEl: document.querySelector<HTMLInputElement>("#follow")!,
  loraEl: document.querySelector<HTMLInputElement>("#lora")!,
});
