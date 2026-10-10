# MAP-WIRE-01 — MapChanged.MapNumber

2026-10-10; LOW-cost, read-only source inspection. Routing: WORK, bounded cross-system contract review.

## Result: UNKNOWN for the pinned runtime; declared-width mismatch identified

The OpenMU `MapChanged` packet declares a **16-bit big-endian MapNumber**, whereas the pinned native receiver declares **BYTE Map**. This proves a source-level representation difference, not a broken S6 route or a current gameplay blocker. The exact compiled receive-struct offsets and the map-number domain of the saved baseline were not independently established in this pass. No fix is proposed from this evidence alone.

Only this one field was reviewed. Packet framing, flags, coordinates and bridge code were read solely to understand its dependencies; no second mechanic was audited.

## Pins and deduplication

- Client binary source: `8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5` (existing artifact 11567737809).
- Server: `MUnique/OpenMU@d067b3c11c23c3145de6e2c76201ab9a93b267c8`, with the previously recorded Money patch. This review did not inspect or replace runtime bytes.
- Data: `data-4b0ab29c58b27fc4`, tree `77f7830f542d106fc519c8821832d49a3dd8ae3a`, existing socket-metadata overlay. No Data binary was downloaded or decoded.
- Read [AGENTS](https://github.com/ncuxonat7-oss/MuMain/blob/177abb85bc65c41709e16894340b698240c98073/AGENTS.md), [current state](https://github.com/ncuxonat7-oss/MuMain/blob/177abb85bc65c41709e16894340b698240c98073/docs/current-state.md), [strategy index](https://github.com/ncuxonat7-oss/MuMain/blob/177abb85bc65c41709e16894340b698240c98073/docs/s6-strategy-and-mechanics-index.md), navigation, relevant baseline map/warp rows and [S6 baseline diff](https://github.com/ncuxonat7-oss/MuMain/blob/177abb85bc65c41709e16894340b698240c98073/docs/s6-baseline-diff.md).
- Existing evidence already covers map/resource aliases, partial configuration projection, and Lorencia↔Noria runtime warp with Zen debit. None was repeated. The inspected index/evidence does not close this receive-field width/layout contract.

## Exact dependency chain

1. **Server sender:** [MapChangePlugIn.cs](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/GameServer/RemoteView/World/MapChangePlugIn.cs), `SendMessageAsync`: reads `SelectedCharacter.CurrentMap.Number.ToUnsigned()` and passes it to `SendMapChangedAsync`. [TeleportPlugIn.cs](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/GameServer/RemoteView/World/TeleportPlugIn.cs) uses the same packet with `isMapChange=false`.
2. **Wire declaration:** [ServerToClientPackets.xml, lines 2746–2784](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Network/Packets/ServerToClient/ServerToClientPackets.xml#L2746-L2784): C3 header with subcode, code `1C`, subcode `0F`, length 15. Boolean IsMapChange at offset 4; **ShortBigEndian MapNumber at offsets 5–6**; X/Y/rotation at 7/8/9. [Generated protocol documentation](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/docs/Packets/C3-1C-0F-MapChanged_by-server.md) agrees.
3. **Client transport dependencies:** [ConnectionWrapper.cs](https://github.com/ncuxonat7-oss/MuMain/blob/8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/ClientLibrary/ConnectionWrapper.cs), `OnPacketReceivedAsync`, copies received bytes and invokes the native callback; [Connection.cpp, lines 317–325](https://github.com/ncuxonat7-oss/MuMain/blob/8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/src/source/Dotnet/Connection.cpp#L317-L325) forwards the same data pointer. No MapNumber conversion exists in these inspected bridge methods.
4. **Client receiver layout declaration:** [WSclient.h, lines 921–928](https://github.com/ncuxonat7-oss/MuMain/blob/8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/src/source/Network/Server/WSclient.h#L921-L928): `PBMSG_HEADER Header; WORD Flag; BYTE Map; BYTE PositionX; BYTE PositionY; BYTE Angle;`. PBMSG_HEADER consists of three BYTE fields (lines 127–132). This struct has no local packing directive; the preceding local push(1) is popped at line 786. Root and src CMake files contain no observed pack-struct or /Zp setting. This is not a complete transitive-header or binary ABI proof.
5. **Client use:** [WSclient.cpp, lines 2183–2238](https://github.com/ncuxonat7-oss/MuMain/blob/8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/src/source/Network/Server/WSclient.cpp#L2183-L2238) directly casts the buffer to that struct and, on its nonzero Flag branch, assigns `gMapManager.WorldActive = Data->Map` before LoadWorld. Dispatch is case `0x1C` at lines 13899–13906. There is no 16-bit MapNumber decode in this receiver.

## Interpretation and limits

- **Conditional layout reasoning, not measured ABI:** if WORD has normal 2-byte alignment and BYTE is 1 byte, Header occupies 0–2, padding occupies 3, Flag occupies 4–5, Map is at 6, and X/Y/angle are at 7/8/9. On that layout, Map reads the server's low MapNumber byte. Values 0–255 are preserved; e.g. hypothetical wire map 256 would become 0. That hypothetical is outside any established failing baseline scenario.
- The same layout makes the server's high MapNumber byte overlap the receiver's Flag. Do not infer actual flag behavior without confirming layout and the selected map; it is a dependency warning, not a second verified defect.
- Existing [client-resource-check.json](https://github.com/ncuxonat7-oss/MuMain/blob/177abb85bc65c41709e16894340b698240c98073/docs/client-resource-check.json) records 73 map definitions / 68 distinct numbers, but does not enumerate all numbers or establish the maximum. The owner-scoped source projection records 66 maps. These different scoped counts do not prove all baseline IDs fit one byte.
- [tools/gen_wire_sizes.py](https://github.com/ncuxonat7-oss/MuMain/blob/8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/tools/gen_wire_sizes.py) covers only CharacterCreationSuccessful, CharacterInformationExtended and RespawnAfterDeathExtended. It does not validate this MapChanged layout or offsets. Prior 423 test PASS is not promoted to this field proof.
- STATIC: declaration discrepancy established; compiled byte mapping conditional. LOCAL test: NOT_RUN. NATIVE/runtime: NOT_RUN. No known teleport bug report is linked. No new readiness credit or blocker; 65.5/model1.1/MEDIUM unchanged.

## Next cheapest step / stop

When a concrete teleport report arrives, record origin/destination, requested action, expected/actual map and X:Y, build session and timestamp. Reuse the preserved baseline export to identify that one destination number, then inspect existing receive evidence for C3/1C/0F if available. Confirm actual `offsetof(Map)`/`offsetof(Flag)` only through existing compile evidence or a separately authorized tiny layout check; do not rebuild the client or replay known routes merely to resolve this note. If the destination is <=255 and the expected offset is verified, this width difference alone does not explain a failure.

Stopped here: no runtime, builds, code/config changes, binary downloads, environment launch, broader map scan, or GitHub publication.
