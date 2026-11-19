# Destructive Script Report

Heuristic static scan. A hit means the code *can* delete, move, or rename; it does not prove it runs that path.
No script was executed.

## Deletes files/folders (69)

### `engine/00_MASTER_GUI/unified_gui.py`
dry-run: Y · receipts: N
```
804: rd = asdict(rec)
```

### `engine/01_ENGINE/TTS_Pipeline/LAUNCH_SUBSTACK_COPY.bat`
dry-run: N · receipts: N
```
31: del "%temp%\selected_file.txt"
```

### `engine/01_ENGINE/TTS_Pipeline/scripts/get_drive_links.py`
dry-run: Y · receipts: N
```
482: f.unlink()
```

### `engine/01_ENGINE/TTS_Pipeline/scripts/math_translation_manager.py`
dry-run: N · receipts: N
```
59: checkpoint_file.unlink()
274: output_path.unlink()
```

### `engine/01_ENGINE/TTS_Pipeline/scripts/smart_upload_to_drive.py`
dry-run: Y · receipts: N
```
435: audio_path.unlink()
```

### `engine/01_ENGINE/TTS_Pipeline/scripts/tts_pipeline.py`
dry-run: N · receipts: N
```
409: os.remove(temp_path)
```

### `engine/01_ENGINE/backend_scripts/generate_clean_tags.py`
dry-run: N · receipts: N
```
272: old_file.unlink()
```

### `engine/01_ENGINE/backend_scripts/install.py`
dry-run: N · receipts: N
```
104: shutil.rmtree(venv_path)
```

### `engine/01_ENGINE/conversation_to_md/app.py`
dry-run: N · receipts: N
```
106: shutil.rmtree(output_dir, ignore_errors=True)
```

### `engine/01_ENGINE/conversation_to_md/core/pipeline.py`
dry-run: N · receipts: N
```
62: shutil.rmtree(extracted_dir, ignore_errors=True)
89: shutil.rmtree(extracted_dir, ignore_errors=True)
```

### `engine/01_ENGINE/conversation_to_md/utils/unzip.py`
dry-run: N · receipts: N
```
43: tmp_zip.unlink(missing_ok=True)
```

### `engine/01_ENGINE/core/vault_health_engine.py`
dry-run: N · receipts: Y
```
578: p.unlink()
```

### `engine/01_ENGINE/scripts/Edge-TTS/edge_tts_batch.py`
dry-run: Y · receipts: N
```
114: silence_path.unlink()
```

### `engine/01_ENGINE/scripts/MCP_Setup/TROUBLES-MCP-SERVERS.bat`
dry-run: N · receipts: N
```
242: del "%TEMP%\mcp_test.txt"
```

### `engine/01_ENGINE/scripts/MCP_Setup/UNINSTALL-TYPINGMIND-STARTUP.ps1`
dry-run: N · receipts: N
```
10: Remove-Item -Path $startupCmd -Force
```

### `engine/01_ENGINE/scripts/NUMBER_FILES.bat`
dry-run: N · receipts: N
```
63: del "!TMPLIST!" 2>nul
136: del "!TMPLIST!" 2>nul
137: del "!TMPLIST2!" 2>nul
138: del "!TMPLIST3!" 2>nul
```

### `engine/01_ENGINE/scripts/VaultTools.ps1`
dry-run: N · receipts: N
```
230: if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
235: Remove-Item -LiteralPath $groupFolder -Recurse -Force
```

### `engine/01_ENGINE/scripts/find_duplicates.py`
dry-run: Y · receipts: N
```
164: p.unlink()
```

### `engine/01_ENGINE/scripts/from_Note/07.ps1`
dry-run: Y · receipts: N
```
194: Remove-Item $inner -Recurse -Force
```

### `engine/01_ENGINE/scripts/from_Note/sensitivity_analyzer.py`
dry-run: N · receipts: N
```
197: del modified_rubric['variables'][var_key]
223: del modified_rubric['fruits'][fruit_key[0]]
249: del modified_rubric['constraints'][constraint_key[0]]
```

### `engine/01_ENGINE/scripts/python_pipeline/data_command_center/app/core/scheduler.py`
dry-run: N · receipts: N
```
162: del self._schedules[schedule_id]
```

### `engine/01_ENGINE/scripts/python_pipeline/obsidian_programs/lossless_summary_engine/build_lossless_summary.ps1`
dry-run: N · receipts: Y
```
163: if (Test-Path $tmpTxt) { Remove-Item -Path $tmpTxt -Force -ErrorAction SilentlyContinue }
164: if (Test-Path $tmpPy) { Remove-Item -Path $tmpPy -Force -ErrorAction SilentlyContinue }
```

### `engine/01_ENGINE/scripts/vault_score_importer.py`
dry-run: N · receipts: N
```
411: os.remove(filepath)
426: os.rmdir(dirpath)
```

### `engine/01_ENGINE/scripts/vault_watcher.py`
dry-run: N · receipts: N
```
293: path.unlink()
```

### `engine/01_ENGINE/ui/main_window_v2.py`
dry-run: Y · receipts: N
```
2921: template_path.unlink()
```

### `engine/01_ENGINE/ui/tabs/research_linking_tab.py`
dry-run: N · receipts: N
```
351: del self.research_linker.custom_links[term][source]
353: del self.research_linker.custom_links[term]
```

### `engine/01_ENGINE/utility/master_equation_organizer.py`
dry-run: N · receipts: N
```
205: md_file.unlink()
```

### `engine/01_ENGINE/utility/python folder clean.py`
dry-run: N · receipts: N
```
183: path.unlink()
```

### `engine/01_ENGINE/vault_rater.py`
dry-run: Y · receipts: N
```
893: state_path.unlink()
```

### `engine/02_OPENAI/PAPER-REVIEW/rebuild_master_and_cleanup.py`
dry-run: N · receipts: N
```
208: f.unlink()
220: f.unlink()
```

### `engine/02_OPENAI/VAULT-RATER/vault_rater.py`
dry-run: Y · receipts: N
```
892: state_path.unlink()
```

### `engine/08_DATA_ANALYTICS/data_analytics_gui.py`
dry-run: N · receipts: N
```
470: rd = metrics.get('readability_difficulty', 0)
```

### `engine/10_TIE_GRAPH/scripts/export_tie_snapshot.ps1`
dry-run: N · receipts: N
```
20: if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
```

### `engine/80_OPENAI/PAPER-REVIEW/rebuild_master_and_cleanup.py`
dry-run: N · receipts: N
```
208: f.unlink()
220: f.unlink()
```

### `engine/80_OPENAI/VAULT-RATER/vault_rater.py`
dry-run: Y · receipts: N
```
892: state_path.unlink()
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Export-StocksToExcel.ps1`
dry-run: N · receipts: N
```
10: Remove-Item $xl -ErrorAction SilentlyContinue
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/ImportExcel.psm1`
dry-run: N · receipts: N
```
38: if ($env:NoAutoSize) { Remove-Item Env:\NoAutoSize }
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Private/Invoke-ExcelReZipFile.ps1`
dry-run: N · receipts: N
```
20: Remove-Item $ExcelPackage.File -Force
22: Remove-Item $TempZipPath -Recurse -Force
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Public/Convert-ExcelRangeToImage.ps1`
dry-run: N · receipts: N
```
37: del demo*.xlsx
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Public/ConvertTo-ExcelXlsx.ps1`
dry-run: N · receipts: N
```
29: Remove-Item $xlsxPath -Force
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Public/Import-Html.ps1`
dry-run: N · receipts: N
```
13: Remove-Item $xlFile -ErrorAction Ignore
```

### `engine/85_VAULT_TOOLS/Scripts/convert_vault_to_mdx.py`
dry-run: N · receipts: N
```
174: f.unlink()
```

### `engine/85_VAULT_TOOLS/Scripts/extract_axioms_hypotheses.py`
dry-run: N · receipts: N
```
458: p.unlink()
```

### `engine/90_LEGACY/OPENAI_SELECT_AND_ANALYZE.bat`
dry-run: N · receipts: N
```
214: rd /s /q "%temp_folder%"
```

### `engine/90_LEGACY_ARCHIVED_20260323/OPENAI_SELECT_AND_ANALYZE.bat`
dry-run: N · receipts: N
```
214: rd /s /q "%temp_folder%"
```

### `engine/99_LOOSE/aggregate_axioms.py`
dry-run: Y · receipts: Y
```
297: deleted = sum(1 for f in source_files if f.unlink() is None)
```

### `engine/99_LOOSE/gtq_pipeline.py`
dry-run: N · receipts: Y
```
132: link.unlink()
```

### `engine/99_LOOSE/set_folder_lock.py`
dry-run: N · receipts: N
```
41: lock_path.unlink()
```

### `engine/99_LOOSE/sync_architecture_mirror.py`
dry-run: N · receipts: Y
```
171: shutil.rmtree(path)
```

### `standalone_gui/Reusable_Tools_From_Theophysics/API_Station_References/01_ENGINE/02_OPENAI/PAPER-REVIEW/rebuild_master_and_cleanup.py`
dry-run: N · receipts: N
```
208: f.unlink()
220: f.unlink()
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Conversions_and_Data_Tools/01_ENGINE/01_ENGINE/scripts/python_pipeline/data_command_center/app/core/scheduler.py`
dry-run: N · receipts: N
```
162: del self._schedules[schedule_id]
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Conversions_and_Data_Tools/01_ENGINE/Scripts/convert_vault_to_mdx.py`
dry-run: N · receipts: N
```
174: f.unlink()
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/01_ENGINE/core/vault_health_engine.py`
dry-run: N · receipts: Y
```
578: p.unlink()
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/01_ENGINE/scripts/python_pipeline/obsidian_programs/lossless_summary_engine/build_lossless_summary.ps1`
dry-run: N · receipts: Y
```
163: if (Test-Path $tmpTxt) { Remove-Item -Path $tmpTxt -Force -ErrorAction SilentlyContinue }
164: if (Test-Path $tmpPy) { Remove-Item -Path $tmpPy -Force -ErrorAction SilentlyContinue }
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Split_Combine_and_Organize/01_ENGINE/01_ENGINE/scripts/VaultTools.ps1`
dry-run: N · receipts: N
```
230: if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
235: Remove-Item -LiteralPath $groupFolder -Recurse -Force
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Split_Combine_and_Organize/01_ENGINE/01_ENGINE/scripts/find_duplicates.py`
dry-run: Y · receipts: N
```
164: p.unlink()
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Export-StocksToExcel.ps1`
dry-run: N · receipts: N
```
10: Remove-Item $xl -ErrorAction SilentlyContinue
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/ImportExcel.psm1`
dry-run: N · receipts: N
```
38: if ($env:NoAutoSize) { Remove-Item Env:\NoAutoSize }
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Private/Invoke-ExcelReZipFile.ps1`
dry-run: N · receipts: N
```
20: Remove-Item $ExcelPackage.File -Force
22: Remove-Item $TempZipPath -Recurse -Force
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Public/Convert-ExcelRangeToImage.ps1`
dry-run: N · receipts: N
```
37: del demo*.xlsx
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Public/ConvertTo-ExcelXlsx.ps1`
dry-run: N · receipts: N
```
29: Remove-Item $xlsxPath -Force
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Public/Import-Html.ps1`
dry-run: N · receipts: N
```
13: Remove-Item $xlFile -ErrorAction Ignore
```

### `engine/Scripts/convert_vault_to_mdx.py`
dry-run: N · receipts: N
```
174: f.unlink()
```

### `standalone_gui/file_actions.py`
dry-run: N · receipts: Y
```
135: target.unlink(missing_ok=True)
```

### `engine/gtq_pipeline.py`
dry-run: N · receipts: Y
```
132: link.unlink()
```

### `standalone_gui/series_scaffold.py`
dry-run: N · receipts: N
```
397: del self.items[start:end]
438: del self.items[start:end]
454: del self.items[start:end]
```

### `engine/set_folder_lock.py`
dry-run: N · receipts: N
```
41: lock_path.unlink()
```

### `engine/sync_architecture_mirror.py`
dry-run: N · receipts: Y
```
171: shutil.rmtree(path)
```

### `standalone_gui/uninstall_startup.bat`
dry-run: N · receipts: N
```
13: del "%SHORTCUT_PATH%"
```

## Moves or renames (58)

### `engine/01_ENGINE/TTS_Pipeline/LAUNCH_TTS.bat`
dry-run: N · receipts: N
```
97: move "%%F" "%PROCESSED%\" >nul
```

### `engine/01_ENGINE/TTS_Pipeline/scripts/batch_tts.py`
dry-run: N · receipts: N
```
170: shutil.move(input_path, processed_path)
```

### `engine/01_ENGINE/core/vault_health_engine.py`
dry-run: N · receipts: Y
```
543: shutil.move(str(src), str(dst))
```

### `engine/01_ENGINE/launchers/scripts/AXIOM_CLEANUP.bat`
dry-run: N · receipts: N
```
21: move /Y "O:\_Theophysics_v3\AXIOM CHAPTERS" "O:\_Theophysics_v3\.trash\AXIOM_CHAPTERS_REDUNDANT"
29: move /Y "O:\_Theophysics_v3\GO FOLDER\_AXIOMS_001-188" "O:\_Theophysics_v3\.trash\_AXIOMS_001-188_REDUNDANT"
37: move /Y "O:\_Theophysics_v3\THE Axioms Vault" "O:\_Theophysics_v3\.trash\THE_Axioms_Vault_REDUNDANT"
45: move /Y "O:\_Theophysics_v3\00_Canonical\01_AXIOMS" "O:\_Theophysics_v3\.trash\01_AXIOMS_CANONICAL_REDUNDANT"
53: move /Y "O:\_Theophysics_v3\00_Canonical\_AXIOM_ARCHIVE_SUBFOLDERS" "O:\_Theophysics_v3\.trash\_AXIOM_ARCHIVE_SUBFOLDERS_REDUNDANT"
61: move /Y "O:\_Theophysics_v3\00_Canonical\_ARCHIVE\Opus\Axioms" "O:\_Theophysics_v3\.trash\Opus_Axioms_REDUNDANT"
69: move /Y "O:\_Theophysics_v3\00_Canonical\_ARCHIVE\SOCRATIC_AXIOMS" "O:\_Theophysics_v3\.trash\SOCRATIC_AXIOMS_REDUNDANT"
77: move /Y "O:\_Theophysics_v3\GO FOLDER\LOVE_AXIOMS" "O:\_Theophysics_v3\.trash\LOVE_AXIOMS_REDUNDANT"
```

### `engine/01_ENGINE/libs/obsidiantools/api.py`
dry-run: N · receipts: N
```
1157: .rename(columns={'file_exists': 'note_exists'})
1342: .rename(columns={'note_exists': 'file_exists'}))
```

### `engine/01_ENGINE/scripts/MCP_Setup/UNINSTALL-TYPINGMIND-STARTUP.ps1`
dry-run: N · receipts: N
```
10: Remove-Item -Path $startupCmd -Force
```

### `engine/01_ENGINE/scripts/NUMBER_FILES.bat`
dry-run: N · receipts: N
```
123: ren "!FDIR!!FNAME!" "!NEWNAME!" 2>nul
```

### `engine/01_ENGINE/scripts/VaultTools.ps1`
dry-run: N · receipts: N
```
84: Rename-Item -LiteralPath $f.FullName -NewName $tempName
121: Rename-Item -LiteralPath $row.TempFull -NewName $newName
216: Move-Item -LiteralPath $f.FullName -Destination $groupFolder
230: if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
235: Remove-Item -LiteralPath $groupFolder -Recurse -Force
```

### `engine/01_ENGINE/scripts/add_scores_to_folders.py`
dry-run: N · receipts: N
```
112: folder_path.rename(new_path)
```

### `engine/01_ENGINE/scripts/from_Note/07.ps1`
dry-run: Y · receipts: N
```
119: Move-Item $f.FullName $fullDest -Force
161: Move-Item $f.FullName $dest -Force
173: Move-Item $f.FullName $dest -Force
194: Remove-Item $inner -Recurse -Force
```

### `engine/01_ENGINE/scripts/python_pipeline/obsidian_programs/lossless_summary_engine/build_lossless_summary.ps1`
dry-run: N · receipts: Y
```
163: if (Test-Path $tmpTxt) { Remove-Item -Path $tmpTxt -Force -ErrorAction SilentlyContinue }
164: if (Test-Path $tmpPy) { Remove-Item -Path $tmpPy -Force -ErrorAction SilentlyContinue }
```

### `engine/01_ENGINE/scripts/vault_clean.py`
dry-run: Y · receipts: N
```
290: old_path.rename(new_path)
```

### `engine/01_ENGINE/scripts/vault_toolkit.py`
dry-run: Y · receipts: Y
```
277: old.rename(new)
643: shutil.move(str(f["path"]), str(dst))
```

### `engine/01_ENGINE/utility/cleanup_blank_systems.py`
dry-run: N · receipts: N
```
60: shutil.move(src, dst)
66: shutil.move(yaml_src, yaml_dst)
```

### `engine/01_ENGINE/utility/organize_root_folder.py`
dry-run: N · receipts: N
```
26: shutil.move(src_path, os.path.join(SCRIPTS_DIR, filename))
31: shutil.move(src_path, os.path.join(DOCS_DIR, filename))
36: shutil.move(src_path, os.path.join(DOCS_DIR, filename))
```

### `engine/01_ENGINE/utility/process_new_additions.py`
dry-run: N · receipts: N
```
45: shutil.move(src_path, dest_path)
```

### `engine/01_ENGINE/utility/python folder clean.py`
dry-run: N · receipts: N
```
93: Move images into the canonical per‑paper folder under Assets/images.
138: shutil.move(str(path), str(dest_path))
```

### `engine/01_ENGINE/vault_rater.py`
dry-run: Y · receipts: N
```
718: shutil.move(str(src), str(dest))
751: shutil.move(str(src), str(dest))
```

### `engine/02_OPENAI/VAULT-RATER/vault_rater.py`
dry-run: Y · receipts: N
```
717: shutil.move(str(src), str(dest))
750: shutil.move(str(src), str(dest))
```

### `engine/03_VAULT_TOOLS/archive_and_relocate.py`
dry-run: Y · receipts: Y
```
86: shutil.move(str(src), str(dest))
```

### `engine/03_VAULT_TOOLS/file_loose_papers.py`
dry-run: Y · receipts: Y
```
4: Move stray single papers out of vault root / folder roots.
97: shutil.move(str(src), str(dest))
```

### `engine/03_VAULT_TOOLS/organize_canonical.py`
dry-run: Y · receipts: N
```
213: Move file to target category folder.
```

### `engine/03_VAULT_TOOLS/quarantine_mover.py`
dry-run: N · receipts: N
```
84: shutil.move(str(fp), str(dest))
```

### `engine/10_TIE_GRAPH/scripts/export_tie_snapshot.ps1`
dry-run: N · receipts: N
```
20: if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
```

### `engine/80_OPENAI/VAULT-RATER/vault_rater.py`
dry-run: Y · receipts: N
```
717: shutil.move(str(src), str(dest))
750: shutil.move(str(src), str(dest))
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Export-StocksToExcel.ps1`
dry-run: N · receipts: N
```
10: Remove-Item $xl -ErrorAction SilentlyContinue
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/ImportExcel.psm1`
dry-run: N · receipts: N
```
38: if ($env:NoAutoSize) { Remove-Item Env:\NoAutoSize }
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Private/Invoke-ExcelReZipFile.ps1`
dry-run: N · receipts: N
```
20: Remove-Item $ExcelPackage.File -Force
22: Remove-Item $TempZipPath -Recurse -Force
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Public/ConvertTo-ExcelXlsx.ps1`
dry-run: N · receipts: N
```
29: Remove-Item $xlsxPath -Force
```

### `engine/85_VAULT_TOOLS/Scripts/Modules/ImportExcel/7.8.10/Public/Import-Html.ps1`
dry-run: N · receipts: N
```
13: Remove-Item $xlFile -ErrorAction Ignore
```

### `engine/85_VAULT_TOOLS/Scripts/find-duplicate-pics.ps1`
dry-run: N · receipts: N
```
55: Move-Item -Path $file.FullName -Destination $destPath -Force
```

### `engine/85_VAULT_TOOLS/Scripts/image_audit.py`
dry-run: Y · receipts: N
```
212: shutil.move(str(p), str(dest))
236: shutil.move(str(r), str(dest))
```

### `engine/85_VAULT_TOOLS/archive_and_relocate.py`
dry-run: Y · receipts: Y
```
86: shutil.move(str(src), str(dest))
```

### `engine/85_VAULT_TOOLS/file_loose_papers.py`
dry-run: Y · receipts: Y
```
4: Move stray single papers out of vault root / folder roots.
97: shutil.move(str(src), str(dest))
```

### `engine/85_VAULT_TOOLS/organize_canonical.py`
dry-run: Y · receipts: N
```
213: Move file to target category folder.
```

### `engine/85_VAULT_TOOLS/quarantine_mover.py`
dry-run: N · receipts: N
```
84: shutil.move(str(fp), str(dest))
```

### `engine/99_LOOSE/aggregate_axioms.py`
dry-run: Y · receipts: Y
```
252: axioms["_domain"].value_counts().reset_index().rename(
280: .rename(columns={"statement":"axioms_summary"})
```

### `engine/99_LOOSE/engine_reorg.py`
dry-run: Y · receipts: Y
```
41: Move OpenAI tools:
44: Move vault tools:
92: shutil.move(str(src), str(final_dst))
```

### `engine/99_LOOSE/gtq_pipeline.py`
dry-run: N · receipts: Y
```
125: shutil.move(str(f), str(target))
```

### `engine/99_LOOSE/image_enrich.py`
dry-run: Y · receipts: N
```
113: src.rename(dst)
121: old_yaml.rename(new_yaml)
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/01_ENGINE/core/vault_health_engine.py`
dry-run: N · receipts: Y
```
543: shutil.move(str(src), str(dst))
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/01_ENGINE/scripts/python_pipeline/obsidian_programs/lossless_summary_engine/build_lossless_summary.ps1`
dry-run: N · receipts: Y
```
163: if (Test-Path $tmpTxt) { Remove-Item -Path $tmpTxt -Force -ErrorAction SilentlyContinue }
164: if (Test-Path $tmpPy) { Remove-Item -Path $tmpPy -Force -ErrorAction SilentlyContinue }
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/03_VAULT_TOOLS/archive_and_relocate.py`
dry-run: Y · receipts: Y
```
86: shutil.move(str(src), str(dest))
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/03_VAULT_TOOLS/file_loose_papers.py`
dry-run: Y · receipts: Y
```
4: Move stray single papers out of vault root / folder roots.
97: shutil.move(str(src), str(dest))
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/03_VAULT_TOOLS/organize_canonical.py`
dry-run: Y · receipts: N
```
213: Move file to target category folder.
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Obsidian_and_Documents/01_ENGINE/03_VAULT_TOOLS/quarantine_mover.py`
dry-run: N · receipts: N
```
84: shutil.move(str(fp), str(dest))
```

### `standalone_gui/Reusable_Tools_From_Theophysics/Split_Combine_and_Organize/01_ENGINE/01_ENGINE/scripts/VaultTools.ps1`
dry-run: N · receipts: N
```
84: Rename-Item -LiteralPath $f.FullName -NewName $tempName
121: Rename-Item -LiteralPath $row.TempFull -NewName $newName
216: Move-Item -LiteralPath $f.FullName -Destination $groupFolder
230: if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
235: Remove-Item -LiteralPath $groupFolder -Recurse -Force
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Export-StocksToExcel.ps1`
dry-run: N · receipts: N
```
10: Remove-Item $xl -ErrorAction SilentlyContinue
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/ImportExcel.psm1`
dry-run: N · receipts: N
```
38: if ($env:NoAutoSize) { Remove-Item Env:\NoAutoSize }
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Private/Invoke-ExcelReZipFile.ps1`
dry-run: N · receipts: N
```
20: Remove-Item $ExcelPackage.File -Force
22: Remove-Item $TempZipPath -Recurse -Force
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Public/ConvertTo-ExcelXlsx.ps1`
dry-run: N · receipts: N
```
29: Remove-Item $xlsxPath -Force
```

### `engine/Scripts/Modules/ImportExcel/7.8.10/Public/Import-Html.ps1`
dry-run: N · receipts: N
```
13: Remove-Item $xlFile -ErrorAction Ignore
```

### `engine/Scripts/find-duplicate-pics.ps1`
dry-run: N · receipts: N
```
55: Move-Item -Path $file.FullName -Destination $destPath -Force
```

### `engine/Scripts/image_audit.py`
dry-run: Y · receipts: N
```
212: shutil.move(str(p), str(dest))
236: shutil.move(str(r), str(dest))
```

### `engine/engine_reorg.py`
dry-run: Y · receipts: Y
```
41: Move OpenAI tools:
44: Move vault tools:
92: shutil.move(str(src), str(final_dst))
```

### `standalone_gui/file_actions.py`
dry-run: N · receipts: Y
```
57: os.replace(temporary, target)
```

### `engine/gtq_pipeline.py`
dry-run: N · receipts: Y
```
125: shutil.move(str(f), str(target))
```

### `engine/image_enrich.py`
dry-run: Y · receipts: N
```
113: src.rename(dst)
121: old_yaml.rename(new_yaml)
```
