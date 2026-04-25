import Phaser from "phaser";
import { PixelCityScene } from "./PixelCityScene";

type StartArgs = {
  mountId: string;
  statusEl: HTMLPreElement;
  eventEl: HTMLPreElement;
  btnNew: HTMLButtonElement;
  btnStep: HTMLButtonElement;
  btnRun: HTMLButtonElement;
  modeEl: HTMLSelectElement;
  followEl: HTMLInputElement;
  loraEl: HTMLInputElement;
};

export function startGame(args: StartArgs) {
  const mount = document.getElementById(args.mountId);
  if (!mount) throw new Error(`Mount element not found: ${args.mountId}`);

  const ui = {
    statusEl: args.statusEl,
    eventEl: args.eventEl,
    modeEl: args.modeEl,
    followEl: args.followEl,
    loraEl: args.loraEl,
  };

  const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    parent: mount,
    width: 1280,
    height: 720,
    backgroundColor: "#070911",
    pixelArt: true,
    antialias: false,
    physics: { default: "arcade" },
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    scene: [PixelCityScene],
  };

  const game = new Phaser.Game(config);
  game.scene.start("PixelCityScene", { ui });
  const scene = () => game.scene.getScene("PixelCityScene") as PixelCityScene;

  const seedRand = () => Math.floor(Math.random() * 10_000);

  args.btnNew.onclick = async () => {
    try {
      await scene().newSession(seedRand());
    } catch (e: any) {
      ui.statusEl.textContent = String(e?.message || e);
    }
  };

  args.btnStep.onclick = async () => {
    try {
      await scene().stepOnce();
    } catch (e: any) {
      ui.statusEl.textContent = String(e?.message || e);
    }
  };

  args.btnRun.onclick = async () => {
    try {
      for (let i = 0; i < 60; i++) {
        // eslint-disable-next-line no-await-in-loop
        await scene().stepOnce();
        // brief pacing so camera movement is visible
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, 90));
      }
    } catch (e: any) {
      ui.statusEl.textContent = String(e?.message || e);
    }
  };
}

