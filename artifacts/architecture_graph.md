# Architecture Graph

```mermaid
graph TD
  __ev_grid_oracle_multi_agent_py["./ev_grid_oracle/multi_agent.py"]
  openenv_core_env_server_types["openenv.core.env_server.types"]
  ev_grid_oracle_parsing["ev_grid_oracle.parsing"]
  __tools_fetch_osm_roads_py["./tools/fetch_osm_roads.py"]
  __tests_test_fair_eval_mcnemar_py["./tests/test_fair_eval_mcnemar.py"]
  pydantic["pydantic"]
  PIL["PIL"]
  __server___init___py["./server/__init__.py"]
  scenarios["scenarios"]
  __ev_grid_oracle_env_py["./ev_grid_oracle/env.py"]
  collections["collections"]
  ev_grid_oracle_models["ev_grid_oracle.models"]
  jinja2["jinja2"]
  peft["peft"]
  __tools_build_road_graph_py["./tools/build_road_graph.py"]
  logging["logging"]
  __tools___init___py["./tools/__init__.py"]
  __tools_docs_sync_py["./tools/docs_sync.py"]
  __tests_test_models_and_graph_py["./tests/test_models_and_graph.py"]
  reward["reward"]
  __tools_generate_architecture_diagrams_py["./tools/generate_architecture_diagrams.py"]
  ev_grid_oracle_policies["ev_grid_oracle.policies"]
  tensorboard_backend_event_processing_event_accumulator["tensorboard.backend.event_processing.event_accumulator"]
  ev_grid_oracle_road_env["ev_grid_oracle.road_env"]
  training_fair_eval["training.fair_eval"]
  ev_grid_oracle_road_models["ev_grid_oracle.road_models"]
  __server_ev_grid_road_environment_py["./server/ev_grid_road_environment.py"]
  __ev_grid_oracle___init___py["./ev_grid_oracle/__init__.py"]
  __viz_gradio_demo_py["./viz/gradio_demo.py"]
  __server_ev_grid_environment_py["./server/ev_grid_environment.py"]
  argparse["argparse"]
  __ev_grid_oracle_demand_sim_py["./ev_grid_oracle/demand_sim.py"]
  __tools_prune_osm_geojson_py["./tools/prune_osm_geojson.py"]
  json["json"]
  pytest["pytest"]
  __ev_grid_oracle_road_models_py["./ev_grid_oracle/road_models.py"]
  pygame["pygame"]
  __ev_grid_oracle_parsing_py["./ev_grid_oracle/parsing.py"]
  sys["sys"]
  __training_evaluate_py["./training/evaluate.py"]
  typing["typing"]
  __ev_grid_oracle_policies_py["./ev_grid_oracle/policies.py"]
  __ev_grid_oracle_models_py["./ev_grid_oracle/models.py"]
  __tools_build_roads_render_py["./tools/build_roads_render.py"]
  __training_make_plots_py["./training/make_plots.py"]
  transformers["transformers"]
  server_app["server.app"]
  __ev_grid_oracle_city_graph_py["./ev_grid_oracle/city_graph.py"]
  ev_grid_oracle_oracle_agent["ev_grid_oracle.oracle_agent"]
  openai["openai"]
  __test_script_py["./test_script.py"]
  __viz_record_py["./viz/record.py"]
  math["math"]
  models["models"]
  __ev_grid_oracle_grid_sim_py["./ev_grid_oracle/grid_sim.py"]
  __tools_generate_knowledge_graph_py["./tools/generate_knowledge_graph.py"]
  __tests_test_evaluate_paired_py["./tests/test_evaluate_paired.py"]
  __ev_grid_oracle_traffic_py["./ev_grid_oracle/traffic.py"]
  __server_app_py["./server/app.py"]
  __tests_test_parsing_py["./tests/test_parsing.py"]
  huggingface_hub["huggingface_hub"]
  __ev_grid_oracle_road_env_py["./ev_grid_oracle/road_env.py"]
  __server_road_router_py["./server/road_router.py"]
  __training_fair_eval_py["./training/fair_eval.py"]
  policies["policies"]
  training_evaluate["training.evaluate"]
  env["env"]
  pathlib["pathlib"]
  __ev_grid_oracle_oracle_agent_py["./ev_grid_oracle/oracle_agent.py"]
  datetime["datetime"]
  __viz_record_two_phase_py["./viz/record_two_phase.py"]
  gzip["gzip"]
  __ev_grid_oracle_personas_py["./ev_grid_oracle/personas.py"]
  enum["enum"]
  re["re"]
  gradio["gradio"]
  networkx["networkx"]
  ev_grid_oracle_city_graph["ev_grid_oracle.city_graph"]
  ev_grid_oracle_multi_agent["ev_grid_oracle.multi_agent"]
  matplotlib_pyplot["matplotlib.pyplot"]
  statistics["statistics"]
  copy["copy"]
  __ev_grid_oracle_reward_py["./ev_grid_oracle/reward.py"]
  __tools_generate_health_dashboard_py["./tools/generate_health_dashboard.py"]
  urllib_request["urllib.request"]
  fastapi_testclient["fastapi.testclient"]
  reward_hack["reward_hack"]
  openenv_core_env_server_interfaces["openenv.core.env_server.interfaces"]
  __tests_test_policies_collapse_py["./tests/test_policies_collapse.py"]
  grid_sim["grid_sim"]
  __tests_test_demo_api_py["./tests/test_demo_api.py"]
  __viz___init___py["./viz/__init__.py"]
  time["time"]
  subprocess["subprocess"]
  __tests_test_env_determinism_py["./tests/test_env_determinism.py"]
  road_models["road_models"]
  torch["torch"]
  ev_grid_oracle_reward["ev_grid_oracle.reward"]
  ev_grid_oracle_env["ev_grid_oracle.env"]
  ev_grid_oracle_scenarios["ev_grid_oracle.scenarios"]
  __ev_grid_oracle_reward_hack_py["./ev_grid_oracle/reward_hack.py"]
  uuid["uuid"]
  server_ev_grid_environment["server.ev_grid_environment"]
  __viz_city_map_py["./viz/city_map.py"]
  demand_sim["demand_sim"]
  __tools_write_eval_snapshot_py["./tools/write_eval_snapshot.py"]
  viz_city_map["viz.city_map"]
  __future__["__future__"]
  personas["personas"]
  fastapi_responses["fastapi.responses"]
  __tests___init___py["./tests/__init__.py"]
  __tests_test_world_model_verifier_py["./tests/test_world_model_verifier.py"]
  ast["ast"]
  __ev_grid_oracle_scenarios_py["./ev_grid_oracle/scenarios.py"]
  city_graph["city_graph"]
  __tools_sync_space_to_hub_py["./tools/sync_space_to_hub.py"]
  openenv_core_env_server_http_server["openenv.core.env_server.http_server"]
  __tests_test_reward_py["./tests/test_reward.py"]
  random["random"]
  uvicorn["uvicorn"]
  threading["threading"]
  concurrent_futures["concurrent.futures"]
  bescom_feed["bescom_feed"]
  __ev_grid_oracle_bescom_feed_py["./ev_grid_oracle/bescom_feed.py"]
  __tools_export_grpo_tensorboard_plots_py["./tools/export_grpo_tensorboard_plots.py"]
  hashlib["hashlib"]
  server_role_metrics["server.role_metrics"]
  __tools_road_reward_smoke_py["./tools/road_reward_smoke.py"]
  __server_role_metrics_py["./server/role_metrics.py"]
  fastapi["fastapi"]
  ev_grid_oracle_world_model_verifier["ev_grid_oracle.world_model_verifier"]
  dataclasses["dataclasses"]
  __training___init___py["./training/__init__.py"]
  server_road_router["server.road_router"]
  __ev_grid_oracle_world_model_verifier_py["./ev_grid_oracle/world_model_verifier.py"]
  ev_grid_oracle_traffic["ev_grid_oracle.traffic"]
  __tools_fetch_bangalore_roads_overpass_py["./tools/fetch_bangalore_roads_overpass.py"]
  urllib_parse["urllib.parse"]
  os["os"]
  fastapi_staticfiles["fastapi.staticfiles"]
  server_ev_grid_road_environment["server.ev_grid_road_environment"]
  __ev_grid_oracle_city_graph_py --> networkx
  __ev_grid_oracle_oracle_agent_py --> dataclasses
  __ev_grid_oracle_models_py --> __future__
  __viz_gradio_demo_py --> ev_grid_oracle_env
  __server_app_py --> os
  __tools_build_roads_render_py --> __future__
  __server_app_py --> server_road_router
  __viz_city_map_py --> pygame
  __test_script_py --> pydantic
  __tools_docs_sync_py --> logging
  __ev_grid_oracle_city_graph_py --> models
  __tests_test_env_determinism_py --> pydantic
  __tests_test_env_determinism_py --> ev_grid_oracle_city_graph
  __viz_record_two_phase_py --> viz_city_map
  __tests_test_world_model_verifier_py --> ev_grid_oracle_policies
  __server_role_metrics_py --> __future__
  __tools_generate_health_dashboard_py --> os
  __tools_sync_space_to_hub_py --> argparse
  __training_fair_eval_py --> typing
  __tools_fetch_osm_roads_py --> json
  __ev_grid_oracle_models_py --> openenv_core_env_server_types
  __tools_prune_osm_geojson_py --> argparse
  __training_make_plots_py --> argparse
  __tools_build_roads_render_py --> json
  __tests_test_policies_collapse_py --> ev_grid_oracle_policies
  __ev_grid_oracle_multi_agent_py --> typing
  __tools_build_roads_render_py --> argparse
  __viz_record_two_phase_py --> ev_grid_oracle_city_graph
  __viz_city_map_py --> ev_grid_oracle_models
  __viz_record_two_phase_py --> argparse
  __tools_generate_health_dashboard_py --> datetime
  __server_ev_grid_environment_py --> openenv_core_env_server_interfaces
  __ev_grid_oracle_env_py --> demand_sim
  __ev_grid_oracle_traffic_py --> math
  __tools_write_eval_snapshot_py --> pathlib
  __ev_grid_oracle_road_env_py --> dataclasses
  __ev_grid_oracle_multi_agent_py --> env
  __training_evaluate_py --> ev_grid_oracle_city_graph
  __tools_generate_architecture_diagrams_py --> os
  __server_ev_grid_road_environment_py --> ev_grid_oracle_road_models
  __ev_grid_oracle_oracle_agent_py --> peft
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_policies
  __ev_grid_oracle_env_py --> personas
  __training_make_plots_py --> pathlib
  __viz_record_py --> viz_city_map
  __server_app_py --> collections
  __ev_grid_oracle_bescom_feed_py --> __future__
  __server_ev_grid_road_environment_py --> ev_grid_oracle_road_env
  __tests_test_parsing_py --> ev_grid_oracle_parsing
  __viz_record_py --> ev_grid_oracle_env
  __ev_grid_oracle_road_env_py --> random
  __ev_grid_oracle_oracle_agent_py --> transformers
  __ev_grid_oracle_road_env_py --> server_road_router
  __tools_generate_health_dashboard_py --> urllib_request
  __server_role_metrics_py --> typing
  __tests_test_world_model_verifier_py --> ev_grid_oracle_world_model_verifier
  __viz_gradio_demo_py --> dataclasses
  __tools_sync_space_to_hub_py --> subprocess
  __ev_grid_oracle_traffic_py --> hashlib
  __ev_grid_oracle_models_py --> pydantic
  __training_fair_eval_py --> __future__
  __tools_sync_space_to_hub_py --> sys
  __viz_gradio_demo_py --> __future__
  __tools_build_road_graph_py --> hashlib
  __ev_grid_oracle_multi_agent_py --> models
  __ev_grid_oracle_demand_sim_py --> __future__
  __tools_sync_space_to_hub_py --> pathlib
  __training_evaluate_py --> typing
  __tests_test_evaluate_paired_py --> json
  __ev_grid_oracle_bescom_feed_py --> models
  __ev_grid_oracle_env_py --> reward_hack
  __viz_gradio_demo_py --> ev_grid_oracle_oracle_agent
  __training_evaluate_py --> __future__
  __tools_fetch_bangalore_roads_overpass_py --> json
  __tools_export_grpo_tensorboard_plots_py --> __future__
  __viz_gradio_demo_py --> training_evaluate
  __tools_fetch_osm_roads_py --> argparse
  __ev_grid_oracle_world_model_verifier_py --> grid_sim
  __tools_generate_knowledge_graph_py --> typing
  __ev_grid_oracle_reward_py --> networkx
  __tests_test_env_determinism_py --> pytest
  __tests_test_evaluate_paired_py --> sys
  __tools_export_grpo_tensorboard_plots_py --> argparse
  __ev_grid_oracle_grid_sim_py --> dataclasses
  __tests_test_world_model_verifier_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_reward_hack_py --> models
  __tools_fetch_bangalore_roads_overpass_py --> urllib_parse
  __ev_grid_oracle_reward_py --> math
  __ev_grid_oracle_multi_agent_py --> policies
  __tests_test_env_determinism_py --> ev_grid_oracle_models
  __viz_gradio_demo_py --> PIL
  __ev_grid_oracle_oracle_agent_py --> __future__
  __ev_grid_oracle_oracle_agent_py --> torch
  __server_app_py --> __future__
  __viz_record_two_phase_py --> ev_grid_oracle_oracle_agent
  __tools_export_grpo_tensorboard_plots_py --> re
  __server_app_py --> ev_grid_oracle_oracle_agent
  __ev_grid_oracle_world_model_verifier_py --> copy
  __tests_test_reward_py --> ev_grid_oracle_reward
  __tools_build_road_graph_py --> pathlib
  __training_evaluate_py --> collections
  __ev_grid_oracle_parsing_py --> __future__
  __tools_write_eval_snapshot_py --> os
  __server_app_py --> pydantic
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_models
  __ev_grid_oracle_policies_py --> ev_grid_oracle_city_graph
  __training_fair_eval_py --> pathlib
  __training_make_plots_py --> typing
  __server_road_router_py --> ev_grid_oracle_traffic
  __ev_grid_oracle_road_env_py --> __future__
  __ev_grid_oracle_multi_agent_py --> __future__
  __training_make_plots_py --> matplotlib_pyplot
  __server_app_py --> fastapi_staticfiles
  __tools_road_reward_smoke_py --> re
  __ev_grid_oracle_oracle_agent_py --> typing
  __tools_sync_space_to_hub_py --> __future__
  __server_app_py --> server_role_metrics
  __ev_grid_oracle_city_graph_py --> dataclasses
  __tests_test_world_model_verifier_py --> ev_grid_oracle_models
  __server_app_py --> logging
  __server_ev_grid_environment_py --> ev_grid_oracle_models
  __viz_record_py --> ev_grid_oracle_models
  __viz_gradio_demo_py --> ev_grid_oracle_models
  __server_road_router_py --> typing
  __viz_city_map_py --> ev_grid_oracle_policies
  __ev_grid_oracle_road_env_py --> ev_grid_oracle_city_graph
  __tools_fetch_osm_roads_py --> pathlib
  __tools_prune_osm_geojson_py --> pathlib
  __viz_record_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_bescom_feed_py --> dataclasses
  __tools_road_reward_smoke_py --> __future__
  __ev_grid_oracle_parsing_py --> re
  __ev_grid_oracle_world_model_verifier_py --> models
  __ev_grid_oracle_env_py --> dataclasses
  __tools_generate_knowledge_graph_py --> json
  __tests_test_reward_py --> ev_grid_oracle_models
  __training_evaluate_py --> ev_grid_oracle_env
  __viz_city_map_py --> ev_grid_oracle_env
  __server_role_metrics_py --> ev_grid_oracle_models
  __server_road_router_py --> dataclasses
  __tests_test_reward_py --> ev_grid_oracle_city_graph
  __tools_generate_health_dashboard_py --> jinja2
  __tools_build_roads_render_py --> pathlib
  __tools_generate_knowledge_graph_py --> ast
  __server_app_py --> fastapi
  __training_evaluate_py --> ev_grid_oracle_models
  __training_evaluate_py --> ev_grid_oracle_scenarios
  __ev_grid_oracle_demand_sim_py --> random
  __tools_build_road_graph_py --> gzip
  __tests_test_policies_collapse_py --> __future__
  __server_app_py --> uuid
  __viz_city_map_py --> dataclasses
  __ev_grid_oracle_reward_py --> dataclasses
  __ev_grid_oracle_reward_py --> statistics
  __tests_test_evaluate_paired_py --> pathlib
  __tools_sync_space_to_hub_py --> huggingface_hub
  __ev_grid_oracle_world_model_verifier_py --> env
  __ev_grid_oracle_parsing_py --> models
  __tests_test_policies_collapse_py --> ev_grid_oracle_env
  __tools_fetch_bangalore_roads_overpass_py --> argparse
  __tools_fetch_bangalore_roads_overpass_py --> typing
  __training_fair_eval_py --> math
  __ev_grid_oracle_env_py --> bescom_feed
  __tools_build_road_graph_py --> dataclasses
  __ev_grid_oracle_personas_py --> typing
  __ev_grid_oracle_world_model_verifier_py --> statistics
  __tests_test_demo_api_py --> fastapi_testclient
  __ev_grid_oracle_road_env_py --> road_models
  __ev_grid_oracle_grid_sim_py --> __future__
  __tests_test_evaluate_paired_py --> ev_grid_oracle_city_graph
  __training_evaluate_py --> argparse
  __ev_grid_oracle_oracle_agent_py --> threading
  __server_app_py --> typing
  __training_evaluate_py --> os
  __tools_prune_osm_geojson_py --> __future__
  __ev_grid_oracle_bescom_feed_py --> hashlib
  __viz_city_map_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_reward_py --> models
  __tests_test_models_and_graph_py --> pytest
  __ev_grid_oracle_env_py --> typing
  __server_app_py --> time
  __training_make_plots_py --> json
  __tools_build_road_graph_py --> __future__
  __ev_grid_oracle_parsing_py --> typing
  __server_app_py --> server_ev_grid_road_environment
  __tools_build_road_graph_py --> networkx
  __ev_grid_oracle_env_py --> grid_sim
  __tests_test_world_model_verifier_py --> ev_grid_oracle_env
  __server_app_py --> ev_grid_oracle_multi_agent
  __viz_record_two_phase_py --> ev_grid_oracle_models
  __server_app_py --> ev_grid_oracle_traffic
  __tools_generate_health_dashboard_py --> subprocess
  __server_app_py --> ev_grid_oracle_city_graph
  __tools_generate_health_dashboard_py --> openai
  __ev_grid_oracle_bescom_feed_py --> random
  __ev_grid_oracle_models_py --> typing
  __server_ev_grid_environment_py --> ev_grid_oracle_city_graph
  __server_app_py --> server_ev_grid_environment
  __tools_export_grpo_tensorboard_plots_py --> matplotlib_pyplot
  __server_ev_grid_road_environment_py --> __future__
  __server_road_router_py --> pathlib
  __ev_grid_oracle_road_models_py --> __future__
  __server_road_router_py --> __future__
  __server_ev_grid_environment_py --> uuid
  __ev_grid_oracle_personas_py --> dataclasses
  __tests_test_models_and_graph_py --> ev_grid_oracle_models
  __tools_fetch_bangalore_roads_overpass_py --> urllib_request
  __training_fair_eval_py --> argparse
  __ev_grid_oracle_reward_py --> __future__
  __server_ev_grid_environment_py --> ev_grid_oracle_env
  __tests_test_env_determinism_py --> __future__
  __tools_generate_architecture_diagrams_py --> logging
  __ev_grid_oracle_scenarios_py --> dataclasses
  __tests_test_reward_py --> ev_grid_oracle_env
  __tests_test_env_determinism_py --> ev_grid_oracle_policies
  __tests_test_evaluate_paired_py --> os
  __tools_fetch_osm_roads_py --> dataclasses
  __tests_test_models_and_graph_py --> ev_grid_oracle_env
  __tools_fetch_osm_roads_py --> time
  __training_evaluate_py --> json
  __tests_test_env_determinism_py --> ev_grid_oracle_env
  __training_evaluate_py --> statistics
  __viz_record_py --> pygame
  __viz_record_py --> ev_grid_oracle_policies
  __ev_grid_oracle_demand_sim_py --> math
  __tools_fetch_bangalore_roads_overpass_py --> pathlib
  __ev_grid_oracle_reward_hack_py --> __future__
  __ev_grid_oracle_city_graph_py --> __future__
  __viz_gradio_demo_py --> ev_grid_oracle_city_graph
  __ev_grid_oracle_traffic_py --> __future__
  __tools_write_eval_snapshot_py --> sys
  __server_ev_grid_road_environment_py --> openenv_core_env_server_types
  __viz_record_two_phase_py --> ev_grid_oracle_policies
  __tests_test_fair_eval_mcnemar_py --> training_fair_eval
  __viz_city_map_py --> math
  __tools_build_road_graph_py --> math
  __ev_grid_oracle_road_models_py --> pydantic
  __viz_record_two_phase_py --> pathlib
  __tools_docs_sync_py --> ast
  __ev_grid_oracle_models_py --> enum
  __tools_generate_knowledge_graph_py --> logging
  __ev_grid_oracle_env_py --> networkx
  __server_app_py --> networkx
  __tests_test_evaluate_paired_py --> pytest
  __tools_prune_osm_geojson_py --> json
  __ev_grid_oracle_personas_py --> __future__
  __server_app_py --> uvicorn
  __ev_grid_oracle_road_models_py --> openenv_core_env_server_types
  __server_ev_grid_environment_py --> openenv_core_env_server_types
  __ev_grid_oracle_city_graph_py --> typing
  __ev_grid_oracle_env_py --> __future__
  __ev_grid_oracle_env_py --> scenarios
  __training_evaluate_py --> ev_grid_oracle_policies
  __tests_test_demo_api_py --> server_app
  __ev_grid_oracle_grid_sim_py --> math
  __tools_docs_sync_py --> os
  __training_fair_eval_py --> matplotlib_pyplot
  __ev_grid_oracle_policies_py --> __future__
  __viz_record_two_phase_py --> typing
  __server_app_py --> openenv_core_env_server_http_server
  __tools_export_grpo_tensorboard_plots_py --> pathlib
  __viz_record_two_phase_py --> __future__
  __ev_grid_oracle_personas_py --> random
  __tests_test_models_and_graph_py --> ev_grid_oracle_city_graph
  __tools_fetch_osm_roads_py --> urllib_request
  __ev_grid_oracle_oracle_agent_py --> ev_grid_oracle_parsing
  __ev_grid_oracle_policies_py --> ev_grid_oracle_models
  __server_app_py --> ev_grid_oracle_policies
  __viz_record_py --> __future__
  __viz_city_map_py --> typing
  __tools_write_eval_snapshot_py --> subprocess
  __ev_grid_oracle_env_py --> random
  __tools_prune_osm_geojson_py --> ev_grid_oracle_city_graph
  __viz_gradio_demo_py --> ev_grid_oracle_policies
  __server_app_py --> ev_grid_oracle_world_model_verifier
  __ev_grid_oracle_scenarios_py --> typing
  __tests_test_evaluate_paired_py --> training_evaluate
  __server_road_router_py --> networkx
  __ev_grid_oracle_road_env_py --> networkx
  __ev_grid_oracle_world_model_verifier_py --> __future__
  __server_app_py --> concurrent_futures
  __server_ev_grid_environment_py --> __future__
  __ev_grid_oracle_world_model_verifier_py --> dataclasses
  __training_make_plots_py --> __future__
  __viz_record_two_phase_py --> ev_grid_oracle_env
  __server_road_router_py --> json
  __ev_grid_oracle_reward_hack_py --> dataclasses
  __server_ev_grid_road_environment_py --> openenv_core_env_server_interfaces
  __viz_record_two_phase_py --> pygame
  __tests_test_evaluate_paired_py --> ev_grid_oracle_env
  __tools_prune_osm_geojson_py --> sys
  __server_app_py --> ev_grid_oracle_road_models
  __tools_docs_sync_py --> re
  __tests_test_evaluate_paired_py --> __future__
  __tools_fetch_bangalore_roads_overpass_py --> __future__
  __training_fair_eval_py --> json
  __tests_test_reward_py --> typing
  __ev_grid_oracle_env_py --> reward
  __server_app_py --> fastapi_responses
  __tests_test_policies_collapse_py --> ev_grid_oracle_city_graph
  __server_road_router_py --> gzip
  __tools_generate_architecture_diagrams_py --> ast
  __tests_test_policies_collapse_py --> ev_grid_oracle_models
  __training_make_plots_py --> math
  __training_evaluate_py --> ev_grid_oracle_oracle_agent
  __tools_build_road_graph_py --> json
  __ev_grid_oracle_env_py --> city_graph
  __viz_gradio_demo_py --> typing
  __viz_record_py --> argparse
  __ev_grid_oracle_demand_sim_py --> dataclasses
  __ev_grid_oracle_env_py --> models
  __tools_build_roads_render_py --> typing
  __server_app_py --> ev_grid_oracle_env
  __tools_road_reward_smoke_py --> ev_grid_oracle_road_env
  __tools_road_reward_smoke_py --> ev_grid_oracle_road_models
  __ev_grid_oracle_traffic_py --> dataclasses
  __server_app_py --> hashlib
  __tests_test_evaluate_paired_py --> subprocess
  __viz_record_py --> pathlib
  __ev_grid_oracle_multi_agent_py --> dataclasses
  __tools_write_eval_snapshot_py --> __future__
  __server_app_py --> pathlib
  __server_road_router_py --> math
  __ev_grid_oracle_city_graph_py --> math
  __tools_fetch_osm_roads_py --> urllib_parse
  __tools_generate_architecture_diagrams_py --> re
  __server_app_py --> ev_grid_oracle_parsing
  __tools_generate_health_dashboard_py --> json
  __tests_test_fair_eval_mcnemar_py --> __future__
  __tools_sync_space_to_hub_py --> os
  __server_app_py --> ev_grid_oracle_models
  __tools_generate_knowledge_graph_py --> os
  __ev_grid_oracle_scenarios_py --> __future__
  __viz_record_py --> typing
  __viz_gradio_demo_py --> gradio
  __viz_city_map_py --> __future__
  __tools_fetch_osm_roads_py --> __future__
  __server_app_py --> ev_grid_oracle_scenarios
  __training_evaluate_py --> dataclasses
  __tools_export_grpo_tensorboard_plots_py --> tensorboard_backend_event_processing_event_accumulator
  __server_ev_grid_road_environment_py --> uuid
  __tools_build_road_graph_py --> typing
  __tools_fetch_bangalore_roads_overpass_py --> time
  __tools_build_road_graph_py --> argparse
  __server_app_py --> ev_grid_oracle_reward
```
