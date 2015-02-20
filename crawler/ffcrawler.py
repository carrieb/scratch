from selenium import webdriver
import os
import time


artooscript = "(function(){var t={},e=!0;if('object'==typeof this.artoo&&(artoo.settings.reload||(artoo.log.verbose('artoo already exists within this page. No need to inject him again.'),artoo.loadSettings(t),artoo.exec(),e=!1)),e){var o=document.getElementsByTagName('body')[0];o||(o=document.createElement('body'),document.documentElement.appendChild(o));var a=document.createElement('script');console.log('artoo.js is loading...'),a.src='//medialab.github.io/artoo/public/dist/artoo-latest.min.js',a.type='text/javascript',a.id='artoo_injected_script',a.setAttribute('settings',JSON.stringify(t)),o.appendChild(a)}}).call(this);"
driver = webdriver.Chrome()
i = 1
LIMIT = 50;
while i < LIMIT:
    myscript = "(function(){var scraper = {iterator: '.z-list', data: { title: {sel:'a.stitle'}, url:{sel:'a.stitle', method:function($) {return 'http://www.fanfiction.net'+ $(this).attr('href'); }}, author: {sel:'a[href^=\"/u/\"]'}, summary:{sel:'.z-indent', method: function($) {return $(this).clone().children().remove().end().text();}}, meta:{sel:'.z-indent .xgray'}, update_ts:{sel:'.z-indent .xgray span:first-child', method: function($) {return $(this).data('xutime');}}, publish_ts:{sel: '.z-indent .xgray span:last-child', method: function($){return $(this).data('xutime');}}}}; var data = artoo.scrape(scraper); artoo.savePrettyJson(data, {filename:'final_fanfic_data_"+str(i)+".json'});})()" 
    page = "http://www.fanfiction.net/book/Harry-Potter/?&srt=4&lan=1&r=10&s=1&p=" + str(i)
    print "Fetching " + page
    driver.get(page)
    print "Executing artoo ..."
    driver.execute_script(artooscript)
    time.sleep(2)
    print "Executing our script ..."
    driver.execute_script(myscript)
    print driver.page_source
    print "Sucessful... (would run js script to get JSON & save here)"
    print "Sleeping..."
    i+=1
    time.sleep(1)
    print "Woke up!"
driver.quit()
    
