# Graph Report - tests  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1300 nodes · 3013 edges · 60 communities (49 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- This report represents the complete pre-commit working tree, including local changes.
- See `manifest.json` for per-file content hashes.
- Refresh all layers with `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py` (or invoke `/commit`, which runs it first).
## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 49
- Community 51
- Community 52
- Community 57
- Community 58
- Community 59

## God Nodes (most connected - your core abstractions)
1. `_database()` - 20 edges
2. `period()` - 20 edges
3. `FakeTransport` - 19 edges
4. `_database()` - 18 edges
5. `_request()` - 17 edges
6. `_fake_files()` - 17 edges
7. `SyntheticTransport` - 16 edges
8. `FixedClock` - 15 edges
9. `_config()` - 15 edges
10. `_FakeMutex` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_correction_failure_at_each_boundary_preserves_prior_game()` --calls--> `replace()`  [INFERRED]
  database/games/test_persistence.py → database/games/test_raw_storage.py
- `test_interrupted_active_game_rolls_back_without_removing_earlier_commit()` --calls--> `replace()`  [INFERRED]
  database/games/test_persistence.py → database/games/test_raw_storage.py
- `test_repeated_and_cross_game_positions_reuse_db02_identity()` --calls--> `replace()`  [INFERRED]
  database/games/test_persistence.py → database/games/test_raw_storage.py
- `test_valid_correction_replaces_every_metadata_field_and_occurrence()` --calls--> `replace()`  [INFERRED]
  database/games/test_persistence.py → database/games/test_raw_storage.py
- `submit()` --calls--> `_request()`  [EXTRACTED]
  database/positions/test_training_requirements_concurrency.py → database/positions/test_training_answers.py

## Import Cycles
- None detected.

## Communities (60 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (55): chess_move_trainer_database, chess_move_trainer_database_connection, chess_move_trainer_database_schema, chess_move_trainer_database_statistics, _normalized_sql(), Connection, Path, test_canonical_resource_is_installed_and_schema_is_exact() (+47 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (52): chess_move_trainer_database_games, chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, chess_move_trainer_database_games_reading, chess_move_trainer_database_games_search, _step(), test_from_step_requires_one_unambiguous_match(), test_suite_stops_at_failure_and_resumes_at_that_check() (+44 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (34): chess_move_trainer_database_preferred_moves, _database(), _period_values(), parametrize, Path, Preference, PreferredMoveRepository, _removal_request() (+26 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (28): chess_move_trainer_database_openings, _fake_files(), FakeTransport, _file_urls(), _parent_snapshot(), BaseException, MonkeyPatch, parametrize (+20 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (26): chess_move_trainer_database_games_acquisition, chess_move_trainer_database_openings_acquisition, parametrize, test_lifecycle_adapter_rejects_a_service_destination_override(), test_lifecycle_adapters_forward_fixed_path_service_results(), test_lifecycle_adapters_preserve_service_exit_mapping(), _counts(), FixedClock (+18 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (28): chess, chess_move_trainer_database_positions, _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, StockfishAnalysis (+20 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (33): chess_move_trainer_database_preferred_moves_ranges, _period_values(), parametrize, Path, PreferredMoveRepository, _run_serialized_delete_and_put(), delete_mutation(), first_target() (+25 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (27): _database(), _FakeClock, _FakeEngine, _FakeMutex, AnalysisQuality, AnalysisResultInput, Any, Path (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (18): checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), checkA11y(), expectDescriptionAssociation(), expectStaticGraphic() (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (29): backend_app_features_analysis, backend_app_features_analysis_engine, backend_app_features_analysis_errors, _database(), parametrize, Path, _queue(), _result() (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (29): chess_move_trainer_database_preferred_moves_repository, chess_move_trainer_database_preferred_moves_setup, CliRunner, MonkeyPatch, parametrize, _runner(), test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt(), test_preferred_moves_setup_help_registers_exact_command_without_options() (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (30): chess_move_trainer_database_proof, chess_move_trainer_database_stockfish, ctypes, _database(), Path, test_measurement_output_is_aggregate_only(), test_real_direct_database_records_query_plans_and_timings(), _child_process() (+22 more)

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (27): _database(), _game(), _install_analysis(), _install_opening(), _install_preference(), _occurrence(), _position_id(), Connection (+19 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (12): _FakeFactory, _FakeProcess, _FakeStdin, _FakeStdout, Any, test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs(), test_identity_failure_terminates_the_child(), test_terminal_position_returns_no_lines_without_a_search() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.16
Nodes (21): BenchmarkRunner, BenchmarkSpec, csv, _fake_analysis(), _FakeEngine, _FakeFactory, _InjectedWriter, Any (+13 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (26): chess_move_trainer_database_analysis, chess_move_trainer_database_analysis_reading, _line(), _lines(), AnalysisLine, AnalysisQuality, AnalysisRepository, Path (+18 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (26): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.26
Nodes (26): AcquireConfiguration, _archive_url(), _config(), FixedClock, _fixture(), _month_url(), Any, datetime (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (27): chess_move_trainer_database_games_configuration, chess_move_trainer_database_games_raw_storage, chess_move_trainer_database_openings_recognition, chess_move_trainer_database_openings_source, _database_rows(), _publish(), parametrize, Path (+19 more)

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (25): chess_move_trainer_database_openings_persistence, _copy_fixture(), parametrize, Path, test_invalid_batch_raises_source_error_without_returning_partial_result(), test_non_directory_source_is_rejected(), test_reordered_rows_and_files_produce_the_same_deterministic_result(), test_result_is_immutable_and_does_not_retain_a_board() (+17 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (19): _artifact_fixture(), _assert_relative_catalogue_path(), _graph_path_values(), MonkeyPatch, Path, _single_layer_catalogue(), test_allowlist_cleanup_removes_known_tree_but_refuses_unknown_content(), test_artifact_contract_rejects_missing_and_unexpected_entries() (+11 more)

### Community 21 - "Community 21"
Cohesion: 0.17
Nodes (26): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+18 more)

### Community 22 - "Community 22"
Cohesion: 0.16
Nodes (21): AnalysisTerminalKind, CanonicalPosition, _line(), _position(), AnalysisLine, AnalysisResultInput, parametrize, _result() (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (22): period(), NormalizedPeriod, parametrize, Preference, test_adjacent_equal_move_and_no_preference_states_merge(), test_equal_overlay_extends_and_merges_across_an_existing_boundary(), test_insertion_into_empty_schedule_is_exact(), test_normalization_rejects_out_of_order_overlap_and_nonfinal_indefinite() (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (18): chess_move_trainer_database_games_persistence_repository, _count(), _game_snapshot(), MonkeyPatch, Path, _raw(), test_batched_occurrence_writes_preserve_exact_rows(), test_bulk_failure_rolls_back_all_games_and_retains_skip_reporting() (+10 more)

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (16): BulkRunner, _database(), _FakeEngine, _FakeMutex, Path, StockfishAnalysis, _RecordingPublisher, _runner() (+8 more)

### Community 26 - "Community 26"
Cohesion: 0.17
Nodes (19): _line(), AnalysisLine, AnalysisResultInput, parametrize, _result(), test_configuration_version_must_be_an_integer_at_least_one(), test_depth_must_be_a_nonnegative_integer(), test_normalized_line_and_result_values_are_immutable() (+11 more)

### Community 27 - "Community 27"
Cohesion: 0.24
Nodes (20): _add_black_training_item(), _fixture(), _game(), _item(), _occurrence(), _opening_route(), _position_fen(), _preference() (+12 more)

### Community 28 - "Community 28"
Cohesion: 0.25
Nodes (18): concurrent_futures, _balance(), _fixture(), _game(), _occurrence(), Connection, parametrize, Path (+10 more)

### Community 29 - "Community 29"
Cohesion: 0.31
Nodes (19): _line(), _lines(), AnalysisLine, AnalysisQuality, AnalysisRepository, Path, _repository(), _result() (+11 more)

### Community 30 - "Community 30"
Cohesion: 0.23
Nodes (16): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+8 more)

### Community 31 - "Community 31"
Cohesion: 0.31
Nodes (18): chess_move_trainer_database_preferred_moves_inference, expected_period(), observation(), periods_for(), NormalizedPeriod, test_candidate_period_starts_on_first_matching_date_not_21st_match(), test_dates_before_first_signal_remain_unconfigured_and_no_no_preference_is_inferred(), test_every_eligible_occurrence_is_counted_including_same_date_duplicates() (+10 more)

### Community 32 - "Community 32"
Cohesion: 0.24
Nodes (15): copy, _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime (+7 more)

### Community 33 - "Community 33"
Cohesion: 0.28
Nodes (17): _configured_database(), _database(), parametrize, Path, _request(), _segment_values(), test_delete_is_immediately_visible_as_unconfigured_in_the_timeline(), test_empty_and_unseen_schedules_are_one_read_only_unconfigured_segment() (+9 more)

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (17): _make_arbitrary_database(), _make_generated_column_database(), CompletedProcess, MonkeyPatch, Path, _run_inspect_cli(), test_atomic_publication_writes_identical_bytes_from_destination_directory(), record_replace() (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.28
Nodes (15): _database(), _position_with_result(), AnalysisQuality, Path, _queue_row(), _result(), test_concurrent_mixed_quality_requests_create_one_position_and_queue_row(), test_current_result_reuse_is_read_only_and_higher_quality_satisfies_browser() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (6): ast, Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (16): chess_move_trainer_database_openings_catalogue, chess_move_trainer_database_openings_keys, _keys(), _make_database(), parametrize, Path, test_catalogue_counts_distinct_usage_and_selects_deterministic_deepest(), test_catalogue_is_deterministic_read_only_and_uses_explicit_path() (+8 more)

### Community 38 - "Community 38"
Cohesion: 0.23
Nodes (15): Board, _candidate(), _corpus_database(), _positions(), parametrize, Path, _run(), _semantic_candidate() (+7 more)

### Community 39 - "Community 39"
Cohesion: 0.44
Nodes (15): AnalysisQuality, Path, _queue_row(), _result(), _setup(), _stored_analysis(), test_browser_completion_after_tool_promotion_publishes_then_releases(), test_claim_is_fifo_and_replaces_a_stale_token_with_fresh_uuid() (+7 more)

### Community 40 - "Community 40"
Cohesion: 0.21
Nodes (14): argparse, count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path, Count lines in a file, tolerating unusual characters. (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.32
Nodes (11): _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped(), test_nullable_metadata_remains_nullable_without_rejecting_game(), test_numeric_end_time_wins_and_start_uses_approved_pgn_fallback() (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.27
Nodes (10): parametrize, Path, test_connection_probe_returns_only_ordinary_package_data(), test_internal_existing_read_write_factory_never_creates_a_missing_target(), test_internal_factory_configures_before_yielding_a_clean_connection(), test_internal_factory_preserves_an_existing_non_default_journal_mode(), test_lock_timeout_override_must_be_finite_and_positive(), test_parent_path_must_exist_and_be_a_directory() (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 45 - "Community 45"
Cohesion: 0.25
Nodes (3): constrainedWidths, desktopWidths, ref_playwright_test

### Community 46 - "Community 46"
Cohesion: 0.50
Nodes (3): Path, _result(), test_public_publish_delegates_to_private_transaction_participant()

### Community 47 - "Community 47"
Cohesion: 0.50
Nodes (3): _load_mapping(), Path, test_games_example_documents_setup_and_update_identity_placeholders()

### Community 49 - "Community 49"
Cohesion: 0.83
Nodes (3): _fixture(), test_repetition_reuses_db02_canonical_keys_while_counters_advance(), test_replay_produces_n_plus_one_outgoing_moves_and_position_counters()

## Knowledge Gaps
- **20 isolated node(s):** `DistributionLabelBox`, `LayoutBounds`, `GEOMETRY_TOLERANCE`, `STORYBOOK_URL`, `OPENING_ITEMS` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 330 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_RecordingPublisher` connect `Community 25` to `Community 26`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `DistributionLabelBox`, `LayoutBounds`, `GEOMETRY_TOLERANCE` to the rest of the system?**
  _20 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05336951605608322 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07103825136612021 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.11212121212121212 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.14376321353065538 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.08748615725359911 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
