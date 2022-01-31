<?php
# Main class

// error reporting
error_reporting(E_ALL |E_STRICT);
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);

require_once 'config.inc.php';

function my_autoloader($class) {
    include 'classes/' . $class . '.class.php';
}

function compare_profiles ($profile1, $profile2) {  
    # get profiles from one device
    $fmprofiles1 = json_decode($profile1->getAllProfiles());

    # get profiles from second device
    $fmprofiles2 = json_decode($profile2->getAllProfiles());

    $return = Profile::compare( $fmprofiles2, $fmprofiles1 );
    $extra = $return[0];

    foreach ($extra as $objects1) {
        if ( !($objects1->name == 'All Sources' || $objects1->group == 'Sources') ) {
            echo '<tr>';
            echo '<td><input type="checkbox" name="deletep[]" value="'. $objects1->id .'"></td>';
            echo '<td>'. $objects1->name .'</td>';
            echo '<td>'. $objects1->type .'</td>';
            echo '<td>'. $objects1->group .'</td>';
            echo '<td>'. $objects1->description .'</td>';
            echo '</tr>';
        }
    }

}

function all_profiles($profile1) {
    # get all profiles
    $fmprofiles1 = json_decode($profile1->getAllProfiles());
    foreach ($fmprofiles1 as $profile) {
        if ( !($profile->name == 'All Sources' || $profile->group == 'Sources' || $profile->type == 'shadow') ) {
            echo '<tr>';
            echo '<td><input type="checkbox" name="deletep[]" value="'. $profile->id .'"></td>';
            echo '<td>'. $profile->name .'</td>';
            echo '<td>'. (string)$profile->type .'</td>';
            echo '<td>'. $profile->group .'</td>';
            echo '<td>'. $profile->description .'</td>';
            echo '</tr>';
        }
    }
}

spl_autoload_register('my_autoloader');
# create connections to both collectors
//$profile2 = new Profiles($flowmon2['host'], $flowmon2['client_id'], $flowmon2['username'], $flowmon2['password']);
$profile1 = new Profiles($flowmon1['host'], $flowmon1['client_id'], $flowmon1['username'], $flowmon1['password']);

if ( isset($_GET['action']) ) {
    if ( $_GET['action'] == 'delete' ) {
        $to_be_delete = urlencode('["'. implode('","', $_POST['deletep']) .'"]');
    } elseif ($_GET['action'] == 'modify') {
        foreach ($_POST['deletep'] as $profile){
            $temp = json_decode($profile1->getProfile($profile));
            $temp->type = 'shadow';
            $changed = array('entity' => $temp);
            echo $profile1->changeProfile(json_encode($changed));
        }
    }
}

?>