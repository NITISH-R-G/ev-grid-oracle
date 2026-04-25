from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.policies import baseline_policy


def _station_color(load: float) -> tuple[int, int, int]:
    if load < 0.40:
        return (46, 213, 115)
    if load < 0.60:
        return (255, 200, 0)
    if load < 0.80:
        return (255, 130, 0)
    if load < 0.95:
        return (255, 50, 50)
    return (180, 0, 0)


def _norm(v: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    x = (v - lo) / (hi - lo)
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


@dataclass
class RenderConfig:
    width: int = 1280
    height: int = 720
    fps: int = 30

    margin: int = 48
    hud_w: int = 320

    bg: tuple[int, int, int] = (10, 12, 20)
    panel: tuple[int, int, int] = (18, 20, 32)
    panel_border: tuple[int, int, int] = (80, 90, 120)


class CityMapRenderer:
    def __init__(self, env: EVGridCore, cfg: RenderConfig = RenderConfig()):
        self.env = env
        self.cfg = cfg
        self._font = pygame.font.SysFont("Consolas", 18)
        self._font_sm = pygame.font.SysFont("Consolas", 14)

        state = self.env._grid_state
        if state is None:
            raise RuntimeError("env must be reset() before rendering")

        lats = [s.lat for s in state.stations]
        lngs = [s.lng for s in state.stations]
        self.lat_lo, self.lat_hi = min(lats), max(lats)
        self.lng_lo, self.lng_hi = min(lngs), max(lngs)
        self._graph = env.city_graph
        self._node_xy = {s.station_id: self.xy(s.lat, s.lng) for s in state.stations}
        self._t = 0.0

    def xy(self, lat: float, lng: float) -> tuple[int, int]:
        w = self.cfg.width - self.cfg.hud_w - self.cfg.margin * 2
        h = self.cfg.height - self.cfg.margin * 2
        x = int(self.cfg.margin + _norm(lng, self.lng_lo, self.lng_hi) * w)
        y = int(self.cfg.margin + (1.0 - _norm(lat, self.lat_lo, self.lat_hi)) * h)
        return x, y

    def draw_arrow(self, surf: pygame.Surface, a: tuple[int, int], b: tuple[int, int], color=(0, 200, 255)):
        ax, ay = a
        bx, by = b
        pygame.draw.line(surf, color, a, b, 3)
        ang = math.atan2(by - ay, bx - ax)
        head = 14
        left = (bx - head * math.cos(ang - 0.4), by - head * math.sin(ang - 0.4))
        right = (bx - head * math.cos(ang + 0.4), by - head * math.sin(ang + 0.4))
        pygame.draw.polygon(surf, color, [(bx, by), left, right])

    def render(self, surf: pygame.Surface, *, last_action: Optional[EVGridAction] = None, mode_label: str = ""):
        cfg = self.cfg
        self._t += 1.0 / max(1, cfg.fps)
        self._draw_background(surf)

        state = self.env._grid_state
        if state is None:
            return

        self._draw_edges(surf)

        # stations
        for st in state.stations:
            x, y = self.xy(st.lat, st.lng)
            load = st.occupied_slots / max(1, st.total_slots)
            col = _station_color(load)
            radius = 10 + int(_norm(st.total_slots, 4, 16) * 14)
            self._draw_glow(surf, (x, y), radius, col, intensity=load)
            pygame.draw.circle(surf, col, (x, y), radius)
            pygame.draw.circle(surf, (0, 0, 0), (x, y), radius, 2)

            # queue dots
            for i in range(min(5, st.queue_length)):
                pygame.draw.circle(surf, (245, 245, 245), (x - 10 + i * 6, y - radius - 10), 3)

            label = self._font_sm.render(st.station_id, True, (220, 220, 220))
            surf.blit(label, (x + radius + 6, y - 8))

        # draw arrow: from EV neighborhood's station -> chosen station
        if last_action and last_action.action_type == ActionType.route and last_action.station_id and state.pending_evs:
            ev = state.pending_evs[0]
            try:
                from_station = next(s for s in state.stations if s.neighborhood_slug == ev.neighborhood_slug)
                to_station = next(s for s in state.stations if s.station_id == last_action.station_id)
                self._draw_animated_route(
                    surf,
                    self.xy(from_station.lat, from_station.lng),
                    self.xy(to_station.lat, to_station.lng),
                )
            except StopIteration:
                pass

        # HUD panel
        hud_x = cfg.width - cfg.hud_w + 16
        pygame.draw.rect(
            surf,
            cfg.panel,
            pygame.Rect(cfg.width - cfg.hud_w, 0, cfg.hud_w, cfg.height),
        )
        pygame.draw.rect(
            surf,
            cfg.panel_border,
            pygame.Rect(cfg.width - cfg.hud_w, 0, cfg.hud_w, cfg.height),
            2,
        )

        def blit_line(y: int, txt: str, *, big=False):
            f = self._font if big else self._font_sm
            surf.blit(f.render(txt, True, (240, 240, 240)), (hud_x, y))

        blit_line(20, "EV GRID ORACLE", big=True)
        if mode_label:
            blit_line(48, f"Mode: {mode_label}")
        blit_line(74, f"Time: {state.hour:02d}:00  {state.day_type.value}")
        blit_line(98, f"Grid load: {state.grid_load_pct*100:5.1f}%")
        blit_line(122, f"Renewable: {state.renewable_pct*100:5.1f}%")
        blit_line(146, f"Peak risk: {state.peak_risk.value}")
        avg_wait = sum(s.avg_wait_minutes for s in state.stations) / max(1, len(state.stations))
        blit_line(170, f"Avg wait: {avg_wait:5.1f} min")
        blit_line(196, f"Pending EVs: {len(state.pending_evs)}")

        if state.pending_evs:
            ev = state.pending_evs[0]
            crit = "CRITICAL" if ev.battery_pct_0_100 < 15 else ""
            blit_line(240, "Next EV:", big=True)
            blit_line(266, f"{ev.ev_id}  {ev.battery_pct_0_100:4.1f}% {crit}")
            blit_line(290, f"From: {ev.neighborhood_name}")
            blit_line(314, f"Urgency: {ev.urgency:.2f}")

    def _draw_background(self, surf: pygame.Surface) -> None:
        # simple vertical gradient + vignette
        w, h = surf.get_size()
        top = (10, 12, 20)
        bot = (6, 8, 14)
        for y in range(0, h, 4):
            t = y / max(1, h - 1)
            col = (
                int(top[0] * (1 - t) + bot[0] * t),
                int(top[1] * (1 - t) + bot[1] * t),
                int(top[2] * (1 - t) + bot[2] * t),
            )
            pygame.draw.rect(surf, col, pygame.Rect(0, y, w, 4))

    def _draw_edges(self, surf: pygame.Surface) -> None:
        # subtle graph edges for "city network" feel
        col = (35, 45, 70)
        for a, b in self._graph.edges:
            if a in self._node_xy and b in self._node_xy:
                pygame.draw.line(surf, col, self._node_xy[a], self._node_xy[b], 1)

    def _draw_glow(
        self,
        surf: pygame.Surface,
        pos: tuple[int, int],
        radius: int,
        col: tuple[int, int, int],
        *,
        intensity: float,
    ) -> None:
        # fake glow: draw expanded translucent circles
        x, y = pos
        pulse = 0.5 + 0.5 * math.sin(self._t * 2.5 + intensity * 3.0)
        for k in (10, 18, 26):
            r = radius + k
            alpha = int(40 * pulse * (1.0 - k / 30.0))
            if alpha <= 0:
                continue
            s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, alpha), (r + 1, r + 1), r)
            surf.blit(s, (x - r - 1, y - r - 1))

    def _draw_animated_route(self, surf: pygame.Surface, a: tuple[int, int], b: tuple[int, int]) -> None:
        # arrow + moving dot along path
        self.draw_arrow(surf, a, b, color=(0, 200, 255))
        ax, ay = a
        bx, by = b
        t = (math.sin(self._t * 4.0) * 0.5 + 0.5)
        x = int(ax + (bx - ax) * t)
        y = int(ay + (by - ay) * t)
        pygame.draw.circle(surf, (0, 220, 255), (x, y), 6)


def run_live(seed: int = 123, *, mode: str = "baseline"):
    pygame.init()
    cfg = RenderConfig()
    screen = pygame.display.set_mode((cfg.width, cfg.height))
    pygame.display.set_caption("EV Grid Oracle — City Map")
    clock = pygame.time.Clock()

    env = EVGridCore(city_graph=build_city_graph())
    env.reset(seed=seed)
    renderer = CityMapRenderer(env, cfg)

    last_action: Optional[EVGridAction] = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # one sim tick
                    st = env._grid_state
                    if st is None or not st.pending_evs:
                        action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
                    else:
                        action = baseline_policy(st, env.city_graph)
                    last_action = action
                    env.step(action)

        renderer.render(screen, last_action=last_action, mode_label=mode)
        pygame.display.flip()
        clock.tick(cfg.fps)

    pygame.quit()


if __name__ == "__main__":
    run_live()

