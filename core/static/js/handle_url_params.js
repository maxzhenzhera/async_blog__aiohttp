function addUrlParameter(name, value) {
	var searchParams = new URLSearchParams(window.location.search)
	searchParams.set(name, value)
	window.location.search = searchParams.toString()
}


function deleteUrlParameter(name) {
	var searchParams = new URLSearchParams(window.location.search)
	searchParams.delete(name)
	window.location.search = searchParams.toString()
}