$("#btnpreview").on "click", ->
	($ '#preview .modal-body')
		.html marked ($ '#txtcontent').val()