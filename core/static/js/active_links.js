if ( window.location.href == 'http://localhost:5000/posts/rubrics/' ) {
	var el = document.getElementById("rubrics");
	var newClass = el.getAttribute("class");
	newClass += " active"; 
	console.log(newClass)
	el.setAttribute("class", newClass);
} else if ( window.location.href == 'http://localhost:5000/posts/' ) {
	var el = document.getElementById("posts");
	var newClass = el.getAttribute("class");
	newClass += " active"; 
	el.setAttribute("class", newClass);
} else if ( window.location.href == 'http://localhost:5000/contacts/' ) {
	var el = document.getElementById("contacts");
	var newClass = el.getAttribute("class");
	newClass += " active"; 
	el.setAttribute("class", newClass);
}