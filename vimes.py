import subprocess
import dns
import dns.query
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image
import time

def DotTest(serverip):
    """runs test to see if supplies IP supports DoT, returns True or False."""
    r = dns.message.make_query('google.com', dns.rdatatype.AAAA)
    try:
        response = dns.query.tls(r, serverip)
        response = response.to_text().split()
        return True
    except TimeoutError:
        return False
    except:
        return False

def StartCoredns():
    """Starts th CoreDNS binary with the Corefile."""
    command = """.\\coredns.exe -conf .\\Corefile"""
    script = subprocess.Popen(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe", command], stdout=subprocess.PIPE)
    out, err = script.communicate()
    return out

def DotTemplateRewrite(config_location, ip1):
    """Rewrites the Corefile template with supplied IP address."""
    with open(config_location + 'Corefile.template', 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('---IP1---', 'tls://' + ip1)
    filedata = filedata.replace('---IP2---', '')  # FIX THIS
    with open(config_location + 'Corefile', 'w') as file:
        file.write(filedata)

def WindowsGetDnsServer():
    """Uses Powershell command to retrieve DNS servers from active network connections and returns an array of results."""
    command = """Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} |
                        select-object -First 1 | Get-DnsClientServerAddress |
                        Select-Object -ExpandProperty ServerAddresses"""
    script = subprocess.Popen(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe", command], stdout=subprocess.PIPE)
    out, err = script.communicate()
    out = out.decode('UTF-8')
    servers = out.split()
    return servers

def ResetDnsToDefault():
    """Removed local override of DNS servers."""
    command = 'Set-DnsClientServerAddress -InterfaceAlias Wi-Fi -ResetServerAddresses'
    script = subprocess.Popen(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe", command], stdout=subprocess.PIPE)
    out, err = script.communicate()

def SetDnsServerToLocal():
    """Sets system DNS server to 127.0.0.1."""
    command = 'Set-DnsClientServerAddress -InterfaceAlias Wi-Fi -ServerAddresses ("127.0.0.1")'
    script = subprocess.Popen(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe", command], stdout=subprocess.PIPE)
    out, err = script.communicate()

def action():
    pass
 
def exit_prg():
    """exits the program."""
    global icon
    global quit
    quit = True
    icon.stop()

def StartGreen():
    """Chagnes systray icon to green to indicate proxied status."""
    global proxied
    global icon
    global quit
    menu = (item('Help', action),
        item('Stop Proxying Traffic', StopProxyTraffic),
        item('Quit', exit_prg)
        )
    image = Image.open("green.png")
    icon = pystray.Icon("", image, "Vimes", menu)
    icon.run()

def StartYellow():
    """Changes systray icon to yellow to indicate proxy available but not enabled."""
    global proxied
    global icon
    global quit
    menu = (item('Help', action),
        item('Proxy Traffic', ProxyTraffic),
        item('Quit', exit_prg)
        )
    image = Image.open("yellow.png")
    icon = pystray.Icon("", image, "Vimes", menu)
    icon.run()

def StartRed():
    """Changes systray icon to red to indicate no upgrade available."""
    global proxied
    global icon
    global quit
    menu = (item('Help', action),
        item('Quit', exit_prg)
        )
    image = Image.open("red.png")
    icon = pystray.Icon("", image, "Vimes", menu)
    icon.run()

def StopProxyTraffic():
    """stops proxying traffic."""
    global proxied
    proxied = False
    ResetDnsToDefault()

def ProxyTraffic():
    """starts proxying traffic."""
    global proxied
    t = threading.Thread(target=StartCoredns)
    t.start()
    print('Pointing System DNS to proxy')
    SetDnsServerToLocal()
    print('DNS Redirected')
    proxied = True

def main():
    """ Main entry point of the app """
    global icon
    global proxied
    global quit
    proxied = ''
    while True:
        if quit == True:
            break
        else:
            pass
        if proxied is True:
            print('proxied set to True')
            green = threading.Thread(target=StartGreen)
            try:
                icon
            except NameError:
                pass
            else:
                icon.stop()
            green.start()
        print("System DNS Servers:")
        servers = WindowsGetDnsServer()
        print(servers)
        if servers[0] == '127.0.0.1':
            green = threading.Thread(target=StartGreen)
            try:
                icon
            except NameError:
                green.start()
            else:
                pass
        else:
            print("\nDoT Test against first server: " + servers[0])
            dot_support = DotTest(servers[0])
            if dot_support is True:
                print('DoT Supported, changing icon')
                x = threading.Thread(target=StartYellow)
                try:
                    icon
                except NameError:
                    pass
                else:
                    icon.stop()
                x.start()
                DotTemplateRewrite('.\\', servers[0])  # TODO fix config location
            else:
                x = threading.Thread(target=StartRed)
                try:
                    icon
                except NameError:
                    pass
                else:
                    icon.stop()
                x.start()
                print('no DoT Support')
            time.sleep(5)

if __name__ == "__main__":
    main()