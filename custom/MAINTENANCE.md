# Maintaining the private notification firmware

Repository: https://github.com/sintezcs/PebbleOS-notification-count.
Maintained branch: `codex/notification-count`. Source base and ABI are pinned in
`custom/state.json`. The target is Time 2 PVT (`obelix_pvt`, emery); build both slots.

The private API returns the count of retained watch notifications, including read
records and excluding deleted records. It exposes no content. The paired LCD221
source is in `custom/watchface`. The user reports this behavior working on a retail
Time 2; new release builds require their own verification and physical check.

## Release checks

Check all official published, non-prerelease releases with both PVT slot assets.
Compare semantic versions against `base_tag`; do not use GitHub's global `latest`
endpoint alone. Older branch backports can be published later than the current
release. Never downgrade. Initially the highest eligible base is v4.38.4.

For a newer release, preserve a known-good branch and create an isolated candidate.
Fetch only needed source/submodules. Rebase the notification API and custom tooling
onto that exact tag, resolving changed source paths and code deliberately. Update
state's base tag/commit and allocate the private export revision after upstream's
last revision. Choose a private SDK minor above the upstream minor and any already
reserved minor (0x6b was reserved by main when this fork started). Do not blindly
reuse revision 110 or SDK 0x6c when upstream changes. Verify the official symbol
prefix is unchanged and the count API is appended, not inserted in existing ABI.

If upstream has an equivalent official API, check retained/read/deleted semantics
and tests before removing the private implementation. Fail closed on incompatible
or ambiguous API changes; report the conflict rather than publishing a broken build.

## CI and promotion

Push the candidate to `codex/notification-count` only after integration review,
or use a candidate PR targeting that branch so the existing verified head remains
available. Run `Custom notification firmware` and inspect actual completed jobs,
unit results and artifacts. The workflow compiles both PVT slots and a matching PBW,
checks the SDK contract, and verifies archive payload CRCs and boot priorities.
Never call a dispatch or YAML edit a successful build. Never replace the known-good
release when tests or package validation fail. Record failure fingerprints to avoid
repeating unchanged failures or notifications.

Only after CI passes, advance the maintained branch and create a custom release
with the two PBZs, matching PBW, verification reports and SHA-256 sums. Source and
build commit must be identifiable. Notify the user with direct artifact links and
installation steps. Do not flash a watch automatically. A user must identify its
current slot anew; install the opposite slot. Select a stock/system face before
changing firmware, then install the PBW compiled by that same build. A private API
index can move when upstream adds exports, so an old private PBW is not guaranteed
compatible with a new custom firmware even if the SDK minor increases.

## Packaging and recovery

Do not ship development-band boot priority (0x80): it outranks all stock releases.
`custom/scripts/package_firmware.py` changes only header bytes 8-15 to release-band
priority for the base version plus package timestamp, checks the body CRC, and
recomputes the full manifest CRC. Future higher stock versions can outrank it.
Returning to an older original stock image may require PRF/recovery to invalidate
normal slots. The version tag remains visibly custom; do not impersonate stock
firmware to suppress Android alerts.

Daily Codex checks run at 10:00 Europe/Moscow. Stay quiet if unchanged. Notify only
for a verified new downloadable build, a new failure or required user input.
The phone's Firmware Updates notification category can be muted independently.

No real notifications, user screenshots, serial numbers, IPs, secrets or machine
home-directory paths belong in commits or release files. Existing upstream
contribution policy applies separately to any PR proposed to Core Devices; this
personal fork does not assert that the user has manually reviewed generated code
for upstream submission.
