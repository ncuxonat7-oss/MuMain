# Library transfer to a prepared environment: short recovery runbook

Verified incident: 2026-10-12. Publication authorized for the separate overnight checkpoint branch. Do not interrupt or repeat an active database stage to follow this note.

## What resolved this incident

The old consumer 01a12db0 had two failed official Library-helper transfer routes. The reported error was download failed; no HTTP cause or explicit access-denial response was captured. Python 3.12.14, curl 8.14.1, wget 1.25.0 and 154 CA certificates were already available. Installing another downloader was unnecessary.

Only the hostname sdmntpreastus2.oaiusercontent.com was extracted from the returned signed transfer URL. The old consumer's /etc/codex/network-policy.json contained 147 exact restricted rules and did not include that host. The owner approved adding only that hostname. Saving the environment draft did not publish it. After a publication-status access error, the owner refreshed the UI and successfully published environment version 6acc3c7746408195a96a7c62513f1740. The UI error's cause remains unknown; refresh is not a guaranteed remedy.

The old running consumer retained its old policy and was stopped without another transfer retry. New consumer 01a12dd2-edb9-7192-9acb-672e5bf9c00b confirmed the exact host in its actual policy. One official-helper transfer of the baseline attachment then succeeded. Verified destination in that consumer: /workspace/transfer-verification/github-actions-artifact-11651520969.zip. Size: 2,091,291 bytes. SHA256: b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea. Reported active verification time: 45 seconds; transfer: 0.25 seconds. No installation or support intervention was needed. The observed policy mismatch was resolved; the missing HTTP diagnosis still limits any claim about the exact original failure mechanism.

## Second attachment: a different region

The later existing-EF-tools bundle resolved to sdmntprwestus2.oaiusercontent.com, not the first archive's eastus2 host. Child 01a12dd2, turn 01a12de6-45df-72f3-870a-d6679a1d00f5, reported at 02:17:44 UTC that this exact returned hostname was absent from its policy; it did not attempt the download. This demonstrates that one successful attachment's hostname must not be assumed for another attachment.

The owner approved that exact westus2 hostname at 02:18:35 UTC. Setup task 01a12ded saved draft a25c9862bd5c8195b891a9d98bc5a9ab revision 2 with only this domain addition. The owner published at 02:29:44; the catalog confirmed published environment version 6acc45db63e481958283bd5c84e97bc0 at 02:30:53.

Fresh admin executor confirmed both exact hosts in its actual policy before transfer. One current official-helper download per attachment succeeded into /workspace/admin-provision-3f1U4Dge. The baseline matched the size/hash above. admin-ef-existing-tools-20261012.zip matched 13,566,379 bytes and SHA256 e36693ebf7d4a6c38863c5a8b82cf8024e59208097f4692002ddda2ea75dc3f0. Bundle manifest SHA256 ea0a7b03e5d30b99a06dcc3a5a9f01a79044c598993c61aaf135bbf29a1752de and all 125 declared files were verified; 127 archive entries, 41,716,944 unpacked bytes. No new timing metric is inferred. Detailed transfer checks, generator result, admin provisioning and shutdown evidence are now preserved in this checkpoint's evidence directory, replacing the earlier parent evidence-retrieval limitation.

## Reuse this sequence

1. Distinguish file metadata, a conversation attachment, and verified local bytes. A recognized Library item or attachment alone does not prove the target environment can read its contents. A path in another environment is not local availability.
2. Use the current official Library skill and helper for the resolved reference. Preserve the complete transfer object. Do not substitute raw download commands, invented URLs, or another downloader after an unexplained failure.
3. Record the exact error and whether an HTTP status or explicit denial exists. Check available tools and CA certificates before proposing installation. Stop unchanged retries.
4. Inspect only the returned URL's hostname for each attachment; never retain the signed URL, query string, headers or tokens. Region/hostname can differ between attachments. Compare that exact hostname with the consumer's actual network policy, not merely the environment editor's saved configuration. Do not infer the next hostname or pre-authorize a wildcard.
5. Any necessary network-policy expansion requires explicit owner approval. Request only the verified hostname; do not add broad wildcards or disable restrictions. Distinguish a saved draft from a successfully published environment version.
6. Do not assume publication updates an already running consumer. Verify its actual policy. If unchanged, stop retries there; use an appropriately approved consumer of the published version and verify its policy before one supported transfer.
7. Check the resulting file's exact size and SHA256 in the consuming environment before downstream use. Preserve completed transfer/build/test evidence; do not rerun unrelated successful work.

## Preservation boundary and next step

Keep signed URLs, tokens, database dumps and private database contents out of GitHub and reports. Retain only sanitized identifiers, errors, approved hostname, version, size and hash. This runbook is included under the owner's explicit overnight checkpoint publication authorization; it does not authorize network changes, another transfer or database execution. Private Library attachment identifiers are omitted from this published copy; filenames, public artifact identity and hashes identify the required bytes.
