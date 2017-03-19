# firewall_byPass_python_script
A script that utilises security holes in authentication mechanism for authenticating users in a LAN .

Now lets understand how we bypassed firewall.  
To get this we have to understand how firewall works . So basically ,**when a user logins into firewall , he will be assigned some session time for which , he have access to internet . When that fixed session time expires your firewall will ask you again for login .**  
Usually every firewall binds that session time with the IP address of the user who logged in correctly .  
**What happens if that user turns off his device or detaches from that  network . Then that  IP address might have some session time left with it . In short we just searched for how many users have left the network  by looking at those free IP addresses . And we statically assign that IP address to our network card so that we can utilize that session time for our use . And for firewall we are still that guy who logged in .**  
#### Note:-  
when we assigned a static IP address to our network interface then we don't need to query the DHCP server so, DHCP server will never get to know about such an IP address .( an IP address which was assigned using DHCP initially from the IP address pool but later used as static IP ).  
So it may happen that the same user connects back to network and try to use that IP address again which it previously had . In this case either he or we couldn't properly access the internet.  
But you don't have to worry because if this happened by any chance then , you still have many of free IPs left with you . And you will be able to access  the internet again .  
