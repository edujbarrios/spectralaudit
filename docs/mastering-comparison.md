# MasteringDiff: comparing premaster and master

`compare_masters(original, master)` measures sample offset, linear gain,
residual RMS and frequency-band changes after alignment. It does not infer
which plugin or process caused a change. See `docs/algorithms.md`.

For a multi-stage sequence, supply an insertion-ordered `dict` to
`audit_pipeline`, which compares consecutive versions.

Significant pitch shifts, time stretching, different arrangements,
nonlinear compression and sample rate conversion can confound the alignment.
Always inspect the signal pair independently if alignment quality is poor.
