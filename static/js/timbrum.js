function notifyMe( mustShow, tag ) {
	
	if (!Notification) {
		alert('Che cavolo di browser preistorico usi?!?! Scarica l\'ultima versione di Chrome, Firefox o Opera!');
		return;
	}
	
	if (Notification.permission !== "granted")
		Notification.requestPermission();
	
	if ( mustShow ) {
		var notification = new Notification(
				'Complimenti!!!',
				{
					tag: "timbrumNotification",
					icon : 'http://www.cineca.it/sites/default/files/ISCRA.png',
					body : "Anche oggi hai portato la pagnotta a casa. Ma ora la domanda sorge spontanea ... che ci fai ancora su quella sedia???"
				});
	}
}

