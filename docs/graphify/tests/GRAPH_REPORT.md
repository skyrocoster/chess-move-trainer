# Graph Report - tests  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1222 nodes · 2652 edges · 83 communities (68 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 110 edges (avg confidence: 0.85)
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
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 68
- Community 69
- Community 71
- Community 73
- Community 74
- Community 81
- Community 82

## God Nodes (most connected - your core abstractions)
1. `period()` - 20 edges
2. `_database()` - 20 edges
3. `FakeTransport` - 19 edges
4. `_database()` - 18 edges
5. `_fake_files()` - 17 edges
6. `_request()` - 17 edges
7. `SyntheticTransport` - 16 edges
8. `FixedClock` - 15 edges
9. `_config()` - 15 edges
10. `_FakeMutex` - 14 edges

## Surprising Connections (you probably didn't know these)
- `submit()` --calls--> `_request()`  [EXTRACTED]
  database/positions/test_training_requirements_concurrency.py → database/positions/test_training_answers.py
- `checkA11y()` --calls--> `retryAxeWhenBusy()`  [EXTRACTED]
  e2e/analysis-panel-storybook.spec.ts → e2e/axe-busy-retry.ts
- `checkA11y()` --calls--> `retryAxeWhenBusy()`  [EXTRACTED]
  e2e/board-adapter-storybook.spec.ts → e2e/axe-busy-retry.ts
- `assertFixtureStates()` --calls--> `retryAxeWhenBusy()`  [EXTRACTED]
  e2e/design-system-accessibility-storybook.spec.ts → e2e/axe-busy-retry.ts
- `checkA11y()` --calls--> `retryAxeWhenBusy()`  [EXTRACTED]
  e2e/line-library-storybook.spec.ts → e2e/axe-busy-retry.ts

## Import Cycles
- None detected.

## Communities (83 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (27): _fake_files(), FakeTransport, _file_urls(), _parent_snapshot(), BaseException, MonkeyPatch, parametrize, Path (+19 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (38): _database(), _game(), _install_analysis(), _install_opening(), _install_preference(), _occurrence(), _position_id(), Connection (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (23): parametrize, test_lifecycle_adapter_rejects_a_service_destination_override(), test_lifecycle_adapters_forward_fixed_path_service_results(), test_lifecycle_adapters_preserve_service_exit_mapping(), _counts(), FixedClock, _game_fixture(), GameTransport (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (27): _database(), _FakeClock, _FakeEngine, _FakeMutex, AnalysisQuality, AnalysisResultInput, Any, datetime (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (18): checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), checkA11y(), expectDescriptionAssociation(), expectStaticGraphic() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (30): _database(), _period_values(), parametrize, Path, Preference, PreferredMoveRepository, _removal_request(), _request() (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (26): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+18 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (11): _FakeFactory, _FakeProcess, _FakeStdin, _FakeStdout, Any, test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs(), test_identity_failure_terminates_the_child(), test_terminal_position_returns_no_lines_without_a_search() (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (20): BenchmarkRunner, BenchmarkSpec, _fake_analysis(), _FakeEngine, _FakeFactory, _InjectedWriter, Any, Path (+12 more)

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (26): AcquireConfiguration, _archive_url(), _config(), FixedClock, _fixture(), _month_url(), Any, datetime (+18 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (20): _artifact_fixture(), _assert_relative_catalogue_path(), _graph_path_values(), _single_layer_catalogue(), test_allowlist_cleanup_removes_known_tree_but_refuses_unknown_content(), test_artifact_contract_rejects_missing_and_unexpected_entries(), test_catalogue_stops_at_failing_layer(), test_commands_use_code_only_no_label_and_application_interpreter() (+12 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (26): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+18 more)

### Community 12 - "Community 12"
Cohesion: 0.16
Nodes (21): AnalysisTerminalKind, CanonicalPosition, _line(), _position(), AnalysisLine, AnalysisResultInput, parametrize, _result() (+13 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (23): period(), NormalizedPeriod, parametrize, Preference, test_adjacent_equal_move_and_no_preference_states_merge(), test_date_values_reject_timestamp_precision(), test_equal_overlay_extends_and_merges_across_an_existing_boundary(), test_insertion_into_empty_schedule_is_exact() (+15 more)

### Community 14 - "Community 14"
Cohesion: 0.16
Nodes (17): BulkRunner, _database(), _FakeEngine, _FakeMutex, AnalysisResultInput, Path, StockfishAnalysis, _RecordingPublisher (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.27
Nodes (19): _line(), _lines(), AnalysisLine, AnalysisQuality, AnalysisRepository, Path, _repository(), _result() (+11 more)

### Community 16 - "Community 16"
Cohesion: 0.20
Nodes (17): _count(), _game_snapshot(), MonkeyPatch, Path, _raw(), test_batched_occurrence_writes_preserve_exact_rows(), test_bulk_failure_rolls_back_all_games_and_retains_skip_reporting(), test_bulk_interruption_rolls_back_all_games_and_propagates() (+9 more)

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (19): test_preferred_moves_public_exports_are_usable_without_handles(), _configured_database(), _database(), parametrize, Path, _request(), _segment_values(), test_delete_is_immediately_visible_as_unconfigured_in_the_timeline() (+11 more)

### Community 18 - "Community 18"
Cohesion: 0.27
Nodes (21): _add_coverage(), _database(), _install_openings(), _occurrence_ids(), parametrize, Path, _raw_game(), _route() (+13 more)

### Community 19 - "Community 19"
Cohesion: 0.24
Nodes (20): _add_black_training_item(), _fixture(), _game(), _item(), _occurrence(), _opening_route(), _position_fen(), _preference() (+12 more)

### Community 20 - "Community 20"
Cohesion: 0.32
Nodes (19): _line(), _lines(), AnalysisLine, AnalysisQuality, AnalysisRepository, Path, _repository(), _result() (+11 more)

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (18): _line(), AnalysisLine, AnalysisResultInput, parametrize, _result(), test_configuration_version_must_be_an_integer_at_least_one(), test_depth_must_be_a_nonnegative_integer(), test_normalized_line_and_result_values_are_immutable() (+10 more)

### Community 22 - "Community 22"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.27
Nodes (17): _balance(), _fixture(), _game(), _occurrence(), Connection, parametrize, Path, _request() (+9 more)

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (17): _make_arbitrary_database(), _make_generated_column_database(), CompletedProcess, MonkeyPatch, Path, _run_inspect_cli(), test_atomic_publication_writes_identical_bytes_from_destination_directory(), record_replace() (+9 more)

### Community 25 - "Community 25"
Cohesion: 0.28
Nodes (15): _database(), _position_with_result(), AnalysisQuality, Path, _queue_row(), _result(), test_concurrent_mixed_quality_requests_create_one_position_and_queue_row(), test_current_result_reuse_is_read_only_and_higher_quality_satisfies_browser() (+7 more)

### Community 26 - "Community 26"
Cohesion: 0.34
Nodes (17): expected_period(), observation(), periods_for(), NormalizedPeriod, test_candidate_period_starts_on_first_matching_date_not_21st_match(), test_dates_before_first_signal_remain_unconfigured_and_no_no_preference_is_inferred(), test_every_eligible_occurrence_is_counted_including_same_date_duplicates(), test_exact_21_match_boundary_qualifies_but_20_does_not() (+9 more)

### Community 27 - "Community 27"
Cohesion: 0.27
Nodes (16): BaseException, parametrize, Path, PreferredMoveRepository, repository(), test_boundary_requires_exactly_four_valid_fen_fields(), test_failed_replacement_restores_the_preexisting_schedule(), test_failure_or_interruption_rolls_back_standalone_position_and_period() (+8 more)

### Community 28 - "Community 28"
Cohesion: 0.41
Nodes (16): _count_periods(), _database(), _game(), _position(), Connection, Path, test_complete_result_validation_rejects_an_illegal_inferred_move_before_insert(), test_later_insert_failure_rolls_back_the_complete_schedule() (+8 more)

### Community 29 - "Community 29"
Cohesion: 0.16
Nodes (10): _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, StockfishAnalysis, test_initial_analysis_is_serial_resumable_direct_and_queue_free(), engine_factory() (+2 more)

### Community 30 - "Community 30"
Cohesion: 0.28
Nodes (14): _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime, Path (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.32
Nodes (16): _database_rows(), _publish(), parametrize, Path, _repository(), _summary(), test_corrupt_persisted_route_fails_as_operational_error(), test_current_prefers_route_then_lexical_name_and_merges_repeated_label_evidence() (+8 more)

### Community 32 - "Community 32"
Cohesion: 0.21
Nodes (14): MonkeyPatch, parametrize, Path, test_an_existing_truly_empty_database_is_initialized(), test_compatible_target_does_not_read_all_existing_bytes(), test_fresh_creation_and_exact_compatible_repeat_are_byte_preserving(), test_internal_compatibility_assertion_accepts_v2_and_leaves_connection_clean(), test_internal_compatibility_assertion_rejects_empty_target_without_modification() (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.23
Nodes (15): Board, _candidate(), _corpus_database(), _positions(), parametrize, Path, _run(), _semantic_candidate() (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.44
Nodes (15): AnalysisQuality, Path, _queue_row(), _result(), _setup(), _stored_analysis(), test_browser_completion_after_tool_promotion_publishes_then_releases(), test_claim_is_fifo_and_replaces_a_stale_token_with_fresh_uuid() (+7 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (5): Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 36 - "Community 36"
Cohesion: 0.26
Nodes (12): _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException, parametrize (+4 more)

### Community 37 - "Community 37"
Cohesion: 0.24
Nodes (12): EngineIdentity, _archive(), _fake_verifier(), parametrize, Path, test_checksum_failure_happens_before_extraction_and_cleans_everything(), test_explicit_override_verifies_identity_and_checksum_without_install(), test_pinned_setup_is_checksum_first_atomic_and_cleans_staging() (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (14): _keys(), _make_database(), parametrize, Path, test_catalogue_counts_distinct_usage_and_selects_deterministic_deepest(), test_catalogue_is_deterministic_read_only_and_uses_explicit_path(), test_catalogue_paginates_empty_and_beyond_end_pages(), test_catalogue_rejects_invalid_filters() (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.32
Nodes (13): _add_game_occurrences(), _add_route(), _database(), _position_ids(), AnalysisQuality, MonkeyPatch, parametrize, Path (+5 more)

### Community 40 - "Community 40"
Cohesion: 0.26
Nodes (12): count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path, Count lines in a file, tolerating unusual characters., Walk the repo and measure every script file. Returns one row per file. (+4 more)

### Community 41 - "Community 41"
Cohesion: 0.26
Nodes (11): CliRunner, MonkeyPatch, parametrize, _runner(), test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt(), setup(), test_preferred_moves_setup_help_registers_exact_command_without_options(), test_preferred_moves_setup_maps_failures_to_stderr_status() (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.39
Nodes (11): _database(), parametrize, Path, _queue(), _result(), test_existing_and_unseen_fens_are_canonical_sparse_read_only_observations(), test_incomplete_current_result_is_rejected_without_fallback(), test_invalid_observation_fens_are_rejected_before_storage_access() (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.39
Nodes (10): parametrize, Path, test_acquire_cli_values_override_only_matching_yaml_values(), test_acquire_rejects_invalid_effective_delay(), test_acquire_rejects_invalid_effective_timeout(), test_acquire_uses_yaml_values_and_exact_defaults(), test_command_specific_invalid_yaml_is_rejected(), test_config_path_must_name_an_existing_file() (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.32
Nodes (11): _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped(), test_nullable_metadata_remains_nullable_without_rejecting_game(), test_numeric_end_time_wins_and_start_uses_approved_pgn_fallback() (+3 more)

### Community 45 - "Community 45"
Cohesion: 0.39
Nodes (11): _copy_fixture(), parametrize, Path, test_invalid_batch_raises_source_error_without_returning_partial_result(), test_non_directory_source_is_rejected(), test_reordered_rows_and_files_produce_the_same_deterministic_result(), test_result_is_immutable_and_does_not_retain_a_board(), test_standard_start_and_legal_replay_are_required() (+3 more)

### Community 46 - "Community 46"
Cohesion: 0.27
Nodes (10): parametrize, Path, test_connection_probe_returns_only_ordinary_package_data(), test_internal_existing_read_write_factory_never_creates_a_missing_target(), test_internal_factory_configures_before_yielding_a_clean_connection(), test_internal_factory_preserves_an_existing_non_default_journal_mode(), test_lock_timeout_override_must_be_finite_and_positive(), test_parent_path_must_exist_and_be_a_directory() (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 48 - "Community 48"
Cohesion: 0.35
Nodes (9): _create_v1_database(), _data_snapshot(), MonkeyPatch, parametrize, Path, test_exact_v1_upgrade_preserves_rows_and_starts_empty_aggregate(), test_exact_v2_upgrade_is_a_byte_preserving_no_op(), test_interrupted_upgrade_rolls_back_additive_ddl_and_version() (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.28
Nodes (4): parametrize, test_one_credit_half_life_halves_signed_adjustment_not_quarters_it(), test_policy_rejects_non_finite_or_out_of_range_values(), test_scoring_rejects_malformed_evidence_counts()

### Community 50 - "Community 50"
Cohesion: 0.50
Nodes (8): _child_process(), Path, test_abandoned_child_acquisition_is_reported_as_acquired(), test_clean_release_allows_the_next_owner(), test_mutex_name_uses_one_normalized_database_identity(), test_real_child_owner_is_busy_then_kernel_releases_on_process_death(), _wait_for_signal(), Popen

### Community 51 - "Community 51"
Cohesion: 0.50
Nodes (6): _assert_same_key_set(), _assert_same_mapping(), _database(), Path, test_real_direct_database_capabilities(), test_real_direct_database_matches_the_retained_source_ledger()

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 53 - "Community 53"
Cohesion: 0.48
Nodes (6): Path, test_each_identity_field_distinguishes_rows(), test_invalid_input_reaches_no_write_path(), test_only_an_existing_compatible_v1_database_is_accepted(), test_repeated_resolution_and_reopen_return_one_stable_integer_id(), test_repository_has_no_update_delete_or_raw_handle_contract()

### Community 54 - "Community 54"
Cohesion: 0.40
Nodes (5): AnalysisQuality, AnalysisResultInput, Path, _result(), test_analysis_reader_returns_complete_current_result()

### Community 55 - "Community 55"
Cohesion: 0.53
Nodes (5): CompletedProcess, Path, _run(), _smoke_arguments(), test_one_position_real_benchmark_is_contained_and_completed_run_is_noop()

### Community 56 - "Community 56"
Cohesion: 0.47
Nodes (5): _normalized_sql(), Connection, Path, test_canonical_resource_is_installed_and_schema_is_exact(), test_unique_constraints_are_exact_and_internal_autoindexes_only()

### Community 57 - "Community 57"
Cohesion: 0.40
Nodes (3): parametrize, test_legal_only_en_passant_normalization(), test_malformed_en_passant_target_is_rejected()

### Community 58 - "Community 58"
Cohesion: 0.50
Nodes (3): Path, _result(), test_public_publish_delegates_to_private_transaction_participant()

### Community 59 - "Community 59"
Cohesion: 0.60
Nodes (4): Path, test_game_reader_returns_ordered_occurrences_including_final(), test_public_game_detail_is_read_only_and_uses_schema_compatibility(), test_public_game_detail_returns_metadata_pgn_and_replayable_fens()

### Community 60 - "Community 60"
Cohesion: 0.60
Nodes (4): _database(), Path, test_measurement_output_is_aggregate_only(), test_real_direct_database_records_query_plans_and_timings()

### Community 61 - "Community 61"
Cohesion: 0.60
Nodes (4): CompletedProcess, Path, _run_worker(), test_one_position_real_worker_publishes_fixed_tool_profile_and_exits()

### Community 62 - "Community 62"
Cohesion: 0.50
Nodes (3): _load_mapping(), Path, test_games_example_documents_setup_and_update_identity_placeholders()

### Community 63 - "Community 63"
Cohesion: 0.60
Nodes (4): Path, test_grouped_resolution_rolls_back_when_later_work_fails(), test_position_remains_after_a_focused_reference_is_removed(), test_successful_multiple_resolution_composes_through_opaque_unit_of_work()

### Community 64 - "Community 64"
Cohesion: 0.70
Nodes (4): _create_v1_database(), Path, test_schema_upgrade_cli_does_not_create_a_missing_target(), test_schema_upgrade_cli_is_explicit_and_existing_only()

### Community 65 - "Community 65"
Cohesion: 0.80
Nodes (4): _database_with_synthetic_occurrences(), Path, test_move_response_distribution_separates_trainer_and_opponent(), test_position_context_counts_distinct_games_and_test_actor()

### Community 68 - "Community 68"
Cohesion: 0.83
Nodes (3): _fixture(), test_repetition_reuses_db02_canonical_keys_while_counters_advance(), test_replay_produces_n_plus_one_outgoing_moves_and_position_counters()

### Community 69 - "Community 69"
Cohesion: 0.67
Nodes (3): Path, _raw_game(), test_indexed_persistence_benchmark_is_bounded_and_aggregate_only()

## Knowledge Gaps
- **20 isolated node(s):** `DistributionLabelBox`, `LayoutBounds`, `GEOMETRY_TOLERANCE`, `STORYBOOK_URL`, `STORY_IDS` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 281 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_removal_request()` connect `Community 5` to `Community 1`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **What connects `DistributionLabelBox`, `LayoutBounds`, `GEOMETRY_TOLERANCE` to the rest of the system?**
  _20 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.14950166112956811 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11295681063122924 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.07657657657657657 - nodes in this community are weakly interconnected._
- **Should `Community 6` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
