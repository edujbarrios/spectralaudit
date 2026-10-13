# Scientific references and implementation boundaries

The algorithms in SpectralAudit are original Python implementations of conventional
DSP ideas. A detected artifact is not proof of AI generation. No code or weights
are taken from the Deezer research implementation.

1. Afchar, D., Meseguer-Brocal, G., Akesbi, K., & Hennequin, R. (2025).
   **A Fourier Explanation of AI-music Artifacts**. Proceedings of the 26th
   International Society for Music Information Retrieval Conference, 739–746.
   https://doi.org/10.5281/zenodo.17811475 . Motivates investigating periodic
   spectral structure, but the present heuristic is not their published detector.
2. Cros Vila, L., Sturm, B. L. T., Casini, L., & Dalmazzo, D. (2025).
   **The AI Music Arms Race: On the Detection of AI-Generated Music**.
   *Transactions of the International Society for Music Information Retrieval*, 8(1).
   https://doi.org/10.5334/tismir.254 . Motivates explicit confounders and
   robustness warnings.
3. Welch, P. D. (1967). **The Use of Fast Fourier Transform for the Estimation
   of Power Spectra: A Method Based on Time Averaging Over Short, Modified
   Periodograms**. *IEEE Transactions on Audio and Electroacoustics*, 15(2),
   70–73. https://doi.org/10.1109/TAU.1967.1161901 . Basis of Welch PSD.
4. Harris, F. J. (1978). **On the use of windows for harmonic analysis with the
   discrete Fourier transform**. *Proceedings of the IEEE*, 66(1), 51–83.
   https://doi.org/10.1109/PROC.1978.10837 . Basis for Hann windowing.

## Licensing / research provenance

Deezer's publication-related repository is CC BY-NC 4.0 and reports patent
applications: https://github.com/deezer/ismir25-ai-music-detector . We have
not copied its implementation. Independent implementation does not automatically
resolve patent concerns; obtain professional review before relying on this
software commercially for provenance detection.

The peak detection and cutoff estimation included here are exploratory
measurements without empirical provenance calibration. They must not be reported
as reproducing the published detection rates.
