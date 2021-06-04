// js code ref. -
// https://code.google.com/p/fbug/source/browse/branches/firebug1.7/content/firebug/lib.js?r=8828
// Next code was taken from Firebug project, credits to them
// Check license file - ../../licenses/firebug_license.txt

function getElementXPath(element) {
  if (element && element.id) return '//*[@id="' + element.id + '"]';
  else return getElementTreeXPath(element);
}

function getElementTreeXPath(element) {
  var paths = [];

  // Use nodeName (instead of localName) so namespace prefix is included (if any).
  for (; element && element.nodeType == 1; element = element.parentNode) {
    var index = 0;
    for (
      var sibling = element.previousSibling;
      sibling;
      sibling = sibling.previousSibling
    ) {
      // Ignore document type declaration.
      if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE) continue;

      if (sibling.nodeName == element.nodeName) ++index;
    }

    var tagName = element.nodeName.toLowerCase();
    var pathIndex = index ? "[" + (index + 1) + "]" : "";
    paths.splice(0, 0, tagName + pathIndex);
  }

  return paths.length ? "/" + paths.join("/") : null;
}
return getElementXPath(arguments[0]);
