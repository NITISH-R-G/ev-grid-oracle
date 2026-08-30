sed -i 's/def ma_new(req: Request, payload: MANewRequest = Body(...)) -> dict\[str, Any\]:/def ma_new(req: Request, payload: MANewRequest) -> dict[str, Any]:/g' server/app.py
sed -i 's/req: Request, payload: MAAutoStepRequest = Body(...)/req: Request, payload: MAAutoStepRequest/g' server/app.py
sed -i 's/def ma_step(req: Request, payload: MultiAgentStepRequest = Body(...)) -> dict\[str, Any\]:/def ma_step(req: Request, payload: MultiAgentStepRequest) -> dict[str, Any]:/g' server/app.py
sed -i 's/def demo_new(req: Request, payload: DemoNewRequest = Body(...)) -> dict\[str, Any\]:/def demo_new(req: Request, payload: DemoNewRequest) -> dict[str, Any]:/g' server/app.py
sed -i 's/req: Request, payload: DemoSpawnVehicleRequest = Body(...)/req: Request, payload: DemoSpawnVehicleRequest/g' server/app.py
sed -i 's/mode: Literal\["baseline", "oracle"\] = Body("baseline"),/mode: Literal["baseline", "oracle"] = "baseline",/g' server/app.py
sed -i 's/oracle_lora_repo: str = Body("", embed=True),/oracle_lora_repo: str = "",/g' server/app.py
sed -i 's/forced_action: dict\[str, Any\] | None = Body(None),/forced_action: dict[str, Any] | None = None,/g' server/app.py
sed -i 's/timed_out/_timed_out/g' server/app.py
sed -i 's/skipped/_skipped/g' server/app.py
sed -i 's/ts, core = row/_ts, core = row/g' server/app.py
sed -i 's/raise ValueError("invalid road graph json")/raise TypeError("invalid road graph json")/g' server/road_router.py

# Models fix
sed -i 's/if self.defer_minutes <= 0:/if self.defer_minutes <= 0 and self.action_type == ActionType.defer:/g' ev_grid_oracle/models.py
sed -i 's/if self.action_type == ActionType.defer://g' ev_grid_oracle/models.py
sed -i 's/if self.defer_minutes != 0:/if self.defer_minutes != 0 and self.action_type == ActionType.load_shift:/g' ev_grid_oracle/models.py
sed -i 's/if self.action_type == ActionType.load_shift://g' ev_grid_oracle/models.py

# MultiAgent Fix
sed -i 's/if resolved.action_type.value == "route":/if resolved.action_type.value == "route" and float(st.grid_load_pct) >= float(grid_directive.max_grid_load_pct):/g' ev_grid_oracle/multi_agent.py
sed -i 's/if float(st.grid_load_pct) >= float(grid_directive.max_grid_load_pct)://g' ev_grid_oracle/multi_agent.py
