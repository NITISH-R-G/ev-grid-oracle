# Architecture Graph

```mermaid
graph TD
  __ev_grid_oracle_models_py["./ev_grid_oracle/models.py"]
  __tools_fetch_osm_roads_py["./tools/fetch_osm_roads.py"]
  ev_grid_oracle_road_env["ev_grid_oracle.road_env"]
  enum["enum"]
  __server___init___py["./server/__init__.py"]
  personas["personas"]
  subprocess["subprocess"]
  __ev_grid_oracle_reward_hack_py["./ev_grid_oracle/reward_hack.py"]
  fastapi_staticfiles["fastapi.staticfiles"]
  __viz_gradio_demo_py["./viz/gradio_demo.py"]
  __tools_generate_architecture_diagrams_py["./tools/generate_architecture_diagrams.py"]
  matplotlib_pyplot["matplotlib.pyplot"]
  fastapi_responses["fastapi.responses"]
  fastapi_testclient["fastapi.testclient"]
  openenv_core_env_server_interfaces["openenv.core.env_server.interfaces"]
  demand_sim["demand_sim"]
  fastapi["fastapi"]
  __ev_grid_oracle_road_models_py["./ev_grid_oracle/road_models.py"]
  __tools_generate_health_dashboard_py["./tools/generate_health_dashboard.py"]
  __ev_grid_oracle_policies_py["./ev_grid_oracle/policies.py"]
  __ev_grid_oracle_multi_agent_py["./ev_grid_oracle/multi_agent.py"]
  server_role_metrics["server.role_metrics"]
  __tests_test_fair_eval_mcnemar_py["./tests/test_fair_eval_mcnemar.py"]
  __tests_test_reward_py["./tests/test_reward.py"]
  __tests_test_parsing_py["./tests/test_parsing.py"]
  __test_script_py["./test_script.py"]
  __future__["__future__"]
  gradio["gradio"]
  __tools_fetch_bangalore_roads_overpass_py["./tools/fetch_bangalore_roads_overpass.py"]
  datetime["datetime"]
  openenv_core_env_server_types["openenv.core.env_server.types"]
  torch["torch"]
  PIL["PIL"]
  __ev_grid_oracle_oracle_agent_py["./ev_grid_oracle/oracle_agent.py"]
  reward["reward"]
  grid_sim["grid_sim"]
  __server_role_metrics_py["./server/role_metrics.py"]
  huggingface_hub["huggingface_hub"]
  ev_grid_oracle_road_models["ev_grid_oracle.road_models"]
  __ev_grid_oracle_grid_sim_py["./ev_grid_oracle/grid_sim.py"]
  ev_grid_oracle_policies["ev_grid_oracle.policies"]
  __training___init___py["./training/__init__.py"]
  __server_ev_grid_environment_py["./server/ev_grid_environment.py"]
  __ev_grid_oracle_scenarios_py["./ev_grid_oracle/scenarios.py"]
  __ev_grid_oracle___init___py["./ev_grid_oracle/__init__.py"]
  peft["peft"]
  __tools_generate_knowledge_graph_py["./tools/generate_knowledge_graph.py"]
  __ev_grid_oracle_traffic_py["./ev_grid_oracle/traffic.py"]
  __viz_record_py["./viz/record.py"]
  gzip["gzip"]
  typing["typing"]
  __training_make_plots_py["./training/make_plots.py"]
  collections["collections"]
  os["os"]
  copy["copy"]
  __viz_record_two_phase_py["./viz/record_two_phase.py"]
  dataclasses["dataclasses"]
  ev_grid_oracle_city_graph["ev_grid_oracle.city_graph"]
  __viz_city_map_py["./viz/city_map.py"]
  __ev_grid_oracle_parsing_py["./ev_grid_oracle/parsing.py"]
  threading["threading"]
  pytest["pytest"]
  __ev_grid_oracle_personas_py["./ev_grid_oracle/personas.py"]
  __tools_build_roads_render_py["./tools/build_roads_render.py"]
  urllib_parse["urllib.parse"]
  server_ev_grid_environment["server.ev_grid_environment"]
  viz_city_map["viz.city_map"]
  __tools_build_road_graph_py["./tools/build_road_graph.py"]
  pygame["pygame"]
  __viz___init___py["./viz/__init__.py"]
  policies["policies"]
  pathlib["pathlib"]
  json["json"]
  __tests_test_world_model_verifier_py["./tests/test_world_model_verifier.py"]
  argparse["argparse"]
  __tests_test_models_and_graph_py["./tests/test_models_and_graph.py"]
  concurrent_futures["concurrent.futures"]
  openenv_core_env_server_http_server["openenv.core.env_server.http_server"]
  __ev_grid_oracle_world_model_verifier_py["./ev_grid_oracle/world_model_verifier.py"]
  urllib_request["urllib.request"]
  __tools_write_eval_snapshot_py["./tools/write_eval_snapshot.py"]
  bescom_feed["bescom_feed"]
  __tests_test_policies_collapse_py["./tests/test_policies_collapse.py"]
  __tools_prune_osm_geojson_py["./tools/prune_osm_geojson.py"]
  env["env"]
  __ev_grid_oracle_city_graph_py["./ev_grid_oracle/city_graph.py"]
  __tools_export_grpo_tensorboard_plots_py["./tools/export_grpo_tensorboard_plots.py"]
  time["time"]
  ev_grid_oracle_traffic["ev_grid_oracle.traffic"]
  openai["openai"]
  tensorboard_backend_event_processing_event_accumulator["tensorboard.backend.event_processing.event_accumulator"]
  ev_grid_oracle_scenarios["ev_grid_oracle.scenarios"]
  ev_grid_oracle_models["ev_grid_oracle.models"]
  pydantic["pydantic"]
  ev_grid_oracle_multi_agent["ev_grid_oracle.multi_agent"]
  uvicorn["uvicorn"]
  __ev_grid_oracle_env_py["./ev_grid_oracle/env.py"]
  __ev_grid_oracle_demand_sim_py["./ev_grid_oracle/demand_sim.py"]
  __tests_test_demo_api_py["./tests/test_demo_api.py"]
  __tools___init___py["./tools/__init__.py"]
  __tools_road_reward_smoke_py["./tools/road_reward_smoke.py"]
  __tests_test_env_determinism_py["./tests/test_env_determinism.py"]
  re["re"]
  training_evaluate["training.evaluate"]
  __server_ev_grid_road_environment_py["./server/ev_grid_road_environment.py"]
  reward_hack["reward_hack"]
  sys["sys"]
  math["math"]
  __ev_grid_oracle_reward_py["./ev_grid_oracle/reward.py"]
  __ev_grid_oracle_road_env_py["./ev_grid_oracle/road_env.py"]
  ast["ast"]
  server_app["server.app"]
  __tests_test_evaluate_paired_py["./tests/test_evaluate_paired.py"]
  __server_road_router_py["./server/road_router.py"]
  server_road_router["server.road_router"]
  training_fair_eval["training.fair_eval"]
  uuid["uuid"]
  __training_evaluate_py["./training/evaluate.py"]
  logging["logging"]
  ev_grid_oracle_parsing["ev_grid_oracle.parsing"]
  __ev_grid_oracle_bescom_feed_py["./ev_grid_oracle/bescom_feed.py"]
  __server_app_py["./server/app.py"]
  __tools_docs_sync_py["./tools/docs_sync.py"]
  road_models["road_models"]
  __tests___init___py["./tests/__init__.py"]
  hashlib["hashlib"]
  __training_fair_eval_py["./training/fair_eval.py"]
  statistics["statistics"]
  networkx["networkx"]
  ev_grid_oracle_reward["ev_grid_oracle.reward"]
  city_graph["city_graph"]
  jinja2["jinja2"]
  ev_grid_oracle_oracle_agent["ev_grid_oracle.oracle_agent"]
  random["random"]
  ev_grid_oracle_env["ev_grid_oracle.env"]
  server_ev_grid_road_environment["server.ev_grid_road_environment"]
  transformers["transformers"]
  scenarios["scenarios"]
  models["models"]
  __tools_sync_space_to_hub_py["./tools/sync_space_to_hub.py"]
  ev_grid_oracle_world_model_verifier["ev_grid_oracle.world_model_verifier"]
  __tests_test_reward_py --> ev_grid_oracle_city_graph
  __tests_test_reward_py --> typing
  __server_app_py --> ev_grid_oracle_scenarios
  __tools_build_road_graph_py --> dataclasses
  __tools_generate_knowledge_graph_py --> typing
  __ev_grid_oracle_models_py --> openenv_core_env_server_types
  __ev_grid_oracle_scenarios_py --> dataclasses
  __ev_grid_oracle_env_py --> typing
  __tests_test_evaluate_paired_py --> ev_grid_oracle_env
  __tools_export_grpo_tensorboard_plots_py --> pathlib
  __tools_prune_osm_geojson_py --> sys
  __tools_fetch_bangalore_roads_overpass_py --> time
  __viz_record_two_phase_py --> typing
  __tools_prune_osm_geojson_py --> pathlib
  __tests_test_world_model_verifier_py --> ev_grid_oracle_policies
  __viz_record_two_phase_py --> viz_city_map
  __tests_test_fair_eval_mcnemar_py --> __future__
  __training_fair_eval_py --> matplotlib_pyplot
  __ev_grid_oracle_world_model_verifier_py --> models
  __tests_test_evaluate_paired_py --> sys
  __tools_fetch_bangalore_roads_overpass_py --> argparse
  __tools_sync_space_to_hub_py --> pathlib
  __tests_test_env_determinism_py --> pydantic
  __viz_record_two_phase_py --> ev_grid_oracle_models
  __server_ev_grid_road_environment_py --> ev_grid_oracle_road_env
  __tools_export_grpo_tensorboard_plots_py --> __future__
  __ev_grid_oracle_bescom_feed_py --> hashlib
  __ev_grid_oracle_road_env_py --> dataclasses
  __tools_road_reward_smoke_py --> __future__
  __viz_record_two_phase_py --> ev_grid_oracle_city_graph
  __server_ev_grid_road_environment_py --> openenv_core_env_server_interfaces
  __server_app_py --> ev_grid_oracle_traffic
  __tools_write_eval_snapshot_py --> pathlib
  __ev_grid_oracle_city_graph_py --> dataclasses
  __tools_generate_health_dashboard_py --> os
  __tests_test_env_determinism_py --> pytest
  __viz_city_map_py --> pygame
  __server_road_router_py --> json
  __ev_grid_oracle_multi_agent_py --> models
  __ev_grid_oracle_models_py --> enum
  __tests_test_demo_api_py --> fastapi_testclient
  __ev_grid_oracle_oracle_agent_py --> peft
  __ev_grid_oracle_env_py --> dataclasses
  __viz_record_py --> ev_grid_oracle_models
  __ev_grid_oracle_road_env_py --> road_models
  __tools_build_roads_render_py --> argparse
  __server_app_py --> fastapi_staticfiles
  __server_app_py --> ev_grid_oracle_policies
  __training_evaluate_py --> argparse
  __training_evaluate_py --> ev_grid_oracle_scenarios
  __ev_grid_oracle_world_model_verifier_py --> statistics
  __training_evaluate_py --> ev_grid_oracle_oracle_agent
  __tests_test_world_model_verifier_py --> ev_grid_oracle_env
  __tools_fetch_osm_roads_py --> urllib_request
  __training_fair_eval_py --> pathlib
  __server_ev_grid_road_environment_py --> __future__
  __ev_grid_oracle_reward_py --> math
  __server_app_py --> uvicorn
  __ev_grid_oracle_env_py --> __future__
  __tools_sync_space_to_hub_py --> sys
  __training_fair_eval_py --> argparse
  __tests_test_evaluate_paired_py --> subprocess
  __tools_generate_knowledge_graph_py --> ast
  __server_app_py --> __future__
  __ev_grid_oracle_oracle_agent_py --> typing
  __tools_docs_sync_py --> logging
  __training_make_plots_py --> pathlib
  __tests_test_evaluate_paired_py --> training_evaluate
  __ev_grid_oracle_reward_hack_py --> models
  __ev_grid_oracle_env_py --> reward
  __server_app_py --> ev_grid_oracle_reward
  __tools_generate_architecture_diagrams_py --> ast
  __viz_city_map_py --> typing
  __ev_grid_oracle_traffic_py --> dataclasses
  __tests_test_evaluate_paired_py --> __future__
  __viz_record_py --> __future__
  __tools_write_eval_snapshot_py --> __future__
  __tools_generate_architecture_diagrams_py --> os
  __ev_grid_oracle_scenarios_py --> __future__
  __tools_fetch_bangalore_roads_overpass_py --> __future__
  __tests_test_policies_collapse_py --> ev_grid_oracle_city_graph
  __viz_record_two_phase_py --> __future__
  __server_app_py --> logging
  __server_road_router_py --> typing
  __viz_record_py --> typing
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_parsing
  __server_road_router_py --> networkx
  __training_evaluate_py --> ev_grid_oracle_models
  __tools_sync_space_to_hub_py --> huggingface_hub
  __ev_grid_oracle_road_env_py --> __future__
  __tools_generate_health_dashboard_py --> json
  __ev_grid_oracle_env_py --> bescom_feed
  __ev_grid_oracle_multi_agent_py --> dataclasses
  __server_road_router_py --> pathlib
  __viz_record_two_phase_py --> pathlib
  __viz_city_map_py --> ev_grid_oracle_models
  __tests_test_env_determinism_py --> ev_grid_oracle_policies
  __server_app_py --> os
  __ev_grid_oracle_personas_py --> dataclasses
  __test_script_py --> pydantic
  __viz_record_py --> ev_grid_oracle_policies
  __tools_build_road_graph_py --> json
  __tests_test_policies_collapse_py --> __future__
  __ev_grid_oracle_demand_sim_py --> math
  __tools_fetch_bangalore_roads_overpass_py --> pathlib
  __tools_write_eval_snapshot_py --> subprocess
  __ev_grid_oracle_oracle_agent_py --> transformers
  __server_ev_grid_environment_py --> openenv_core_env_server_types
  __tests_test_policies_collapse_py --> ev_grid_oracle_policies
  __server_app_py --> ev_grid_oracle_models
  __tools_generate_knowledge_graph_py --> logging
  __tests_test_reward_py --> ev_grid_oracle_env
  __ev_grid_oracle_traffic_py --> __future__
  __ev_grid_oracle_multi_agent_py --> typing
  __training_evaluate_py --> typing
  __tools_docs_sync_py --> re
  __tests_test_models_and_graph_py --> ev_grid_oracle_models
  __server_road_router_py --> math
  __ev_grid_oracle_bescom_feed_py --> models
  __ev_grid_oracle_city_graph_py --> math
  __ev_grid_oracle_demand_sim_py --> dataclasses
  __ev_grid_oracle_traffic_py --> math
  __ev_grid_oracle_world_model_verifier_py --> grid_sim
  __ev_grid_oracle_parsing_py --> models
  __tools_fetch_bangalore_roads_overpass_py --> json
  __viz_record_two_phase_py --> ev_grid_oracle_policies
  __server_app_py --> pydantic
  __viz_city_map_py --> dataclasses
  __tools_sync_space_to_hub_py --> subprocess
  __tools_build_roads_render_py --> typing
  __training_make_plots_py --> typing
  __server_app_py --> ev_grid_oracle_multi_agent
  __tools_fetch_osm_roads_py --> dataclasses
  __server_ev_grid_environment_py --> uuid
  __viz_city_map_py --> __future__
  __ev_grid_oracle_env_py --> reward_hack
  __ev_grid_oracle_models_py --> typing
  __viz_gradio_demo_py --> ev_grid_oracle_env
  __viz_record_two_phase_py --> ev_grid_oracle_env
  __ev_grid_oracle_reward_py --> networkx
  __tools_export_grpo_tensorboard_plots_py --> matplotlib_pyplot
  __server_road_router_py --> __future__
  __tools_prune_osm_geojson_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_world_model_verifier_py --> copy
  __training_make_plots_py --> json
  __ev_grid_oracle_parsing_py --> __future__
  __viz_record_py --> pygame
  __server_role_metrics_py --> __future__
  __ev_grid_oracle_env_py --> scenarios
  __tools_generate_health_dashboard_py --> openai
  __tools_fetch_osm_roads_py --> __future__
  __ev_grid_oracle_reward_py --> statistics
  __viz_gradio_demo_py --> ev_grid_oracle_policies
  __tools_sync_space_to_hub_py --> os
  __training_evaluate_py --> dataclasses
  __training_evaluate_py --> ev_grid_oracle_city_graph
  __server_road_router_py --> dataclasses
  __tools_fetch_bangalore_roads_overpass_py --> urllib_parse
  __ev_grid_oracle_road_env_py --> random
  __tools_generate_health_dashboard_py --> datetime
  __tools_road_reward_smoke_py --> ev_grid_oracle_road_env
  __ev_grid_oracle_road_models_py --> __future__
  __viz_record_two_phase_py --> argparse
  __ev_grid_oracle_world_model_verifier_py --> env
  __server_app_py --> openenv_core_env_server_http_server
  __viz_city_map_py --> ev_grid_oracle_policies
  __ev_grid_oracle_env_py --> grid_sim
  __tests_test_evaluate_paired_py --> json
  __tests_test_evaluate_paired_py --> pathlib
  __viz_record_py --> pathlib
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_policies
  __ev_grid_oracle_road_models_py --> openenv_core_env_server_types
  __ev_grid_oracle_policies_py --> ev_grid_oracle_models
  __server_app_py --> pathlib
  __server_app_py --> time
  __tests_test_models_and_graph_py --> ev_grid_oracle_city_graph
  __server_app_py --> ev_grid_oracle_oracle_agent
  __tools_generate_architecture_diagrams_py --> logging
  __training_evaluate_py --> ev_grid_oracle_env
  __server_ev_grid_environment_py --> ev_grid_oracle_models
  __tools_build_roads_render_py --> json
  __tools_fetch_osm_roads_py --> pathlib
  __server_ev_grid_environment_py --> __future__
  __ev_grid_oracle_personas_py --> random
  __tools_fetch_osm_roads_py --> urllib_parse
  __ev_grid_oracle_multi_agent_py --> __future__
  __viz_gradio_demo_py --> __future__
  __training_fair_eval_py --> typing
  __tools_docs_sync_py --> ast
  __ev_grid_oracle_oracle_agent_py --> threading
  __server_app_py --> server_road_router
  __tools_fetch_osm_roads_py --> argparse
  __viz_record_two_phase_py --> ev_grid_oracle_oracle_agent
  __tools_build_roads_render_py --> __future__
  __viz_record_py --> ev_grid_oracle_env
  __server_app_py --> concurrent_futures
  __server_app_py --> networkx
  __server_ev_grid_road_environment_py --> uuid
  __training_make_plots_py --> matplotlib_pyplot
  __ev_grid_oracle_world_model_verifier_py --> dataclasses
  __ev_grid_oracle_oracle_agent_py --> __future__
  __tests_test_models_and_graph_py --> ev_grid_oracle_env
  __viz_gradio_demo_py --> typing
  __tools_sync_space_to_hub_py --> __future__
  __ev_grid_oracle_road_models_py --> pydantic
  __ev_grid_oracle_env_py --> city_graph
  __ev_grid_oracle_city_graph_py --> typing
  __ev_grid_oracle_reward_py --> dataclasses
  __tools_build_road_graph_py --> math
  __tools_road_reward_smoke_py --> ev_grid_oracle_road_models
  __viz_gradio_demo_py --> training_evaluate
  __ev_grid_oracle_reward_hack_py --> __future__
  __training_evaluate_py --> json
  __tests_test_policies_collapse_py --> ev_grid_oracle_models
  __server_ev_grid_environment_py --> ev_grid_oracle_env
  __server_app_py --> server_ev_grid_environment
  __ev_grid_oracle_policies_py --> __future__
  __training_evaluate_py --> collections
  __tests_test_world_model_verifier_py --> ev_grid_oracle_world_model_verifier
  __ev_grid_oracle_road_env_py --> networkx
  __server_app_py --> server_role_metrics
  __ev_grid_oracle_city_graph_py --> networkx
  __training_evaluate_py --> statistics
  __ev_grid_oracle_road_env_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_reward_hack_py --> dataclasses
  __viz_city_map_py --> ev_grid_oracle_env
  __tools_build_road_graph_py --> typing
  __server_app_py --> ev_grid_oracle_parsing
  __server_ev_grid_road_environment_py --> openenv_core_env_server_types
  __viz_city_map_py --> math
  __ev_grid_oracle_grid_sim_py --> math
  __tools_export_grpo_tensorboard_plots_py --> argparse
  __ev_grid_oracle_personas_py --> __future__
  __training_fair_eval_py --> math
  __viz_gradio_demo_py --> ev_grid_oracle_models
  __server_app_py --> ev_grid_oracle_road_models
  __server_road_router_py --> gzip
  __ev_grid_oracle_env_py --> models
  __training_fair_eval_py --> json
  __ev_grid_oracle_bescom_feed_py --> __future__
  __ev_grid_oracle_policies_py --> ev_grid_oracle_city_graph
  __tests_test_world_model_verifier_py --> ev_grid_oracle_city_graph
  __tools_write_eval_snapshot_py --> sys
  __tests_test_env_determinism_py --> ev_grid_oracle_city_graph
  __server_app_py --> fastapi
  __ev_grid_oracle_oracle_agent_py --> torch
  __tools_generate_health_dashboard_py --> jinja2
  __training_fair_eval_py --> __future__
  __ev_grid_oracle_demand_sim_py --> random
  __ev_grid_oracle_grid_sim_py --> __future__
  __ev_grid_oracle_models_py --> __future__
  __ev_grid_oracle_parsing_py --> re
  __ev_grid_oracle_oracle_agent_py --> dataclasses
  __training_evaluate_py --> ev_grid_oracle_policies
  __viz_gradio_demo_py --> ev_grid_oracle_city_graph
  __server_app_py --> server_ev_grid_road_environment
  __server_road_router_py --> ev_grid_oracle_traffic
  __tools_road_reward_smoke_py --> re
  __server_ev_grid_road_environment_py --> ev_grid_oracle_road_models
  __server_ev_grid_environment_py --> openenv_core_env_server_interfaces
  __ev_grid_oracle_env_py --> demand_sim
  __viz_gradio_demo_py --> dataclasses
  __tools_prune_osm_geojson_py --> json
  __tools_build_road_graph_py --> pathlib
  __tools_fetch_osm_roads_py --> time
  __viz_city_map_py --> ev_grid_oracle_city_graph
  __tests_test_evaluate_paired_py --> ev_grid_oracle_city_graph
  __tools_build_road_graph_py --> hashlib
  __viz_gradio_demo_py --> PIL
  __viz_record_py --> viz_city_map
  __tools_fetch_bangalore_roads_overpass_py --> urllib_request
  __tests_test_fair_eval_mcnemar_py --> training_fair_eval
  __tools_generate_health_dashboard_py --> subprocess
  __training_make_plots_py --> math
  __tests_test_reward_py --> ev_grid_oracle_models
  __tests_test_env_determinism_py --> __future__
  __ev_grid_oracle_multi_agent_py --> policies
  __ev_grid_oracle_bescom_feed_py --> dataclasses
  __tools_generate_architecture_diagrams_py --> re
  __server_ev_grid_environment_py --> ev_grid_oracle_city_graph
  __tests_test_env_determinism_py --> ev_grid_oracle_env
  __tests_test_models_and_graph_py --> pytest
  __tools_prune_osm_geojson_py --> __future__
  __ev_grid_oracle_demand_sim_py --> __future__
  __tests_test_policies_collapse_py --> ev_grid_oracle_env
  __ev_grid_oracle_env_py --> networkx
  __server_app_py --> collections
  __server_app_py --> ev_grid_oracle_world_model_verifier
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_models
  __ev_grid_oracle_parsing_py --> typing
  __ev_grid_oracle_multi_agent_py --> env
  __training_make_plots_py --> argparse
  __ev_grid_oracle_world_model_verifier_py --> __future__
  __viz_record_py --> argparse
  __tests_test_demo_api_py --> server_app
  __ev_grid_oracle_reward_py --> __future__
  __viz_gradio_demo_py --> ev_grid_oracle_oracle_agent
  __tools_build_road_graph_py --> networkx
  __tools_generate_knowledge_graph_py --> os
  __training_evaluate_py --> __future__
  __training_evaluate_py --> os
  __tests_test_env_determinism_py --> ev_grid_oracle_models
  __tools_fetch_osm_roads_py --> json
  __tools_docs_sync_py --> os
  __viz_record_two_phase_py --> pygame
  __server_role_metrics_py --> typing
  __server_app_py --> ev_grid_oracle_city_graph
  __tools_fetch_bangalore_roads_overpass_py --> typing
  __tests_test_world_model_verifier_py --> ev_grid_oracle_models
  __tools_generate_health_dashboard_py --> urllib_request
  __viz_gradio_demo_py --> gradio
  __tests_test_evaluate_paired_py --> pytest
  __training_make_plots_py --> __future__
  __tools_build_road_graph_py --> argparse
  __ev_grid_oracle_env_py --> random
  __tools_build_road_graph_py --> gzip
  __tools_generate_knowledge_graph_py --> json
  __tools_sync_space_to_hub_py --> argparse
  __tests_test_parsing_py --> ev_grid_oracle_parsing
  __ev_grid_oracle_traffic_py --> hashlib
  __server_app_py --> hashlib
  __server_app_py --> fastapi_responses
  __ev_grid_oracle_city_graph_py --> models
  __server_app_py --> typing
  __tests_test_evaluate_paired_py --> os
  __tools_prune_osm_geojson_py --> argparse
  __tools_export_grpo_tensorboard_plots_py --> re
  __server_app_py --> uuid
  __server_role_metrics_py --> ev_grid_oracle_models
  __ev_grid_oracle_personas_py --> typing
  __tools_export_grpo_tensorboard_plots_py --> tensorboard_backend_event_processing_event_accumulator
  __tools_build_roads_render_py --> pathlib
  __viz_record_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_city_graph_py --> __future__
  __ev_grid_oracle_env_py --> personas
  __server_app_py --> ev_grid_oracle_env
  __tools_build_road_graph_py --> __future__
  __tests_test_reward_py --> ev_grid_oracle_reward
  __ev_grid_oracle_scenarios_py --> typing
  __ev_grid_oracle_models_py --> pydantic
  __ev_grid_oracle_grid_sim_py --> dataclasses
  __tools_write_eval_snapshot_py --> os
  __ev_grid_oracle_reward_py --> models
  __ev_grid_oracle_bescom_feed_py --> random
  __ev_grid_oracle_road_env_py --> server_road_router
```
