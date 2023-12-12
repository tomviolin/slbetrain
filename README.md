# FISH IDENTIFIER TRAINING

## THIS SOFTWARE IS NOT INTENDED FOR DEPLOYMENT ON A PUBLIC-FACING SERVER.


This software is intended only for use on a local machine or a local private subnet.

No security has been enabled and this code could be easily hacked.

If you like the algorithms, feel free to fork this (and give credit per the MIT license) if
you want to make this more secure.


# INSTALLATION

There isn't an official install procedure yet. I just made a copy of my site file from `/etc/apache2/sites-enabled` [really hyperlinked from `.../sites-avaiable` but who's counting] and here we are.

I did this on Linux Mint 21.2 "Victoria" which is based on Ubuntu 22.04 "Jammy" so if you are on one of those, or something reasonably close, this should work.

Requirements:

* recent linux distro with Apache2 installed
* Python 3.recent (need `f"... "` formatting)

Once Apache 2 and Python 3.recent are installed:

* Edit the file `apache_vhost_example.conf`. 
You'll need to replace `myserver.example.com` with your web server address
and `/home/myuser/` with wherever you want this to live on your machine.
#
#  You'll also need to enable the cgid module. This command will work on most modern distros
#  with Apache2 installed.
#
#  $ sudo a2enmod cgid
#


# data layout

