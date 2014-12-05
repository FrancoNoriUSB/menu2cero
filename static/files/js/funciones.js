/* Javascript Code */

/*Funcion para pintar de gris imagenes*/
function gris(id, source) {
    var canvas = document.getElementById(id);
    var context = canvas.getContext("2d");
    var image = document.getElementById(source);
    context.drawImage(image, 0, 0);

	var imgd = context.getImageData(0, 0, 500, 300);
	var pix = imgd.data;
	for (var i = 0, n = pix.length; i < n; i += 4) {
		var grayscale = pix[i  ] * .3 + pix[i+1] * .59 + pix[i+2] * .11;
		pix[i  ] = grayscale; 	// red
		pix[i+1] = grayscale; 	// green
		pix[i+2] = grayscale; 	// blue
		// alpha
	}
	context.putImageData(imgd, 0, 0);
};

/*Funcion para obtener las zonas de una ciudad*/
function get_zona_ciudad(){
	new Ajax.Request('/ciudad/ajax_purpose_staff/', {
		method: 'post',
		parameters: $H({'type': $('id_Ciudad').getValue()}),
		onSuccess: function(busqueda){
			var e = $('id_Zona');
			if(busqueda.responseText){
				e.update(transport.responseText);
			}
		}
	});
}