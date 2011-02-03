
(function($){
	$.fn.shoppingList = function(options) {

		// Options par defaut
		var defaults = {};

		var options = $.extend(defaults, options);

		this.each(function(){

			var obj = $(this);

			// Empêcher la sélection des éléments à la sourirs (meilleure gestion du drag & drop)
			//var _preventDefault = function(evt) { evt.preventDefault(); };
			//$("li").bind("dragstart", _preventDefault).bind("selectstart", _preventDefault);

			$("li").disableSelection();

			// Initialisation du composant "sortable"
			$(obj).sortable({
				axis: "y", // Le sortable ne s'applique que sur l'axe vertical
				containment: ".shoppingList", // Le drag ne peut sortir de l'élément qui contient la liste
//				handle: ".item", // Le drag ne peut se faire que sur l'élément .item (le texte)
				distance: 10, // Le drag ne commence qu'à partir de 10px de distance de l'élément
				// Evenement appelé lorsque l'élément est relaché
				stop: function(event, ui){
					// Pour chaque item de liste
					$(obj).find("li").each(function(){
						// On actualise sa position
						index = parseInt($(this).index()+1);
						// On la met à jour dans la page
						$(this).find(".count").text(index);
					});
				}
			});

			// On ajoute l'élément Poubelle à notre liste
			$(obj).after("<div class='trash'>Trash</div>");
			// On ajoute un petit formulaire pour ajouter des items
			$(obj).after("<div class='add'><input class='addValue' /> <input type='button' value='+' class='addBtn' /></div>");

			// Action de la poubelle
			// Initialisation du composant Droppable
			$(".trash").droppable({
				// Lorsque l'on relache un élément sur la poubelle
				drop: function(event, ui){
					// On retire la classe "hover" associée au div .trash
					$(this).removeClass("hover");
					// On ajoute la classe "deleted" au div .trash pour signifier que l'élément a bien été supprimé
					$(this).addClass("deleted");
					// On affiche un petit message "Cet élément a été supprimé" en récupérant la valeur textuelle de l'élément relaché
					$.ajax({
					    url: 'rm',
					    data: {id: ui.draggable.data('item')},
					});
					$(this).text(ui.draggable.find(".item").text()+" removed !");
					// On supprimer l'élément de la page, le setTimeout est un fix pour IE (http://dev.jqueryui.com/ticket/4088)
					setTimeout(function() { ui.draggable.remove(); }, 1);

					// On retourne à l'état originel de la poubelle après 2000 ms soit 2 secondes
					elt = $(this);
					setTimeout(function(){ elt.removeClass("deleted"); elt.text("Trash"); }, 2000);
				},
				// Lorsque l'on passe un élément au dessus de la poubelle
				over: function(event, ui){
					// On ajoute la classe "hover" au div .trash
					$(this).addClass("hover");
					// On cache l'élément déplacé
					ui.draggable.hide();
					// On indique via un petit message si l'on veut bien supprimer cet élément
					$(this).text("Remove "+ui.draggable.find(".item").text());
					// On change le curseur
					$(this).css("cursor", "pointer");
				},
				// Lorsque l'on quitte la poubelle
				out: function(event, ui){
					// On retire la classe "hover" au div .trash
					$(this).removeClass("hover");
					// On réaffiche l'élément déplacé
					ui.draggable.show();
					// On remet le texte par défaut
					$(this).text("Trash");
					// Ainsi que le curseur par défaut
					$(this).css("cursor", "normal");
				}
			})

			/*
			* Ajouter les controles sur le bouton "ajouter"
			*
			* @Return void
			*/

			// Bouton ajouter
			$(".addBtn").click(function(){
				// Si le texte n'est pas vide
				if($(".addValue").val() != "")
				{
				    var name=$(".addValue").val();
				    $.ajax({url:"add",
				        data: {text: name},
				        dataType: "text",
				        success: function(data, status, req) {
        					// On ajoute un nouvel item à notre liste
					        $(obj).append('<li>'+name+'</li>');
					        // On ajoute les contrôles à notre nouvel item
					        $(obj).find("li:last-child").data('item', data);
					        addControls($(obj).find("li:last-child"));
				        }
				    });
					// On réinitialise le champ de texte pour l'ajout
					$(".addValue").val("");
				}
			})
			// On autorise également la validation de la saisie d'un nouvel item par pression de la touche entrée
			$(".addValue").live("keyup", function(e) {
				if(e.keyCode == 13) {
					// On lance l'évènement click associé au bouton d'ajout d'item
					$(".addBtn").trigger("click");
				}
			});

			// Pour chaque élément trouvé dans la liste de départ
			$(obj).find("li").each(function(){
				// On ajoute les contrôles
				addControls($(this));
			});

		});

		/*
		* Fonction qui ajoute les contrôles aux items
		* @Paramètres
		*  - elt: élément courant (liste courante)
		*
		* @Return void
		*/

		function addControls(elt)
		{
            $(elt).disableSelection();
			// On ajoute en premier l'élément textuel
			$(elt).html("<span class='item'>"+$(elt).text()+"</span>");
			// Puis l'élément de position
			$(elt).prepend('<span class="count">'+parseInt($(elt).index()+1)+'</span>');
			// Puis l'élément d'action (élément acheté)
			$(elt).prepend('<span class="check unchecked"></span>');

			// Au clic sur cet élément
			$(elt).find(".check").click(function(){
				// On alterne la classe de l'item (le <li>), le CSS associé fera que l'élément sera barré
				$(this).parent().toggleClass("bought");

				// Si cet élément est acheté
				if($(this).parent().hasClass("bought"))
					// On modifie la classe en ajoutant la classe "checked"
					$(this).removeClass("unchecked").addClass("checked");
				// Le cas contraire
				else
					// On modifie la classe en retirant la classe "checked"
					$(this).removeClass("checked").addClass("unchecked");
			})

			// Au double clic sur le texte
			$(elt).find(".item").dblclick(function(){
				// On récupère sa valeur
				txt = $(this).text();
				// On ajoute un champ de saisie avec la valeur
				$(this).html("<input value='"+txt+"' />");
				// On la sélectionne par défaut
				$(this).find("input").select();
			})

			// Lorsque l'on quitte la zone de saisie du texte
			$(elt).find(".item input").live("blur", function(){
				// On récupère la valeur du champ de saisie
				txt = $(this).val();
				// On insère dans le <li> la nouvelle valeur textuelle
				$.ajax({
				url: 'edit',
				data: {id:$(this).parent().parent().data('item'), text:txt}
				});
				$(this).parent().html(txt);
			})

			// On autorise la même action lorsque l'on valide par la touche entrée
			$(elt).find(".item input").live("keyup", function(e) {
				if(e.keyCode == 13) {
					$(this).trigger("blur");
				}
			});
		}

		// On continue le chainage JQuery
		return this;
	};
})(jQuery);
