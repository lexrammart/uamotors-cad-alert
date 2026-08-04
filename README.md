<p align="center">
  <a href="https://uamotors.github.io/">
    <img src="assets/1.completo.svg" width="400" alt="UAMOTORS Logo">
  </a>
</p>

# UAMOTORS CAD Alert Monitor

> **A silent, background monitor for SolidWorks assemblies.**
>
> **[Visit the UAMOTORS Team Website](https://uamotors.github.io/)**

This application monitors SolidWorks assembly files within a local or cloud-synced directory and sends real-time status updates to a Discord webhook.

## Core Features

### Dynamic Version Tracking

The system relies on detecting temporary lock files created by SolidWorks when an assembly is opened. It uses regular expressions to match files independent of their version number. The monitor operates recursively on the target directory, ensuring lock files are detected regardless of their exact path inside the project folder.

### Network Resiliency

The application includes a background worker thread for Discord integration. This ensures that webhooks are queued and retried automatically if a rate limit or a temporary network failure occurs, preventing false status reports.

## Installation & Deployment

### Automatic Setup

Installation is handled automatically. When the executable is run, it copies itself to the local AppData directory and creates a Startup shortcut. This ensures the monitor runs silently in the background every time the computer boots. A single-instance lock prevents multiple monitors from running simultaneously on the same machine.

### Building from Source

Dependencies are defined in the `requirements.txt` file. A GitHub Actions workflow is provided to automatically package the application into a deployment ZIP. This archive includes the compiled executable and an installation batch script (.bat) designed to bypass execution restrictions and handle the deployment process seamlessly.
