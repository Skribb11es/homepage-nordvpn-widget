# homepage-nordvpn-widget

A small widget and server to expose NordVPN connection status for use on a homepage.

## Quick install

Run this single command on a Linux or macOS machine (requires `bash` and `curl`):

```bash
curl -fsSL https://raw.githubusercontent.com/Skribb11es/homepage-nordvpn-widget/main/install.sh | bash
```

If you want to use a custom token for authentication, set the `NORD_STATUS_TOKEN` environment variable in the nord-status-server.env file created in the installation process.

```bash
nano /etc/nord-status-server.env
```

Simply put the following line in the file, replacing `supersecretpasswordhere` with a secure token of your choice:

```bash
NORDVPN_STATUS_TOKEN=supersecretpasswordhere
```



## Homepage integration

Using the [Custom API](https://gethomepage.dev/widgets/services/customapi/) support of [Homepage](https://gethomepage.dev/) you can pretty easily add this api to your homepage as a widget with a similar `services.yaml` configuration to the one provided below.

```yaml
- VPN:
    - NordVPN:
        icon: nordvpn.png
        href: http://VPN_CONTAINER_IP:8787/status
        description: VPN connection status
        widget:
          type: customapi
          url: http://VPN_CONTAINER_IP:8787/status?token=supersecretpasswordhere
          refreshInterval: 10
          method: GET
          mappings:
            - field: connected
              label: Connected
            - field: country
              label: Country
            - field: city
              label: City
            - field: hostname
              label: Host
            - field: technology
              label: Tech
            - field: protocol
              label: Proto
            - field: public_ip_check
              label: Public IP
            - field: uptime
              label: Uptime

```