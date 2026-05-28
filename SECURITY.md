# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| Latest (`main`) | ✅ Yes |
| Older branches | ❌ No |

---

## Reporting a vulnerability

If you discover a security vulnerability, **please do not open a public Issue**.

Instead, report it privately by emailing:

📧 **csbisht1@gmail.com**

Please include:
- A description of the vulnerability
- Steps to reproduce it
- The potential impact

I will acknowledge your report within **72 hours** and aim to release a fix within **14 days** depending on severity.

---

## Scope

This is a local command-line tool that processes PDF files on your own machine.  
It does not connect to the internet, collect data, or run as a server.

Common areas to consider:
- Malformed or malicious PDF files causing unexpected behaviour
- Path traversal issues in file input/output handling
