function bottom() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function(){};
	xhttp.open("PUT", "/api/bottom", true);
	xhttp.send();
}
