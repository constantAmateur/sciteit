(function() {
var write_string="<iframe src=\"http://www.sciteit.com/static/button/button3.html?width=69&url=";
  if (window.sciteit_url)  { 
      write_string += encodeURIComponent(sciteit_url); 
  }
  else { 
      write_string += encodeURIComponent(window.location.href);
  }
  if (window.sciteit_title) {
       write_string += '&title=' + encodeURIComponent(window.sciteit_title);
  }
  if (window.sciteit_target) {
       write_string += '&sr=' + encodeURIComponent(window.sciteit_target);
  }
  if (window.sciteit_css) {
      write_string += '&css=' + encodeURIComponent(window.sciteit_css);
  }
  if (window.sciteit_bgcolor) {
      write_string += '&bgcolor=' + encodeURIComponent(window.sciteit_bgcolor); 
  }
  if (window.sciteit_bordercolor) {
      write_string += '&bordercolor=' + encodeURIComponent(window.sciteit_bordercolor); 
  }
  if (window.sciteit_newwindow) { 
      write_string += '&newwindow=' + encodeURIComponent(window.sciteit_newwindow);}
  write_string += "\" height=\"52\" width=\"69\" scrolling='no' frameborder='0'></iframe>";
  document.write(write_string);
})()
