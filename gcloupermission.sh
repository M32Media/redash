sudo groupadd gcloudconf;
sudo usermod -a -G gcloudconf dev;
sudo usermod -a -G gcloudconf redash;
sudo chgrp gcloudconf /home/dev/.config/;
sudo chmod 777 /home/dev/.config/;
