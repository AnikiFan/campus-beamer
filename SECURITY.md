# Security policy

## Supported versions

Security fixes are prepared for the latest release and the `main` branch. Older
releases may continue to work, but they are not guaranteed to receive security
updates; please reproduce the issue on a current checkout before reporting it.

## Reporting a vulnerability

Please do not open a public issue for an unpatched vulnerability. Use GitHub's
**private vulnerability reporting** for
[AnikiFan/campus-beamer](https://github.com/AnikiFan/campus-beamer/security/advisories/new)
when it is available. If that form is unavailable, email
[xiaofan140@gmail.com](mailto:xiaofan140@gmail.com) with the subject
`Campus Beamer security report`.

Include the affected version or commit, the smallest reproduction you can
share, the expected and actual behavior, and any relevant command output. Remove
personal presentations, credentials, private paths and other sensitive material
before sending files or logs. If a public asset or dependency is involved,
include its name and the relevant URL or checksum.

We will acknowledge a report within seven days when possible, keep the reporter
updated while we investigate, and coordinate a fix and disclosure timeline with
the reporter. Please allow time for a fix before publishing details or an
exploit.

## Scope

This policy covers the template source, build tools, GitHub Actions workflows,
release automation and distributed example assets. Reports about third-party
TeX packages, operating systems, GitHub or PowerPoint should also be reported to
their respective maintainers; include the upstream issue link when it affects
this project.
