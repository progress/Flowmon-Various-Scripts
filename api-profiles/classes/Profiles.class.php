<?php
# Class to work with API on Flowmon Profiles

/**
 * This class provide methods required for this script to work with client
 * It is ment to be used with Flowmon RestAPI available at version 9.02.
 * @copyright Copyright 2019 Flowmon Networks - support@flowmon.com
 * @author Jiri Knapek - jiri.knapek@flowmon.com
 * @uses FMRestClient.php
 * @version 1.1
 */

 class Profiles extends FMRestClient {
     public function __construct($host, $client_id, $username, $password) {
         parent::__construct($host, $client_id, $username, $password);
     }

     public function getAllProfiles() {
        $url = '/rest/fmc/getprofiles';

        return $this->post($url);
     }

     public function deleteProfile($id) {
         $ids = '?id='.$id;
         $url = '/rest/fmc/profiles/id';

         return $this->delete($url, $ids);
     }

     public function changeProfile($data) {
         $url = '/rest/fmc/profiles';

         return $this->modify($url, $data);
     }

     public function getProfile($id) {
         $url = '/rest/fmc/profiles/id?id='.urlencode($id);

         return $this->get($url);
     }
 }
?>