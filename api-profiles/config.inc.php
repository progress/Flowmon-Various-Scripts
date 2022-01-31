<?php
define ( 'CLIENT_ROOT', '/var/www/shtml/api-profiles/' );

################################################################################
# Connection configuration for Flowmon RestAPI client
################################################################################

# Configuration access of first Flowmon
$flowmon1 = array( 'host' => '192.168.47.10',
                   'username' => 'admin',
                   'password' => 'admin',
                   'client_id' => 'invea-tech');

 # Configuration of second Flowmon appliance                  
$flowmon2 = array( 'host' => '192.168.47.11',
                    'username' => 'admin',
                    'password' => 'admin',
                    'client_id' => 'invea-tech');
?>