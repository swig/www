
    <?php 
    // Include this to display news items. Set $rss_limit must contain a value 1-50.
    require_once('magpierss-0.72/rss_fetch.inc');
    ini_set("include_path", ".:./magpierss-0.72");

//    define('MAGPIE_CACHE_DIR', '/tmp/persistent/swig/magpie_cache');
    define('MAGPIE_CACHE_DIR', '/home/project-web/swig/magpie_cache');
    error_reporting(E_ERROR);

    // for debugging:
//    define('MAGPIE_DEBUG', 1);
//    error_reporting(E_ALL);

    // Fetch RSS feed 
//    $rss = fetch_rss('https://sourceforge.net/export/rss2_projnews.php?group_id=1645'); // Project news releases
//    $rss = fetch_rss('https://sourceforge.net/export/rss2_projnews.php?group_id=1645&rss_limit=' . $rss_limit . '&rss_fulltext=1'); // Project news releases (including full text of news items)
    $rss = fetch_rss('https://sourceforge.net/p/swig/news/feed?limit=' . $rss_limit); // Project news releases (including full text of news items)
//    echo '<pre>';
//    print_r($rss);
//    echo '</pre>';

    if ($rss) {
      // Show first 50 items
//      $items = array_slice($rss->items, 0, 50);
      $items = $rss->items;
      // Cycle through each item and echo  
      echo '<dl>';
      foreach ($items as $item) {
        $description = $item['description'];
        $publish_date = $item['pubdate'];

        // Check to see if the first 10 characters in the description are a date... when the old
        // news items were imported, the original publish date was put at the start of the description.
        if (substr($description, 10, 1) == ' ') {
          $possible_date = substr($description, 0, 10);
          // verify date is in expected format: yyyy/mm/dd
          if (substr($possible_date, 4, 1) == '/' && 
              substr($possible_date, 7, 1) == '/' &&
              is_numeric(substr($possible_date, 0, 4)) && 
              is_numeric(substr($possible_date, 5, 2)) &&
              is_numeric(substr($possible_date, 8, 2))) {
            $description = substr($description, 11);
            $publish_date = $possible_date;
          }
        }
        $formatted_date = date("Y/m/d", strtotime($publish_date));

        echo '<p><dt><b>'.$formatted_date.'</b> - <a href="'.$item['link'].'">'.$item['title'].'</a>'.'</dt><dd>'.$description.'</dd></dt></p>';
      }
      echo '</dl>';
    } else {
      echo '<h2>Error:</h2><p>'.magpie_error().'</p>';
    }
    // Restore original error reporting value
    @ini_restore('error_reporting');
    ?> 
