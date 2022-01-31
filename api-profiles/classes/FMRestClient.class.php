<?php
# Class cover general Flowmon RestAPI operations

/**
 * This class provide all required abstraction to work with API.
 * It is ment to be used with Flowmon RestAPI available at version 9.02.
 * @copyright Copyright 2019 Flowmon Networks - support@flowmon.com
 * @author Jiri Knapek - jiri.knapek@flowmon.com
 * @version 1.1
 */


class FMRestClient {
    protected $host;
    protected $client_id;
    protected $username;
    protected $password;
    protected $token;

    public function __construct($host, $client_id, $username, $password) {
        $this->host = $host;
        $this->client_id = $client_id;
        $this->username = $username;
        $this->password = $password;
        $this->token = '';
        $this->login();
    }

    /**
     * Login to the APi to get authentication token
     */
     private function login() {
         $tokenUrl = 'https://' . $this->host . '/resources/oauth/token';

         $data = array(
            "grant_type=password",
            "client_id={$this->client_id}",
            "username={$this->username}",
            "password={$this->password}"
            );

        $paramsCount = count($data);
        $request = join('&', $data);

        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $tokenUrl);
        curl_setopt($ch, CURLOPT_POST, $paramsCount);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

        $result = curl_exec($ch);

        $error = "";
        
        if($result===false) {
            $error = curl_error($ch);
            throw new Exception("Could not authenticate: $error");
        }

        curl_close($ch);

        $this->token = json_decode($result);
     }

     /**
      * General GET method
      * @param $url - required - URL for the request
      * @return json with returned data
      */
    protected function get($url, $data = NULL) {
         if ( empty($this->token) ) {
            throw new Exception("Authentication token does not exists!");
         }

         $dataString = json_encode($data['values']);

         if ( empty($data) ) {
             $url = 'https://' . $this->host . $url;
         } else {
             $url = 'https://' . $this->host . $url .'?' . $data['entity'] . '=' . $dataString;
         }

         $ch = curl_init();

         curl_setopt($ch, CURLOPT_URL, $url);
         curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "GET");
         curl_setopt($ch, CURLOPT_VERBOSE, true);
         curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
         curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
         curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
         curl_setopt($ch, CURLOPT_HTTPHEADER, array(
             "Authorization: Bearer {$this->token->access_token}",
             'Content-Type: application/json',
         ));

         $result = curl_exec($ch);
 
         $error = "";
         
         if($result===false) {
             $error = curl_error($ch);
             throw new Exception("Error while GET $url: $error");
         }

         return $result;
     }
     /**
      * Function for general post
      * @param $url - required - URL for the request
      * @return json with returned data
      */
    protected function post($url, $data = NULL) {
         if ( empty($this->token) ) {
            throw new Exception("Authentication token does not exists!");
         }

         $dataString = json_encode($data['values']);

         if ( empty($data) ) {
             $url = 'https://' . $this->host . $url;
         } else {
             $url = 'https://' . $this->host . $url . '?' . $data['entity'] . '=' . $dataString;
         }

         $ch = curl_init();

         curl_setopt($ch, CURLOPT_URL, $url);
         curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
         curl_setopt($ch, CURLOPT_VERBOSE, true);
         curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
         curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
         curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
         curl_setopt($ch, CURLOPT_HTTPHEADER, array(
             "Authorization: Bearer {$this->token->access_token}",
             'Content-Type: application/json',
         ));

         $result = curl_exec($ch);
 
         $error = "";
         
         if($result===false) {
             $error = curl_error($ch);
             throw new Exception("Error while POST $url: $error");
         }

         return $result;
     }

     /**
      * Function taking care to send a DELETE request
      * @param $url - required - URL of the reques
      */
     protected function delete($url, $data = NULL) {     
        if ( empty($this->token) ) {
            throw new Exception("Authentication token does not exists!");
         }

        $url = 'https://' . $this->host . $url . $data;
         
         $ch = curl_init();

         curl_setopt($ch, CURLOPT_URL, $url);
         curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE");
         curl_setopt($ch, CURLOPT_VERBOSE, true);
         curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
         curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
         curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
         curl_setopt($ch, CURLOPT_HTTPHEADER, array(
             "Authorization: Bearer {$this->token->access_token}",
             'Content-Type: application/json',
         ));

         $result = curl_exec($ch);
 
         $error = "";
         
         if($result===false) {
             $error = curl_error($ch);
             throw new Exception("Error while DELETE $url: $error");
         }

         return curl_getinfo($result);
     }

    /**
     * Function for modification of specific filed (PUT)
     * @param $url - required - URL for the request
     * @param $data -require - data used for modification
     */
    protected function modify($url, $data) { 
        if ( empty($this->token) ) {
            throw new Exception("Authentication token does not exists!");
         }

        $url = 'https://' . $this->host . $url;
        
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "PUT");
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json','Content-Length: ' . strlen($data)));
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_VERBOSE, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            "Authorization: Bearer {$this->token->access_token}",
            'Content-Type: application/json',
        ));

        $result = curl_exec($ch);
 
        $error = "";
        
        if($result===false) {
            $error = curl_error($ch);
            throw new Exception("Error while PUT $url: $error");
        }

        return $result;
    }
 }
?>