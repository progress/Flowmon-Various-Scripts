<?php
# Class cover general Flowmon Profile operations

/**
 * This class provide comparsion method between 
 * @copyright Copyright 2019 Flowmon Networks - support@flowmon.com
 * @author Jiri Knapek - jiri.knapek@flowmon.com
 * @version 1.0
 */
class Profile
{
    protected $parametres = NULL;
    function __construct($parametres) {
        $this->parametres = $parametres;
    }
    
    /**
     * This function is to compate two profiles based on the entities expected to be unique
     * param array $first Information about all profiles we want to get compared
     * param array $second Profiles used for comparasion
     * return array $extra first - second
     * return array $match_full firtst = second
     * return array $match_i matched only on ID
     * return array $match_in matched on ID and name
     * return array $match_int matech on ID, name and type
     * return order ($extra, $match_full, $match_int, $match_in, $match_i)
     */
    public static function compare ($first, $second) {
        $match_full = array();
        $match_i = array();
        $match_in = array();
        $match_int = array();
        $extra = array();
        foreach ($first as $profile1) {
            foreach ($second as $profile2) {
                if ($profile1->id == $profile2->id) {
                    if ($profile1->name == $profile2->name) {
                        if ($profile1->type == $profile1->type) {
                            if ($profile1->group == $profile2->group) {
                                // ID, name, type and group match
                                array_push($match_full, $profile1);
                                break;
                            } else {
                                // non matching group
                                array_push($match_int, $profile1);
                                break;
                            }
                        } else {
                            // non matching type
                            array_push($match_in, $profile1);
                            break;
                        }
                    } else {
                        // not matching name
                        array_push($match_i, $profile1);
                        break;
                    }
                }
            }
            // No matches found, we found an extra profile
            array_push($extra, $profile1);
        }
        return array($extra, $match_full, $match_int, $match_in, $match_i);
    }
} // end public static function compare ($first, $second)
