var new_block;
$(document).ready(function() {
	
	new_block = '<div class="sorting">'+$(".sorting").html()+'</div>';
	
	$("#page_tab").tabs();
	
	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });
	
	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url environment.list %}";
	});
	
	$("#new_block").button({ icons: {primary: "ui-icon-plus"}, text: false })
	$("#remove_all_block").button({ icons: {primary: "ui-icon-trash"}, text: false })
	
	$("#remove_all_block").click(function(){
		if (confirm('Deseja realmente excluir todos os blocos?'))
			$("#sortable").html('');
	});
	
	 $("#sortable").sortable({
			update: function (e, ui) {
				update_order();
			}
	 });
	 
	 $("#new_block").click(function(){
		$("#sortable").append(new_block);
	 	$('textarea').last().val('');
		$('html, body').animate({
		    scrollTop: $("#btn_sav").show(1000).offset().top
		}, 500);
		update_order();
	 });
	 
	 $(".remove_block").live('click', function(){
		if(confirm("Deseja realmente excluir o bloco?")){
			$(this).parents('.sorting').remove();
			update_order();
		}
	 });
	
	function update_order(){
		$(".position").each(function(e){
			$(this).text(e+1 + '°');
		});
	}
});