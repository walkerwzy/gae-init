$ ->
	setTimeout ->
		$('input.gsc-search-button').on 'click',->
			$('#cse').width 500
			return
		$('#gsc-i-id1').on 'keyup',(e)->
			if e.which == 13
				$('#cse').width 500
			return
		$('div.gsc-clear-button').on 'click',->
			$("#cse").width 300
			return
		return
	,5000
	return
