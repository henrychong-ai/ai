# TODO — typescript-version-upgrade

Last reviewed: 2026-09-28.

## Open
- **Node security floors:** the skill uses the live lookup in `references/node/migration-overview.md`. Snapshot on 2026-09-28: last security releases 24.18.1 and 22.23.2 (2026-07-28). Re-check the snapshot line on each review.
- **Node 24 → 26 guide:** written before Node 26 LTS (2026-10-28) and before nodejs.org published a v24-to-v26 migration page. After LTS promotion, re-read the 26.x changelog and the userland-migrations catalogue for new codemods and update `references/node/node-24-to-26.md`.
- **TypeScript 7.1:** when 7.1 ships the compiler API, re-check typescript-eslint, ts-jest and framework support and revise `references/typescript/typescript-6-to-7.md` (the policy change itself belongs in your TypeScript standards).
- **Next.js with TypeScript 7:** unverified whether `next build`'s type-check step works with only TS 7 installed. Test on one Next.js 16 repo before recommending the side-by-side lane there.
- **ES2026 target:** neither TS 6.0 nor 7.0 accepts `--target es2026` (checked 2026-09-28). Add a row to the Node mapping when a compiler release supports it.

## Unverified
- Node 22 → 24 behaviour-change list (fetch compliance, AbortSignal validation, stream error propagation) is summarised from the nodejs.org migration page headings, not from individual changelog entries.
- ES2026 feature list in `references/ecmascript/es-version-features.md` is from secondary coverage of the Ecma approval; confirm against the published ECMA-262 17th edition.

## Done (2026-09-28)
- Restructured: merged legacy Node guides and the three React guides; added TypeScript 5→6 and 6→7 and Node 24→26 guides; replaced the browser matrix and Node-ES mapping with procedures; Next.js file is now a per-major index of official guides and codemods.
