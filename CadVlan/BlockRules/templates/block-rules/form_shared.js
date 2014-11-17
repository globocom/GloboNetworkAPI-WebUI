/*
* Licensed to the Apache Software Foundation (ASF) under one or more
* contributor license agreements.  See the NOTICE file distributed with
* this work for additional information regarding copyright ownership.
* The ASF licenses this file to You under the Apache License, Version 2.0
* (the "License"); you may not use this file except in compliance with
* the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/
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