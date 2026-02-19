# homepage-nordvpn-widget

A small widget and server to expose NordVPN connection status for use with [homepage](https://gethomepage.dev/).

## Quick install

Run the following command in the LXC container you're using as your NordVPN gateway to install the API:

```bash
curl -fsSL https://raw.githubusercontent.com/Skribb11es/homepage-nordvpn-widget/main/install.sh | bash
```

If you want to use a custom token for authentication, set the `NORD_STATUS_TOKEN` environment variable in the nord-status-server.env file created in the installation process.

```bash
nano /etc/nord-status-server.env
```

## Config

There are two optional environment variables you can set in the `nord-status-server.env` file to configure the server:

### `NORDVPN_STATUS_TOKEN` - Used to secure the API with a set token. If unspecified, the API does not require authentication to be utilized. Default value is `None` (no authentication).

```bash
NORDVPN_STATUS_TOKEN=supersecretpasswordhere
```

### `NORDVPN_STATUS_IFACE` - The network interface to check for the LAN IP address of the VPN container otherwise the API will not be reachable locally. Default value is `eth0`.

```bash
NORDVPN_STATUS_IFACE=tun0
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