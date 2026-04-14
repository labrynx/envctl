# Distribution

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    This page covers the release artifacts `envctl` publishes and the integrity signals around them.
    Use it when you need packaging, checksum, SBOM, or attestation details.
  </p>
</div>

This page describes what `envctl` publishes as release artifacts and what integrity signals are expected around them.

## Release artifacts

Tagged releases currently publish:

* one wheel artifact
* one source distribution artifact
* one CycloneDX SBOM for the built wheel
* one `SHA256SUMS` manifest covering the published artifacts and SBOM

The artifact set is intentionally small and inspectable.

## Integrity signals

The current release pipeline provides several observable checks:

* build happens in CI from the tagged source
* the built wheel is smoke-tested before publication
* a `SHA256SUMS` manifest is generated for published artifacts
* a CycloneDX SBOM is generated for the built wheel
* GitHub artifact attestations are generated for release artifacts in CI

That gives consumers both a simple offline check (`SHA256SUMS`) and a stronger provenance signal through GitHub attestations.

## Local packaging workflow

For local validation, the repository exposes these targets:

```bash
make build-package
make check-package
make dist-checksums
make dist-sbom
```

Run them from the project environment:

```bash
make build-package dist-checksums dist-sbom check-package
```

## Verifying checksums

On Unix-like systems:

```bash
cd dist
sha256sum -c SHA256SUMS
```

On Windows (PowerShell):

```powershell
Set-Location dist
$failed = $false
Get-Content SHA256SUMS | ForEach-Object {
  if ($_ -match '^([A-Fa-f0-9]{64})\s+\*?(.+)$') {
    $expected = $matches[1].ToLower()
    $file = $matches[2]
    $actual = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLower()
    if ($actual -ne $expected) {
      Write-Error "Checksum mismatch: $file"
      $failed = $true
    }
  }
}
if ($failed) { exit 1 } else { Write-Host "All checksums match." }
```

## Verifying attestations

GitHub provenance attestations can be verified with the GitHub CLI:

```bash
gh attestation verify dist/envctl-<version>-py3-none-any.whl -R labrynx/envctl
gh attestation verify dist/envctl-<version>.tar.gz -R labrynx/envctl
```

Use the GitHub release page or workflow run details as the source of truth for the attested artifacts that correspond to a published release.

## Scope and limits

The current release integrity model is stronger than raw file upload, but it is still intentionally lightweight:

* it does not yet sign artifacts outside GitHub's attestation flow
* it does not yet publish a wider multi-artifact SBOM set
* it assumes consumers trust GitHub's attestation and release surfaces for verification

That is good enough for the current phase of the project, but it should still be treated as incremental hardening rather than the final state.

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Security reference

Connect release artifact integrity back to the broader security model.

[Open security reference](security.md)
</div>

<div class="envctl-doc-card" markdown>
### Roadmap

See how distribution hardening fits into current product direction.

[Open roadmap](roadmap.md)
</div>

<div class="envctl-doc-card" markdown>
### Migration and compatibility

Open this when release or tooling policy is being interpreted through legacy constraints.

[Open compatibility guide](../internals/compatibility.md)
</div>

</div>
